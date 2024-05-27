import inspect
import os
from termcolor import colored
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

import spot_oath
from spot_oath import create_oath_token, refresh_access_token, get_fresh_spotify_client
import webcrawl_lyrics
import embeddings
import mapping
import make_cluster_playlists
import recommendation
from songs import MockSongs

def assert_equals(expected, actual):
    return expected == actual
        

def assert_not_equals(expected, actual):
    return not expected == actual
        

def pass_test():
    print(inspect.stack()[1][3] + colored(' - pass', 'green'))

def fail_test():
    print(inspect.stack()[1][3] + colored(' - fail', 'red'))

def test_assert_equals():
    if assert_equals(1,1):
        pass_test()
    else:
        fail_test()
def test_assert_not_equals():
    if assert_not_equals(1, 0):
        pass_test()
    else:
        fail_test()


# spot_oath tests

def test_valid_spotify_env_credentials():
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"  #this will open a browser page, follow terminal instructions
    scopes = [
    "user-library-read",
    "playlist-read-private",
    "playlist-modify-public",
    "ugc-image-upload"
    ]

    actual = sp.Spotify(auth_manager=SpotifyOAuth(
        client_id = os.environ["SPOTIPY_CLIENT_ID"],
        client_secret = os.environ["SPOTIPY_CLIENT_SECRET"],
        scope=scopes
    ))
    try:
        actual.current_user()
    except sp.oauth2.SpotifyOauthError as e:
        actual = None
        pass #invalid credentials

    if assert_not_equals(None, actual):
        pass_test()
    else:
        fail_test()

def test_invalid_spotify_env_credentials():
    # Commented out to save time testing. 
    # This test will fail after a proper auth token is cached unless you delete the .cache
    # if os.path.exists('.cache'):
    #    os.remove('.cache')
    
    invalid_client_id = "publicBad"
    invalid_client_secret = "secretBad"
    scopes = [
    "user-library-read",
    "playlist-read-private",
    "playlist-modify-public",
    "ugc-image-upload"
    ]

    actual = None
    try:
        actual = sp.Spotify(auth_manager=SpotifyOAuth(
        client_id = invalid_client_id,
        client_secret = invalid_client_secret,
        scope = scopes
        ))
        actual.current_user()
    except sp.oauth2.SpotifyOauthError as e:
        print('Correctly errors out with bad credentials: ', e)
        actual = -1
    
    if assert_equals(actual, -1):
        pass_test()
    else:
        fail_test()

def test_create_oath_token():
    song_db = MockSongs()
    actual = create_oath_token(song_db)
    if isinstance(actual['client'], sp.client.Spotify) and isinstance(actual['oath'], sp.oauth2.SpotifyOAuth):
        pass_test()
    else:
        fail_test()

def test_refresh_returns_new_token():
    spot_client = sp.Spotify(auth_manager=SpotifyOAuth())
    old_token = spot_client.auth_manager.get_cached_token()['access_token']
    actual = refresh_access_token(spot_client.auth_manager, spot_client.auth_manager.get_cached_token())['access_token']
    
    if assert_not_equals(old_token, actual):
        pass_test()
    else:
        fail_test()

def test_spot_token_is_expired():
    spot_client = sp.Spotify(auth_manager=SpotifyOAuth())
    token = spot_client.auth_manager.get_cached_token()
    expire_one_second_ago = token['expires_at'] - token['expires_in'] - 1   # Expire the token
    token['expires_at'] = expire_one_second_ago
    actual = spot_client.auth_manager.is_token_expired(token)

    if assert_equals(actual, True):
        pass_test()
    else:
        fail_test()

def test_spot_token_is_not_expired():
    spot_client = sp.Spotify(auth_manager=SpotifyOAuth())
    token = spot_client.auth_manager.get_cached_token()     # New token will not be expired
    actual = spot_client.auth_manager.is_token_expired(token)   

    if assert_equals(actual, False):
        pass_test()
    else:
        fail_test()

def test_get_fresh_client():
    song_db = MockSongs()
    actual = get_fresh_spotify_client(song_db)
    if assert_equals(isinstance(actual, sp.client.Spotify), True):
        pass_test()
    else:
        fail_test()



def test_handle_not_found_cannot_find():
    url = 'https://genius.com/NOTREAdsaAdwL'
    title = 'Go to Hell'
    artist = 'Letdown.'
    
    expected = '-1'
    songDb = MockSongs()
    actual = webcrawl_lyrics.handle_page_not_found(url, title, artist, songDb)

    if assert_equals(expected, actual):
        pass_test()
    else:
        fail_test()


def test_handle_not_found_can_find():
    url = 'https://genius.com/NOTREAdsaAdwL'
    title = 'sun and moon'
    artist = 'anees'
    
    actual = webcrawl_lyrics.handle_page_not_found(url, title, artist, None)

    if assert_not_equals('-1', actual):
        pass_test()
    else:
        fail_test()


def test_get_albums_outputs_populated_list():
    actual = webcrawl_lyrics.get_spotify_albums()
    if assert_not_equals(None, actual):
        pass_test()
    else:
        fail_test()

def test_all_albums_returns_some_data():
    album_ids = ['2wPnKggTK3QhYAKL7Q0vvr', '7N29psReKsIR8HOltPJqYS', '0FZK97MXMm5mUQ8mtudjuK']
    songDB = MockSongs()

    actual = webcrawl_lyrics.get_all_album_songs(album_ids, songDB)
    if assert_not_equals(None, actual):
        pass_test()
    else:
        fail_test()

def test_invalid_album_id():
    album_id = 'nope_bad'
    songs = []
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    actual = None
    try:
        actual = webcrawl_lyrics.get_album_songs(sp, album_id, songs)
    except spotipy.exceptions.SpotifyException as e:
        pass_test()

    if actual:
        fail_test()

def test_get_album_songs_returns_songs():
    album_id = '0FZK97MXMm5mUQ8mtudjuK'
    songs = []
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    try:
        webcrawl_lyrics.get_album_songs(sp, album_id, songs)
    except spotipy.exceptions.SpotifyException as e:
        print(e)
        fail_test()

    if songs:
        pass_test()


#What do you want to test?
#What do you want to have happen?
if __name__ == '__main__':
    test_assert_equals()
    test_assert_not_equals()
    test_valid_spotify_env_credentials()
    test_invalid_spotify_env_credentials()
    test_create_oath_token()
    test_refresh_returns_new_token()
    test_spot_token_is_expired()
    test_spot_token_is_not_expired()
    test_get_fresh_client()
    # test_handle_not_found_cannot_find()
    # test_handle_not_found_can_find()
    # test_spotify_album_proper_authentication()
    # test_spotify_album_bad_authentication()
    # test_get_albums_outputs_populated_list()
    # test_all_albums_returns_some_data()
    # test_invalid_album_id()
    # test_get_album_songs_returns_songs()

