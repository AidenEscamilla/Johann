import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from songs import Songs # my class file


# Works for whoever's logged into the browsers spotify
def create_oath_token(database_client):
  scopes = [
    "user-library-read",
    "playlist-read-private",
    "playlist-modify-public",
    "ugc-image-upload"
    ]

  # Authenticate with Spotify
  sp_oauth = SpotifyOAuth(scope=",".join(scopes))

  # Get the access token
  access_token = sp_oauth.get_access_token(as_dict=False)

  # Use the access token to create a Spotify client
  sp = spotipy.Spotify(auth=access_token, requests_timeout=15, retries=5)

  # Insert the user
  spotify_user = sp.me()
  user_id = spotify_user['id']
  user_display_name = spotify_user['display_name']
  database_client.insert_user(user_id, user_display_name)

  # Insert the oath token
  formatted_token = sp_oauth.get_cached_token()
  formatted_token['user_id'] = user_id
  database_client.insert_oath_token(formatted_token)

  return {'client': sp, 'oath': sp_oauth}

# Function to refresh the access token
def refresh_access_token(spotify_oath, oath_token):
    token_info = spotify_oath.refresh_access_token(oath_token['refresh_token'])
    return token_info

def refresh_user_oath_token(db_client, spotify_client, spotify_oath):
  oath_token = db_client.get_oath_token(spotify_client._auth)

  # Check if the token is expired and refresh it if needed
  if spotify_oath.is_token_expired(oath_token):
    token_info = refresh_access_token(spotify_oath, oath_token)
    new_access_token = token_info['access_token']
    spotify_client = spotipy.Spotify(auth=new_access_token)
    # Get the user
    spotify_user = spotify_client.me()
    user_id = spotify_user['id']

    # Insert the oath token
    formatted_token = token_info
    formatted_token['user_id'] = user_id
    db_client.insert_oath_token(formatted_token)

  return spotify_client

def get_fresh_spotify_client(db_client):
  sp_objects = create_oath_token(db_client)
  sp_client = sp_objects['client']
  sp_oath = sp_objects['oath']

  fresh_client = refresh_user_oath_token(db_client, sp_client, sp_oath)

  return fresh_client

def main():
  db_client = Songs()

  new_client = get_fresh_spotify_client(db_client)

  print(new_client)


if __name__ == "__main__":
  main()


