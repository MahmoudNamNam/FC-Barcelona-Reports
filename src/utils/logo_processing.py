import logging
from PIL import Image
import base64
from io import BytesIO
import os
from dotenv import load_dotenv

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path='./../config.env')

# Get logo directory from environment variable
LOGO_DIR = os.getenv("LOGO_DIR")

# Custom exception for missing logo files
class LogoNotFoundError(Exception):
    pass

# Format team name for file naming
def format_team_name(name):
    """
    Formats the team name to a lowercase, underscore-separated format.

    Args:
        name (str): The name of the team.

    Returns:
        str: Formatted team name.
    """
    logger.info(f"Formatting team name: {name}")
    return name.lower().replace(" ", "_")

# Load, resize, and encode the logo
def load_and_resize_logo(team_name, box_size=(150, 150)):
    """
    Loads a team's logo, crops and resizes it, and encodes it to Base64.

    Args:
        team_name (str): The name of the team.
        box_size (tuple): The desired size of the logo (default is 150x150).

    Returns:
        str: Base64-encoded string of the processed logo, or an error message if something goes wrong.
    """
    try:
        logger.info(f"Loading logo for team: {team_name}")
        logo_path = f"{LOGO_DIR}\\{format_team_name(team_name)}_logo.png"

        if not os.path.exists(logo_path):
            raise LogoNotFoundError(f"Logo not found at {logo_path}")

        logo = Image.open(logo_path).convert("RGBA")
        bbox = logo.getbbox()  # Crop transparent edges if present
        if bbox:
            logo = logo.crop(bbox)

        logo.thumbnail(box_size, Image.LANCZOS)  # Resize logo
        logger.info(f"Resized logo to {box_size}.")

        # Encode the resized logo to Base64
        buffered = BytesIO()
        logo.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    except LogoNotFoundError as e:
        logger.error(e)
        return str(e)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {e}"
