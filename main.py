import base64
import csv
import json
import os
import requests
from dotenv import load_dotenv
# Loading .env info about SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI

load_dotenv()

# initialising authentication data for Spotify API and Last.fm API
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
LAST_FM_API_KEY = os.getenv("LAST_FM_API_KEY")
# initialising a lot of times used variables
search_url = "https://api.spotify.com/v1/search"


def get_top_artists():
    url = "https://ws.audioscrobbler.com/2.0"
    params = {
        'method': 'geo.getTopArtists',
        "country": "NETHERLANDS",
        "api_key": LAST_FM_API_KEY,
        'format': 'json'
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to get top artists: {response.status_code}, {response.text}")
        return []

    data = response.json()
    top_artists = data.get('topartists', {}).get('artist', [])
    return [artist['name'] for artist in top_artists]


# requesting token from spotify account service
def get_token():
    # encoding SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET into base64 format
    auth_string = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    # converting auth_bytes into string base64 format
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # initialising url, data, headers for spotify account service
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_request = requests.post(url, data=data, headers=headers)
    # obtaining spotify access token from spotify account service (not spotify web api)
    if token_request.status_code == 200:
        token_response_data = json.loads(token_request.content)
        access_token = token_response_data["access_token"]
        return access_token
    # printing status code if token obtaining failed
    else:
        print("Failed to obtain access token")
        print(token_request.status_code)
        print(token_request.text)
        return None


# obtaining authentication headers for upcoming functions
def get_auth_header():
    token = get_token()
    return {"Authorization": f"Bearer {token}"}


# obtaining artist id
def get_artist_id(artist_name):
    auth_header = get_auth_header()
    params = {
        'q': artist_name,
        'type': 'artist',
        'limit': 1
    }
    response = requests.get(search_url, headers=auth_header, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to search artist: {response.status_code}, {response.text}")
    search_results = response.json()
    if search_results['artists']['items']:
        return search_results['artists']['items'][0]['id']
    else:
        raise Exception("Artist not found")


# obtaining artist genres
def get_artist_genres(artist_id):
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    auth_header = get_auth_header()
    response = requests.get(artist_url, headers=auth_header)
    if response.status_code != 200:
        raise Exception(f"Failed to get artist genres: {response.status_code}, {response.text}")
    return response.json()['genres']


# obtaining artist top tracks
def get_artist_top_tracks(artist_id):
    tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    auth_header = get_auth_header()
    params = {
        "market": None,
    }
    response = requests.get(tracks_url, headers=auth_header, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get artist tracks: {response.status_code}, {response.text}")
    tracks_info = response.json()
    return [track["name"] for track in tracks_info.get("tracks", [])]


# obtaining artist albums (function for future development / functie voor de doorontwikkeling)
def get_artist_albums(artist_id):
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    auth_header = get_auth_header()
    params = {
        "include_groups": "album"
    }
    response = requests.get(albums_url, headers=auth_header, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get artist albums: {response.status_code}, {response.text}")
    data = response.json()
    return [album["name"] for album in data.get("items", [])]


# exporting top tracks as csv file
def export_to_csv(data, filename):
    with open(f"{filename}.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Track Name"])
        for item in data:
            writer.writerow([item])


# exporting top tracks as txt file
def export_to_text(data, filename):
    with open(f"{filename}.txt", mode='w') as file:
        file.write("Track Name\n")
        for item in data:
            file.write(f"{item}\n")


# creating an interactive menu for an intuitive user experience
def interactive_menu():
    artist_name = None
    while True:
        print("Menu:")
        print("1. Get top 10 artists on last.fm in the Netherlands")
        print("2. Get artist genres")
        print("3. Get artist recent top tracks")
        print("4. Export top tracks data to .CSV file")
        print("5. Export top tracks data to .txt file")
        print("6. Exit")
        choice = input("Your choice: ")

        if choice == '1':
            try:
                i = 1
                top = get_top_artists()[:10]
                print("Top artists:")
                for top in top:
                    print(f"{i}) {top}")
                    i += 1
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '2':
            artist_name = input("Type in artist name: ")
            try:
                artist_id = get_artist_id(artist_name)
                genres = get_artist_genres(artist_id)
                print(f"{artist_name} genres: {', '.join(genres)}")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '3':
            artist_name = input("Type in artist name: ")
            try:
                artist_id = get_artist_id(artist_name)
                tracks = get_artist_top_tracks(artist_id)
                print(f"{artist_name} recent top 10 tracks:")
                i = 1
                for track in tracks:
                    print(f"{i}) {track}")
                    i += 1
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '4' and artist_name is not None:
            try:
                artist_id = get_artist_id(artist_name)
                tracks = get_artist_top_tracks(artist_id)
                filename = input("Type in name of csv file: ")
                export_to_csv(tracks, filename)
                print(f"Recent top tracks exported to: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '4' and artist_name is None:
            try:
                artist_name = input("Type in artist name: ")
                artist_id = get_artist_id(artist_name)
                tracks = get_artist_top_tracks(artist_id)
                filename = input("Type in name of csv file: ")
                export_to_csv(tracks, filename)
                print(f"Recent top tracks exported to: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '5' and artist_name is not None:
            try:
                artist_id = get_artist_id(artist_name)
                tracks = get_artist_top_tracks(artist_id)
                filename = input("Type in name of txt file: ")
                export_to_text(tracks, filename)
                print(f"Recent top tracks exported to: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '5' and artist_name is None:
            try:
                artist_name = input("Type in artist name: ")
                artist_id = get_artist_id(artist_name)
                tracks = get_artist_top_tracks(artist_id)
                filename = input("Type in name of txt file: ")
                export_to_text(tracks, filename)
                print(f"Recent top tracks exported to: {filename}")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif choice == '6':
            print("**************************************************")
            print("*                                                *")
            print("*              Exiting Application               *")
            print("*                                                *")
            print("**************************************************")
            break

        else:
            print("Invalid input, try again.")


# running the application
if __name__ == "__main__":
    interactive_menu()
