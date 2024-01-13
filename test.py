import inspect
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import WebCrawlSpotify
from songs import MockSongs

def assert_equals(expected, actual):
    return expected == actual
        

def assert_not_equals(expected, actual):
    return not expected == actual
        

def pass_test():
    print(inspect.stack()[1][3] + ' - pass')

def fail_test():
    print(inspect.stack()[1][3] + ' - fail')

def test_assert_equals():
    if assert_equals(1,1):
        pass_test()
    else:
        fail_test()



def test_empty_url_returns_negative_one():
    expected = '-1'
    actual = WebCrawlSpotify.get_soup_from_website(None, 'n/a', 'n/a', None)
    if assert_equals(expected, actual):
        pass_test()
    else:
        fail_test()
 




def test_handle_not_found_cannot_find():
    url = 'https://genius.com/NOTREAdsaAdwL'
    title = 'Go to Hell'
    artist = 'Letdown.'
    
    expected = '-1'
    songDb = MockSongs()
    actual = WebCrawlSpotify.handle_page_not_found(url, title, artist, songDb)

    if assert_equals(expected, actual):
        pass_test()
    else:
        fail_test()


def test_handle_not_found_can_find():
    url = 'https://genius.com/NOTREAdsaAdwL'
    title = 'sun and moon'
    artist = 'anees'
    
    actual = WebCrawlSpotify.handle_page_not_found(url, title, artist, None)

    if assert_not_equals('-1', actual):
        pass_test()
    else:
        fail_test()

def test_spotify_album_proper_authentication():
    os.environ["SPOTIPY_CLIENT_ID"] = "9534b2ba3dd4408fbee3d0bf3cf4d912"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "aa0326708f2f41fb90dcda386989de53"
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"  #this will oen a browser page, follow terminal instructions
    actual = None
    try:
        actual = WebCrawlSpotify.get_spotify_albums()
    except spotipy.oauth2.SpotifyOauthError as e:
        print(e)
        pass #invalid credentials

    if assert_not_equals(None, actual):
        pass_test()
    else:
        fail_test()

def test_spotify_album_bad_authentication():
    #Commented out to save time testing. This test will fail after a proper auth token is cached
    #if os.path.exists('.cache'):
    #    os.remove('.cache')
    
    os.environ["SPOTIPY_CLIENT_ID"] = "publicBad"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "secretBad"
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"  #this will oen a browser page, follow terminal instructions
    actual = None
    try:
        actual = WebCrawlSpotify.get_spotify_albums()
    except spotipy.oauth2.SpotifyOauthError as e:
        pass_test()
    
    if actual:
        fail_test()

def test_get_albums_outputs_populated_list():
    actual = WebCrawlSpotify.get_spotify_albums()
    if assert_not_equals(None, actual):
        pass_test()
    else:
        fail_test()

def test_all_albums_returns_some_data():
    album_ids = ['2wPnKggTK3QhYAKL7Q0vvr', '7N29psReKsIR8HOltPJqYS', '0FZK97MXMm5mUQ8mtudjuK']
    songDB = MockSongs()

    actual = WebCrawlSpotify.get_all_album_songs(album_ids, songDB)
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
        actual = WebCrawlSpotify.get_album_songs(sp, album_id, songs)
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
        WebCrawlSpotify.get_album_songs(sp, album_id, songs)
    except spotipy.exceptions.SpotifyException as e:
        print(e)
        fail_test()

    if songs:
        pass_test()

# def test_all_albums_returns_no_data():
#     album_ids = ['nope', 'bad']
#     songDB = MockSongs()

#     try:
#         actual = WebCrawlSpotify.get_all_album_songs(album_ids, songDB)
#     except spotipy.exceptions.SpotifyException as e:
#         print(e)



#What do you want to test?
#What do you want to have happen?
if __name__ == '__main__':
    test_assert_equals()
    test_empty_url_returns_negative_one()
    test_handle_not_found_cannot_find()
    test_handle_not_found_can_find()
    test_spotify_album_proper_authentication()
    test_spotify_album_bad_authentication()
    test_get_albums_outputs_populated_list()
    test_all_albums_returns_some_data()
    #test_all_albums_returns_no_data() work in progress (wip)
    test_invalid_album_id()
    test_get_album_songs_returns_songs()