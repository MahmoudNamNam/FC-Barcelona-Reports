from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os
import streamlit as st
import logging
from utilities import *

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='config.env')

def load_data_from_mongo():
    try:
        # Load secrets from Streamlit secrets or environment variables
        MONGO_URI = (
            f"mongodb+srv://{os.getenv('DB_USERNAME', st.secrets.get('mongo', {}).get('DB_USERNAME'))}:"
            f"{os.getenv('DB_PASSWORD', st.secrets.get('mongo', {}).get('DB_PASSWORD'))}@"
            f"{os.getenv('DB_CLUSTER', st.secrets.get('mongo', {}).get('DB_CLUSTER'))}.mongodb.net/"
            f"{os.getenv('DB_NAME', st.secrets.get('mongo', {}).get('DB_NAME'))}?retryWrites=true&w=majority"
        )
        
        logger.info("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[os.getenv('DB_NAME')]
        
        logger.info("Fetching data from collections...")
        matches_data = list(db.matches.find())
        teams_data = list(db.teams.find())
        players_data = list(db.players.find())
        events_data = list(db.events.find())
        
        logger.info("Data fetched successfully. Closing connection.")
        client.close()

        return matches_data, teams_data, players_data, events_data
    except Exception as e:
        logger.error(f"Error loading data from MongoDB: {e}")
        return None, None, None, None
