<div align="center">
  <img src="https://github.com/user-attachments/assets/38e0d35d-e169-4a9a-a288-19f61282ff58" alt="Barcelona Logo" width="200"/>
  <h1>FC Barcelona Reports</h1>
</div>



## Overview

This project provides a web application for analyzing and visualizing FC Barcelona's match data. The application is built with Streamlit, scrapes match data from WhoScored, processes and stores it in MongoDB, and displays it in a streamlined dashboard.

## Features

- **Data Scraping**: Scrapes FC Barcelona's match data from WhoScored.
- **MongoDB Storage**: Stores all match, team, player, and event data in MongoDB.
- **Data Visualization**: Interactive visualizations including:
  - Pass networks
  - Shot maps
  - Match momentum
  - Team statistics
  - Player Statistics: Detailed stats for each player, including goals, assists, pass accuracy, and more.
  - Competition Summary: Summary statistics for each competition, such as total matches played, wins, goals scored, and key performance metrics.

- **Streamlit Interface**: Simple and interactive web dashboard for viewing and analyzing match data.

## Prerequisites

- Python 3.7+
- MongoDB instance
- Chrome WebDriver (for Selenium)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MahmoudNamNam/FC-Barcelona-Reports
   cd FC-Barcelona-Reports
   ```

2. **Set up environment variables:**
   - Create a `.env` file in the project root and add your MongoDB URI:

     ```py
     MONGO_URI="your_mongodb_connection_string"
     ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Data Scraping

To scrape data and add it to your MongoDB, run:

```bash
python scraper.py
```

- This script only scrapes new matches not already in the database.

### 2. Start the Streamlit App

To launch the dashboard, run:

```bash
streamlit run dashboard.py
```

- Access the dashboard at [http://localhost:8501](http://localhost:8501).

## Project Structure

- **`scraper.py`**: Web scraping script that fetches match data from WhoScored.
- **`data_loader.py`**: Loads data from MongoDB into DataFrames.
- **`dashboard.py`**: Streamlit app for displaying match data.
- **`visualizations.py`**: Functions for visualizations used in the app.
- **`utilities.py`**: Helper functions and utilities for data processing and analysis.
- **`config.toml`**: Configuration for Streamlit app styling.
- **`.env`**: Environment variables.

## Requirements

Dependencies listed in `requirements.txt`:

- pandas
- numpy
- selenium
- pymongo
- beautifulsoup4
- streamlit
- mplsoccer
- matplotlib
- python-dotenv

## Notes

- **Environment Variables**: Ensure `.env` is added to `.gitignore` to keep credentials secure.
- **Chrome WebDriver**: Ensure compatibility with your Chrome version. You may need to update the `webdriver.Chrome()` configuration in `scraper.py` based on your setup.

## Future Enhancements

- Add support for other teams or leagues.
- Include more advanced visualizations and analytics.
- Enable user authentication to save and share custom reports.

---
**Contributions and Feedback**
Contributions are welcome! Feel free to open an issue or submit a pull request. For feedback, contact.
