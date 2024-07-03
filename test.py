import inspect
import os
from termcolor import colored
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import re
from anyascii import anyascii
from urllib.parse import quote


import spot_oath
from spot_oath import create_oath_token, refresh_access_token, get_fresh_spotify_client
import webcrawl_lyrics
import embeddings
import mapping
import make_cluster_playlists
import recommendation
from songs import MockSongs, Songs

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


# Webcrawl tests

def test_spotify_album_api_format():
    db_client = Songs() # Real database to get the users token
    spotify_client = get_fresh_spotify_client(db_client) # refresh the token
    results = spotify_client.current_user_saved_albums(limit=10, offset=0)
    items = results.get('items')
    at_last_1_album = (len(items) > 0)
    missing_album_id = (items[0]['album']['id'] == None)

    if assert_equals(at_last_1_album, True) and assert_equals(missing_album_id, False):
        pass_test() # if there's an album & an id it's valid (may fail on users not following any albums)
    else:
        fail_test() # 

def test_spotify_album_tracks():
    db_client = Songs() # Real database to get the users token
    spotify_client = get_fresh_spotify_client(db_client) # refresh the token

    results = spotify_client.album_tracks(album_id='7C72v6qIeAB1UrDSN3iwZq', limit=10, offset=0)
    first_song = results['items'][0]
    actual_song = {'name': first_song['name'], 'artist': first_song['artists'][0]['name'], 'spot_id': first_song['id']} # get name, artist, and id
    if (actual_song['name'] == 'Scene 1: Introduction') and (actual_song['artist'] == 'Naethan Apollo') and (actual_song['spot_id'] == '7k37bPIpQmRLQ3YgTK9JeV'):    # if this song is right
        pass_test()
    else:
        fail_test()

def test_albums_loop_stop_condition():
    more_albums = True
    mock_results = {'items': [
        {'added_at' : '2023-03-19T08:43:45Z', 'album': {'id': 'fake_id_1'}},
        {'added_at' : '2023-03-19T08:43:46Z', 'album': {'id': 'fake_id_2'}},
        {'added_at' : '2023-03-19T08:43:47Z', 'album': {'id': 'fake_id_3'}},
        {'added_at' : '2023-03-19T08:43:48Z', 'album': {'id': 'fake_id_4'}},
        {'added_at' : '2023-03-19T08:43:49Z', 'album': {'id': 'fake_id_5'}},
        {'added_at' : '2023-03-19T08:43:50Z', 'album': {'id': 'fake_id_6'}},
        {'added_at' : '2023-03-19T08:43:51Z', 'album': {'id': 'fake_id_7'}},
        {'added_at' : '2023-03-19T08:43:52Z', 'album': {'id': 'fake_id_8'}},
        {'added_at' : '2023-03-19T08:43:53Z', 'album': {'id': 'fake_id_9'}}
        ]
    }

    while more_albums:
        results = mock_results
        if len(results['items']) < 10:  # < 10 means we're at the end off the list
            more_albums = False # Stop while loop

    if assert_equals(more_albums, False):
        pass_test()
    else:
        fail_test()

def test_append_album_id():
    album_ids = []
    expected = ['fake_id_1', 'fake_id_2', 'fake_id_3', 'fake_id_4', 'fake_id_5', 'fake_id_6', 'fake_id_7', 'fake_id_8', 'fake_id_9', 'fake_id_10']
    mock_results = {'items': [
        {'added_at' : '2023-03-19T08:43:45Z', 'album': {'id': 'fake_id_1'}},
        {'added_at' : '2023-03-19T08:43:46Z', 'album': {'id': 'fake_id_2'}},
        {'added_at' : '2023-03-19T08:43:47Z', 'album': {'id': 'fake_id_3'}},
        {'added_at' : '2023-03-19T08:43:48Z', 'album': {'id': 'fake_id_4'}},
        {'added_at' : '2023-03-19T08:43:49Z', 'album': {'id': 'fake_id_5'}},
        {'added_at' : '2023-03-19T08:43:50Z', 'album': {'id': 'fake_id_6'}},
        {'added_at' : '2023-03-19T08:43:51Z', 'album': {'id': 'fake_id_7'}},
        {'added_at' : '2023-03-19T08:43:52Z', 'album': {'id': 'fake_id_8'}},
        {'added_at' : '2023-03-19T08:43:53Z', 'album': {'id': 'fake_id_9'}},
        {'added_at' : '2023-03-19T08:43:54Z', 'album': {'id': 'fake_id_10'}}
        ]
    }

    for i, album in enumerate(mock_results['items']):    # for every album
        album_ids.append(album['album']['id'])      # add it to the list 
    
    if assert_equals(album_ids, expected):
        pass_test()
    else:
        fail_test()

def test_search_for_song_in_database():
    mock_db = MockSongs()
    search_params = {'name' : 'valid_name', 'artist' : 'valid_artist', 'spot_id': 'valid_spot_id'}
    if mock_db.is_song_in_database(search_params):
        if not mock_db.is_song_in_not_found(search_params):   # Meaning the song is in the 'found' db already
            song_info = mock_db.find_song(search_params)
            mock_db.insert_user_song('mock_spotify_user', song_info['url'])   # Insert it for the user
            actual = True
    else:
        actual = False

    if assert_equals(actual, True):
        pass_test()
    else:
        fail_test()

def test_search_for_song_not_in_database():
    mock_db = MockSongs()
    search_params = {'name' : 'invalid_name', 'artist' : 'invalid_artist', 'spot_id': 'invalid_spot_id'}
    if mock_db.is_song_in_database(search_params):
        if not mock_db.is_song_in_not_found(search_params):   # Meaning the song is in the 'found' db already
            song_info = mock_db.find_song(search_params)
            mock_db.insert_user_song('mock_spotify_user', song_info['url'])   # Insert it for the user
            actual = False
    else:
        actual = True

    if assert_equals(actual, True):
        pass_test()
    else:
        fail_test()

def test_song_titles_regex():
    artist = anyascii("EDEN")
    title = anyascii("love; not wrong (brave)")    # these are from spotify, not ascii guaranteed
    title = re.sub('[/](?=[0-9])', ' ', title)
    # title = re.sub('[Ff]eat.*', '', title)     #fixes formating from song titles
    title = re.sub('\'', '', title)     #fixes formating from song titles #CHECK IF WITH WORKS
    title = re.sub('[?.!,+$<;]', '', title)     
    title = re.sub('\[.*\]', '', title)    # Remove anything between square brackets 
    title = re.sub('\(feat.*\)|\(with.*\)|\(ft.*\)', '', title)     
    title = re.sub('[()]', '', title)     
    title = re.sub('[/-]', ' ', title)     #fixes formating from song titles
    title = re.sub('[&]', 'and', title)
    title = re.sub('[:]', '', title)
    title = re.sub('-[*-]', '', title)
    title = re.sub(' +', ' ', title)
    title = re.sub('(?<=\d).(?=\d)', '', title) # Remove decimal in numbers

    actual = quote(title + ' ' + artist)  # Turn the title and artist into a proper url link
    if assert_equals(actual, 'love%20not%20wrong%20brave%20EDEN'):
        pass_test()
    else:
        fail_test()

def test_song_artist_regex():
    title = anyascii("Broadripple Is Burning")    # these are from spotify, not ascii guaranteed

    artist = anyascii("Margot & The Nuclear So And So's")   # these are from spotify, not ascii guaranteed
    artist = re.sub('[/](?=[0-9])', ' ', artist)
    # artist = re.sub('[Ff]eat.*', '', artist)     #fixes formating from song titles
    artist = re.sub('\'|[?.!$+,/<;{}]|\[.*\]|\(feat*\)|[()]', '', artist)
    artist = re.sub('[&]', 'and', artist)
    artist = re.sub('[:]', '', artist)
    artist = re.sub('-[*-]', '', artist)
    artist = re.sub(' +', ' ', artist)
    artist = re.sub('(?<=\d).(?=\d)', '', artist) # Remove decimal in numbers

    actual = quote(title + ' ' + artist)  # Turn the title and artist into a proper url link
    if assert_equals(actual, 'Broadripple%20Is%20Burning%20Margot%20and%20The%20Nuclear%20So%20And%20Sos'):
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
    test_spotify_album_api_format()
    test_spotify_album_tracks()
    test_albums_loop_stop_condition()
    test_append_album_id()
    test_search_for_song_in_database()
    test_search_for_song_not_in_database()
    test_song_titles_regex()
    test_song_artist_regex()
    # test_handle_not_found_cannot_find()
    # test_handle_not_found_can_find()
    # test_spotify_album_proper_authentication()
    # test_spotify_album_bad_authentication()
    # test_get_albums_outputs_populated_list()
    # test_all_albums_returns_some_data()
    # test_invalid_album_id()
    # test_get_album_songs_returns_songs()

