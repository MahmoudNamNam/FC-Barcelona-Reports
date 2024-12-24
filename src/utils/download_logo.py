from dotenv import load_dotenv
import requests
import logging
import os

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv(dotenv_path='./../config.env')


def download_logo(team_name, url, save_dir=os.getenv('LOGO_DIR')):
    """
    Download and save a team's logo from the given URL.

    Args:
        team_name (str): The name of the team.
        url (str): URL to the logo image.
        save_dir (str): Directory to save the logo. Default is 'team_logos'.

    Returns:
        str: Path to the saved logo file or error message if download fails.
    """
    try:
        # Format the filename
        formatted_name = team_name.lower().replace(" ", "_")
        file_name = f"{formatted_name}_logo.png"
        file_path = os.path.join(save_dir, file_name)

        # Create directory if not exists
        os.makedirs(save_dir, exist_ok=True)
        
        # Download the logo
        logger.info(f"Downloading logo for {team_name} from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the logo
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        logger.info(f"Logo saved at {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download logo for {team_name}: {e}")
        return f"Error: {e}"
