# Spotify Get Artist

## Description

This project demonstrates how to use API requests, process JSON data, and provide users with accurate information. Additionally, it allows users to fetch the top 10 tracks of an artist (recently) and export this data to a .csv or .txt file. It also retrieves the top artists in the Netherlands according to Last.fm.

## Installation

Follow these steps to install the project:

```bash
# Clone the repository
git clone https://github.com/Yockium/spotify-command-line-app.git

# Navigate to the project directory
cd spotify-command-line-app

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Before running the project, you need to create a .env file in the root directory of the project with your API keys. Register at Spotify and Last.fm to obtain your API keys, and then create the .env file as follows:
```.env
SPOTIPY_CLIENT_ID=yourSpotipyClientId
SPOTIPY_CLIENT_SECRET=yourSpotipyClientSecret
LAST_FM_API_KEY=yourLastFmApiKey
```
