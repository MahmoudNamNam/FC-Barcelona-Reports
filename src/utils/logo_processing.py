import logging
from PIL import Image
import base64
from io import BytesIO
import os

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOGO_DIR = os.getenv("LOGO_DIR", "team_logos")  # Use env var for flexibility

class LogoNotFoundError(Exception):
    pass

def format_team_name(name):
    logger.info(f"Formatting team name: {name}")
    formatted_name = name.lower().replace(" ", "_")
    return formatted_name

def load_and_resize_logo(team_name, box_size=(150, 150)):
    try:
        logger.info(f"Loading logo for team: {team_name}")
        logo_path = f"{LOGO_DIR}/{format_team_name(team_name)}_logo.png"
        
        if not os.path.exists(logo_path):
            raise LogoNotFoundError(f"Logo not found at {logo_path}")

        logo = Image.open(logo_path).convert("RGBA")

        bbox = logo.getbbox()
        if bbox:
            logo = logo.crop(bbox)

        logo.thumbnail(box_size, Image.LANCZOS)
        logger.info(f"Resized logo to {box_size}.")

        buffered = BytesIO()
        logo.save(buffered, format="PNG")
        encoded_logo = base64.b64encode(buffered.getvalue()).decode('utf-8')

        logger.info(f"Logo processing complete for {team_name}.")
        return encoded_logo

    except LogoNotFoundError as e:
        logger.error(e)
        return str(e)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {e}"
