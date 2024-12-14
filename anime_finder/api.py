import requests
from io import BytesIO
from PIL import Image
import time

def fetch_genres():
    url = "https://graphql.anilist.co"
    query = """
    query {
      GenreCollection
    }
    """
    try:
        response = requests.post(url, json={"query": query}, timeout=10)
        time.sleep(1.1)  # Throttle the requests
        if response.status_code == 200:
            genres = response.json().get("data", {}).get("GenreCollection", [])
            return [genre for genre in genres if genre.lower() != "hentai"]
        else:
            print(f"Error fetching genres: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return []

def fetch_anime(genres):
    url = "https://graphql.anilist.co"
    query = """
    query ($genres: [String]) {
      Page(page: 1, perPage: 10) {
        media(genre_in: $genres, type: ANIME, sort: POPULARITY_DESC) {
          title {
            romaji
            english
          }
          coverImage {
            medium
          }
          description
          genres
        }
      }
    }
    """
    variables = {"genres": genres}
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
        time.sleep(1.1)  # Throttle the requests
        if response.status_code == 200:
            return response.json().get("data", {}).get("Page", {}).get("media", [])
        else:
            print(f"Error fetching anime: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return []

def fetch_popular_anime_for_genre(genre):
    url = "https://graphql.anilist.co"
    query = """
    query ($genre: String) {
      Page(page: 1, perPage: 1) {
        media(genre_in: [$genre], type: ANIME, sort: POPULARITY_DESC) {
          title {
            romaji
            english
          }
          coverImage {
            medium
          }
        }
      }
    }
    """
    variables = {"genre": genre}
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
        time.sleep(1.1)  # Throttle the requests
        if response.status_code == 200:
            media = response.json().get("data", {}).get("Page", {}).get("media", [])
            return media[0] if media else None
        else:
            print(f"Error fetching anime for genre {genre}: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Network error for genre {genre}: {e}")
        return None

