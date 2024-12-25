from datetime import datetime
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
from utils.download_logo import download_logo

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
            'date': datetime.strptime(matchdict.get('startTime'), "%Y-%m-%dT%H:%M:%S"),
            'home_team_id': matchdict['home']['teamId'],
            'away_team_id': matchdict['away']['teamId'],
            'home_team_name': matchdict['home']['name'],
            'away_team_name': matchdict['away']['name'],
            'home_score_fulltime': matchdict['home']['scores'].get('fulltime', 0),
            'away_score_fulltime': matchdict['away']['scores'].get('fulltime', 0),
            'home_shots_total': sum_stats(matchdict['home']['stats'].get('shotsTotal', {})),
            'home_shots_on_target': sum_stats(matchdict['home']['stats'].get('shotsOnTarget', {})),
            'home_possession': sum_stats(matchdict['home']['stats'].get('possession', {})),
            'home_passes_total': sum_stats(matchdict['home']['stats'].get('passesTotal', {})),
            'home_pass_completion': sum_stats(matchdict['home']['stats'].get('passesAccurate', 0)),
            'home_fouls_committed': sum_stats(matchdict['home']['stats'].get('foulsCommited', {})),
            'home_corners': sum_stats(matchdict['home']['stats'].get('cornersTotal', {})),
            'home_offsides_caught': sum_stats(matchdict['home']['stats'].get('offsidesCaught', {})),
            'away_shots_total': sum_stats(matchdict['away']['stats'].get('shotsTotal', {})),
            'away_shots_on_target': sum_stats(matchdict['away']['stats'].get('shotsOnTarget', {})),
            'away_possession': sum_stats(matchdict['away']['stats'].get('possession', {})),
            'away_passes_total': sum_stats(matchdict['away']['stats'].get('passesTotal', {})),
            'away_pass_completion': sum_stats(matchdict['away']['stats'].get('passesAccurate', 0)),
            'away_fouls_committed': sum_stats(matchdict['away']['stats'].get('foulsCommited', {})),
            'away_corners': sum_stats(matchdict['away']['stats'].get('cornersTotal', {})),
            'away_offsides_caught': sum_stats(matchdict['away']['stats'].get('offsidesCaught', {}))
        }

        teams_data = []
        for side in ['home', 'away']:
            team = matchdict[side]
            teams_data.append({
                '_id': team['teamId'],
                'name': team['name'],
                'country_name': team['countryName'],
                'manager_name': team.get('managerName', 'Unknown'),
                'competition': competition
            })

        players_data = []
        for side in ['home', 'away']:
            team = matchdict[side]
            for player in team['players']:
                players_data.append({
                    '_id': f"{player['playerId']}_{match_id}",
                    'player_id': player['playerId'],
                    'name': player['name'],
                    'shirt_no': player['shirtNo'],
                    'position': player['position'],
                    'age': player.get('age', 'Unknown'),
                    'team_id': team['teamId'],
                    'stats': player.get('stats', {}),
                    'competition': competition,
                    'match_id': match_id
                })

        events_data = []
        for event in matchdict.get('events', []):
            events_data.append({
                '_id': f"{match_id}_{event.get('eventId', '')}",
                'match_id': match_id,
                'type': event.get('type', {}).get('displayName'),
                'minute': event.get('minute'),
                'team_id': event.get('teamId'),
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
                    # Add logo URL and download logo
                    logo_url = f"https://d2zywfiolv4f83.cloudfront.net/img/teams/{team['_id']}.png"
                    result = download_logo(team['name'], logo_url)
                    if result:
                        log.info(f"Logo for team {team['name']} downloaded successfully.")
                    else:
                        log.warning(f"Failed to download logo for team {team['name']}.")

                    # Update team data in the database
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
