import json
import time
import re
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Load environment variables
load_dotenv(dotenv_path='config.env')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Database configuration
MONGO_URI = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}.mongodb.net/{os.getenv('DB_NAME')}?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
DB_NAME = os.getenv('DB_NAME')
INTERVAL_SECONDS = 2  # Delay between requests
BASE_URL = 'https://www.whoscored.com/Teams/65/Fixtures/Spain-Barcelona'


def initialize_driver():
    """Initialize the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="Live"]')))
    return driver


def extract_match_urls(driver):
    """Extract match URLs for different competitions."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_urls = soup.select('a[href*="\/Live\/"]')
    all_urls = list(set(['https://www.whoscored.com' + x.attrs['href'] for x in all_urls]))
    laliga_urls = [url for url in all_urls if 'LaLiga' in url]
    champions_league_urls = [url for url in all_urls if 'Champions-League' in url]
    supercopa_urls = [url for url in all_urls if 'Spain-Supercopa-de-Espana' in url]

    return laliga_urls, champions_league_urls, supercopa_urls


def sum_stats(stats_dict, exclude_keys=None):
    """Sum stats from a dictionary, excluding specified keys."""
    exclude_keys = exclude_keys or []
    return sum(value for key, value in stats_dict.items() if key not in exclude_keys)


def get_existing_match_ids(db):
    """Retrieve existing match IDs from the database."""
    return set(item['_id'] for item in db.matches.find({}, {'_id': 1}))


def scrape_match_data(driver, match_id, url, competition):
    """Scrape data for a single match."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//script[contains(text(), 'matchCentreData')]"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find and parse the matchCentreData script tag
        element = soup.find('script', text=lambda t: 'matchCentreData' in t if t else False)
        if not element:
            log.warning(f"MatchCentreData not found for URL: {url}")
            return None, [], [], []

        # Extract JSON data
        matchdict = json.loads(element.text.split("matchCentreData: ")[1].split(',\n')[0])

        match_info = {
            '_id': match_id,
            'competition': competition,
            'date': matchdict.get('startTime'),
            'home_team_id': matchdict['home']['teamId'],
            'away_team_id': matchdict['away']['teamId'],
            'home_team_name': matchdict['home']['name'],
            'away_team_name': matchdict['away']['name'],
            'home_score_fulltime': matchdict['home']['scores'].get('fulltime', 0),
            'away_score_fulltime': matchdict['away']['scores'].get('fulltime', 0),
            'home_shots_total': sum_stats(matchdict['home']['stats'].get('shotsTotal', {})),
            'away_shots_total': sum_stats(matchdict['away']['stats'].get('shotsTotal', {})),
        }

        teams_data = [{
            '_id': matchdict['home']['teamId'],
            'name': matchdict['home']['name'],
            'country_name': matchdict['home']['countryName'],
            'competition': competition
        }, {
            '_id': matchdict['away']['teamId'],
            'name': matchdict['away']['name'],
            'country_name': matchdict['away']['countryName'],
            'competition': competition
        }]

        players_data = []
        for side in ['home', 'away']:
            team = matchdict[side]
            for player in team['players']:
                players_data.append({
                    '_id': f"{player['playerId']}_{match_id}",
                    'player_id': player['playerId'],
                    'name': player['name'],
                    'team_id': team['teamId'],
                    'competition': competition,
                    'match_id': match_id
                })

        events_data = []
        for event in matchdict.get('events', []):
            events_data.append({
                '_id': f"{match_id}_{event.get('eventId', '')}",
                'match_id': match_id,
                'type': event.get('type', {}).get('displayName'),
                'minute': event.get('minute')
            })

        return match_info, teams_data, players_data, events_data

    except Exception as e:
        log.error(f"Error scraping match {match_id} at {url}: {e}")
        return None, [], [], []


def main():
    # MongoDB setup
    db = client[DB_NAME]
    existing_match_ids = get_existing_match_ids(db)

    # Initialize WebDriver
    driver = initialize_driver()
    laliga_urls, champions_league_urls, supercopa_urls = extract_match_urls(driver)

    # Scrape and insert data
    for competition, urls in [("La Liga", laliga_urls), ("Champions League", champions_league_urls), ("Supercopa", supercopa_urls)]:
        for url in urls:
            match_id = int(re.search(r"Matches/(\d+)/", url).group(1))
            if match_id in existing_match_ids:
                log.info(f"Match {match_id} already exists. Skipping...")
                continue

            log.info(f"Scraping new match: {match_id} ({competition})")
            match_info, teams_data, players_data, events_data = scrape_match_data(driver, match_id, url, competition)

            if match_info:
                db.matches.update_one({'_id': match_info['_id']}, {'$set': match_info}, upsert=True)
            if teams_data:
                for team in teams_data:
                    db.teams.update_one({'_id': team['_id']}, {'$set': team}, upsert=True)
            if players_data:
                for player in players_data:
                    db.players.update_one({'_id': player['_id']}, {'$set': player}, upsert=True)
            if events_data:
                for event in events_data:
                    db.events.update_one({'_id': event['_id']}, {'$set': event}, upsert=True)

            time.sleep(INTERVAL_SECONDS)

    log.info("Scraping completed successfully.")
    driver.quit()
    client.close()


if __name__ == "__main__":
    main()
