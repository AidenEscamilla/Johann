import urllib
from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import quote
import ssl
import time
from bs4 import BeautifulSoup
import re
from anyascii import anyascii
import nltk
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from songs import Songs # my class file
import math
from nltk.sentiment import SentimentIntensityAnalyzer
import sys  # to get the system parameter
import requests  #maybe un needed
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import unicodedata
import linecache
import os
import pickle
import sqlite3
from statistics import mode, median, mean

'''
Define options for the dynamic web scraper
headers keep it from being denied as a bot
--headless=new stops a chrome tab from popping up on screen
The rest help reduce errors (but may be unnecessary)
'''
def get_options():
  headers = {'User-Agent': 'AppleWebKit/537.36'}
  chromedriver_autoinstaller.install()
  op = webdriver.ChromeOptions()
  op.add_argument('--disable-browser-side-navigation')
  op.add_argument("--headless=new")
  op.add_argument(f"--headers={headers}")
  op.add_argument("--disable-third-party-cookies")
  op.add_argument("--pageLoadStrategy=normal")
  return op


'''
Search for matching song title, artist, & the identifier 'lyric'
In a given string called `link`.
Genius.com has 'annotated' replaces 'lyric' sometimes when a song has no lyrics 
'''
def is_matching_link(title, artist, link):
    return re.search(title.replace(" ", "."), link, re.IGNORECASE) \
            and re.search(artist.replace(" ", "."), link, re.IGNORECASE) \
            and ('lyric' in link or 'annotated' in link)

'''
SLEEP_TIME is important to prevent getting rate limited by Genius.com
Takes a list of songs, and the database
Processes the songs one at a time by constructing a Genius.com search url
Scrapes the url for a link matching the song & artist
Saves that url in the database as the "correct" url that has lyrics
'''
def process_songs(song_list, song_db):
    WAIT_TIME = 15
    SLEEP_TIME = 15
    base_url = "https://genius.com/search?q="


    driver = webdriver.Chrome(options=get_options())
    driver.implicitly_wait(WAIT_TIME)

    db = song_db
    print(song_list)
    for song in song_list:
        found_lyrics_first_try = False  # reset every song.  Used to indicate if the song needs a retry lookup or not
        artist = song.get('artist')
        title = song.get('name')

        if artist == None:  # skip podcast w/out artist
            print(f"no artist for {title}")
            continue
        
        print("PREQUOTE")
        print(title + ' ' + artist)

        # clean artist
        artist = anyascii(artist)   # these are from spotify, not ascii guaranteed
        artist = re.sub('[/](?=[0-9])', '-', artist)
        # artist = re.sub('[Ff]eat.*', '', artist)     #fixes formating from song titles
        artist = re.sub('\'|[?.!$+,/]|\[.*\]|\(feat*\)|[()]', '', artist)
        artist = re.sub('[&]', 'and', artist)
        artist = re.sub('[:]', '', artist) 
        artist = re.sub('-[*-]', '', artist)
        title = re.sub(' +', ' ', title)

        # clean title
        title = anyascii(title)    # these are from spotify, not ascii guaranteed
        title = re.sub('[/](?=[0-9])', ' ', title)
        # title = re.sub('[Ff]eat.*', '', title)     #fixes formating from song titles
        title = re.sub('\'|[?.!,+$<]|\[.*\]|\(feat*\)||\(with*\)|[()]', '', title)     #fixes formating from song titles #CHECK IF WITH WORKS
        title = re.sub('[/-]', ' ', title)     #fixes formating from song titles
        title = re.sub('[&]', 'and', title)
        title = re.sub('[:]', '', title)
        title = re.sub('-[*-]', '', title)
        title = re.sub(' +', ' ', title)

        text_encoded = quote(title + ' ' + artist)  # Turn the title and artist into a proper url link
        print("QUOTE:", text_encoded)

        try:
            driver.get(base_url + text_encoded) # Go to url
            time.sleep(10) # Only way I found that sucessfully prevented rate limiting
            html = driver.page_source # Get dynamic html
        except Exception as e:
            print("error, skipping page: ", base_url + text_encoded)
            print("error was: ", e)
            continue    # Skip errors

        soup = BeautifulSoup(html, 'html.parser')   # parse html
    
        for link in soup.find_all('a', class_="mini_card"): # mini_cards hold links to lyrics
            link_str = link.get('href').lower()
            print('.', end="")
            if is_matching_link(title, artist, link_str):
                # insert into song db
                found_lyrics_first_try = True
                print('FOUND:', link_str)
                song['url'] = link_str
                db.insert_song(song)
                break # only insert 1 song ()
        
        if not found_lyrics_first_try:  #retry song
            retry_finding_song(song, driver, db)
        
    driver.quit()   # close chrome driver/scraper


'''
Takes the song we're searching for, the driver we're using, and the database
Tries the same processing_song approach, but truncates the artist from the initial search
Currently does not do any title or artist clean up, maybe it should
'''
def retry_finding_song(song_dict, chrome_driver, database):
    title = song_dict.get('name')
    artist = song_dict.get('artist')

    # clean title
    title = anyascii(title)    # these are from spotify, not ascii guaranteed
    title = re.sub('[/](?=[0-9])', ' ', title)
    # title = re.sub('[Ff]eat.*', '', title)     #fixes formating from song titles
    title = re.sub('\'|[?.!,+$<]|\[.*\]|\(feat*\)||\(with*\)|[()]', '', title)     #fixes formating from song titles #CHECK IF WITH WORKS
    title = re.sub('[/-]', ' ', title)     #fixes formating from song titles
    title = re.sub('[&]', 'and', title)
    title = re.sub('[:]', '', title)
    title = re.sub('-[*-]', '', title)
    title = re.sub(' +', ' ', title)
    
    text_encoded = quote(title) # here is the different search query
    base_url = "https://genius.com/search?q="

    print("RETRY QUOTE:", text_encoded)
    try:
        chrome_driver.get(base_url + text_encoded)  # Search for url by title only
        time.sleep(10)
        html_retry = chrome_driver.page_source
    except Exception as e:
        print("error, skipping page: ", base_url + text_encoded)
        print("error was: ", e)
        song_dict['url'] = base_url + text_encoded  # add url
        song_dict['error'] = e  # add error
        database.insert_into_not_found(song_dict)   # insert and return nothing 
        return None

    soup_retry = BeautifulSoup(html_retry, 'html.parser')

    found_lyrics_on_retry = False   # flag
    for link_retry in soup_retry.find_all('a', class_="mini_card"): # for every link in search results 'mini_card' object
        link_str_retry = link_retry.get('href').lower()                             # annotated for classical/no lyric pieces
        if is_matching_link(title, artist, link_str_retry): # If the song is found
            # insert into song db
            print('FOUND on RETRY:', link_str_retry)
            found_lyrics_on_retry = True    # Change flag to skip "not_found"
            song_dict['url'] = link_str_retry
            database.insert_song(song_dict) # Insert what we found
            break # only insert 1 song ()
    
    if not found_lyrics_on_retry:   # If flag -> add to "not_found" for later analysis
        song_dict['url'] = base_url + text_encoded  # add url
        song_dict['error'] = "No URL found" # Craft an "error"
        database.insert_into_not_found(song_dict)


'''
DEPRECIATED
Use spotipy library to get all the artists followed by a user
Puts them in a set and returns the set
'''
def get_spotify_artists(track_limit):
    artist = []
    scope = "user-library-read"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=15)
    results = sp.current_user_saved_tracks(limit=track_limit) 

    for item in results['items']:
        track = item['track']
        artist.append(track['artists'][0]['name'])

    return [*set(artist)]

'''
Gets all the albums a user follows on Spotify
Goes through adding their id's to a set 10 at a time
Returns the list of ids
'''
def get_spotify_albums():
    album_ids = []
    album_offset = 0
    more_albums = True  # Flag for while loop
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=15)

    while more_albums:
        results = sp.current_user_saved_albums(limit=10, offset=album_offset)
        if len(results['items']) < 10:  # < 10 means we're at the end off the list
            more_albums = False # Stop while loop

        for i, album in enumerate(results['items']):    # for every album
            album_ids.append(album['album']['id'])      # add it to the list    
        album_offset += 10  # next 10 albums
        print(album_offset)
        
    return album_ids

'''
Takes the spotipy client (sp), a single album, and a running list of songs
Goes through all the songs on an album and adds their info to the songs list.
(should return the list. Seems the songs list is passes by reference. \
Less coding for me, raises concerns to check into, but seems to be working)
'''
def get_album_songs(sp, album):  #borken?
    songs_from_spotify = []
    more_songs = True   # Flag for while loop
    offset = 0

    while more_songs:
        results = sp.album_tracks(album_id=album, limit=10, offset=offset)  # get songs 10 at a time
        
        for item in results['items']:
            if item['is_local']:    #Skip local files
                continue

            temp = {'name': item['name'], 'artist': item['artists'][0]['name'], 'spot_id': item['id']} # get name and artist
            songs_from_spotify.append(temp)  # add to list

        if len(results['items']) < 10:  # no more songs, break while loop (old comment said this was broken?)
            offset = 0
            more_songs = False
        else:
            offset += 10    # Continue to find next 10 sings
    
    return songs_from_spotify

'''
Takes the list of all album ids
Gets their songs
And runs them through processing
Returns the list of songs with their found urls (to later find lyrics for them)
'''        
def get_all_album_songs(album_ids, song_db):
    total_songs = []
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=15)
    for album in album_ids:
        songs = get_album_songs(sp, album)

        for song in songs:
            total_songs.append(song)


    #make a set of songs before processing
    #todo: make this a single line function/ google set function
    songs_set = []
    for song in total_songs:
        if not song in songs_set:
            songs_set.append(song)
    
    for song in songs_set:
        print(f"Song:{song}")
        info = song_db.search_user_song_by_title_and_artist(song['name'], song['artist'])
        if info != -1:
            song['url'] = info['url']
            song_db.insert_song(song)
        else:
            print(f"ISSUE# {song.get('name')}:{song.get('artist')}")
   #process_songs(songs_set, song_db) #todo: next to unit test   
    return songs

'''
Get all the playlist a user follows (I think this includes user made playlists)
Returns a list of the playlist id's
'''
def get_spotify_playlists():
    more_playlists = True   # Flag for while loop
    my_offset = 0
    playlists_ids = []
    scope = "playlist-read-private"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=15)

    while more_playlists:
        results = sp.current_user_playlists(limit=10, offset=my_offset) # Get playlists 10 at a time
        
        if len(results['items']) < 10:  # If no more playlists
            more_playlists = False  # break while loop

        for i, playlist in enumerate(results['items']): 
            playlists_ids.append(playlist['id'])    # Add playlist to list       

        my_offset += 10 # Get 10 more playlists
        
    return playlists_ids


'''
Takes the list of playlist id's
Gets the songs from each playlist
Runs all the songs through processing
Returns the list of songs with their found urls (to later find lyrics for them)
'''
def get_playlist_songs(playlist_id_list, song_db):
    my_offset = 0
    songs = []
    temp = {}
    more_songs = True   # Flag for while loop

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(), requests_timeout=15)
    for playlist in playlist_id_list:   # For every playlist
        
        while more_songs:
            results = sp.playlist_tracks(playlist_id=playlist, fields='items(track(id,name,artists(name)))', limit=10, offset=my_offset)   # Get songs from playlist
            
            for item in results['items']:
                if not item['track']: #skip empty tracks
                    continue

                temp = {'name': item['track']['name'], 'artist': item['track']['artists'][0]['name'], 'spot_id': item['track']['id']}   # Format the song from spotify -> dict
                songs.append(temp)  # Add song to list
        
            if len(results['items']) < 10:
                more_songs = False
            else:
                my_offset += 10

        more_songs = True   # Reset to true for next playlist going into while loop


    #make a set of songs before processing
    #todo: use function/solution found in above todo
    set_maker = []
    for song in songs:
        if not song in set_maker:
            set_maker.append(song)

    songs = set_maker   #tested, it works

    process_songs(songs, song_db)   # Get correct url & insert songs
   
    return songs

'''
Get all the saved songs from users "Saved/liked/hearted" list (Spotify keeps changing the name)
Note: As of now this can find and re-process songs previously found in albums and playlists followed
'''
def get_spotify_songs(song_db):
    songs = []
    # urlList = []  Seems like these two lines are leftover from who knows when
    # songDict = {}
    more_songs = True   # Flag for while loop
    song_offset = 0
    scope = "user-library-read"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=15)

    while more_songs:
        results = sp.current_user_saved_tracks(limit=25, offset=song_offset)    # Gets saved songs 25 at a time

        for item in results['items']:   # For every song
            track = item['track']
            temp = {'name': track['name'], 'artist': track['artists'][0]['name'], 'spot_id': track['id']}   # Format spotify song -> dict
            songs.append(temp)  # Add to list
        
        if len(results['items']) < 10:  # Todo: This should be changed to 25. Too scared to change it right now
            more_songs = False
        else:
            song_offset += 25
    
    process_songs(songs, song_db)    # Get correct url & insert songs
    return songs

'''
Takes a url and web scrapes the lyrics
Returns the lyrics found (including empty string for no lyrics), or None on Error
'''
def get_lyrics(lyric_url):
    headers = {'User-Agent': 'AppleWebKit/537.36'}
    req = Request(url=lyric_url, headers=headers)

    try:
        html = urlopen(req).read().decode('utf-8')  # Get html
    except urllib.error.HTTPError as errh:
        print("OOpps http error for:", lyric_url)   # Return nothing on error
        return None
  

    lyric_soup = BeautifulSoup(html, features="html.parser")    # Soup it
    containers = lyric_soup.find_all('div', {"data-lyrics-container": True})    # This is the specific lyric box AS OF NOW on Genius.com
    text = ''
    for content in containers:  # Somtimes it's multiple boxes
                text += content.getText()   # Appened lyrics

    #txt clean up
    text = re.sub('\[[^\]]*\]', '', text)               #Delete everything between [] including brackets like '[Verse 1]', '[Chrous]', ect.
    text = re.sub('(?<=[?!])(?=[A-Z])', '. ', text)      #fixes lines that end in ?
    text = re.sub('\'(?=[A-Z])', '. ', text)         #Fixes "country" ' thats used to start a word e.x: 'Cause
    text = re.sub('(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z])', '. ', text)          #space out text because the <br /> is thrown away leaving words touching and hard to tokenize. 
                                                                                    #Buuut you can seperate by capital letters because every new line they capitalize
    text = text.replace('wanna', 'want to')         #Fix wanna to want to
    text = re.sub('[Cc]an\'t', 'can not', text)     #replace can't or Can't with can not because word tokenize stops reading past ' because it's not alpha
    text = text.replace('...', '. ')               #This line and the one below fix specific formatting found on the website. This fixes ellipses
    text = text.replace('Cause', 'Because')         #This fixes "country" grammar
    text = re.sub(' \(*x[0-9]\)*', '. ', text) #This fixes the '(x2)' text
    text = re.sub('x[0-9]', '. ', text)            #This fixes x2, x3, x4... ect when not in parenthesis
    
  
    lyrics_output = ''
    text = sent_tokenize(text)
    for sentence in text:
        lyrics_output += sentence + " " # Make it readable

    #todo: Add \n to introduce the new line in order to give chatgpt the formatted version of the lyrics
            #Stanzas and new lines helps it recognize patterns, sections of ideas, and sentiment (mood and themes are the same without stanzas)

    print(lyric_url)
    print(lyrics_output)
    print("moving to next song")
    return lyrics_output

'''
Takes the song database client, and the list of songs to find lyrics for
Grabs the song url from the database (because earlier the found url was saved in the db)
Scrapes the url for lyrics
'''
def generate_lyric_files(song_data_base, new_songs_list):
    lyrics = None

    for song in new_songs_list: # For every song in the list provided
        print(song)
        found_song = song_data_base.search_user_song_by_title_and_artist(song.get('name'), song.get('artist'))

        if found_song != -1:    # If song in database
            lyrics = get_lyrics(found_song.get('url'))
        else:   # skip 'no url found'
            continue

        if lyrics == None:       #Skip 404's
            continue
        
        lyrics = anyascii(lyrics)   # EDIT: convert lyrics with anyascii (untested but should work) This prevents pesky \u2005 spaces
        temp = {'url': found_song.get('url'), 'lyrics': lyrics} # format to dict for db input
        song_data_base.insert_into_lyrics(temp) # input lyrics into the dict 

'''
Takes the song databse client, song being searched by user, and a first time flag
I dont know 100% how this works anymore
'''
def lyric_recommendation(song_database, song_wanting_recommendation_for, first_time_flag):
    
    dataframe_recommended_song = {}
    error_message = 'Sorry, I could not find that song from your library'
    error_message2 = 'Sorry, the song wasn\'t found in the vectorized database'
    lyrics_row = []


    if len(song_wanting_recommendation_for) == 1:   # If only artist was input
        answer = song_database.search_user_song_by_title(song_wanting_recommendation_for[0])    # Database search by title
        if answer == -1:    # if not found
            return error_message
        
        print(answer['name'], ': ', answer['artist'])

        lyrics_row = song_database.find_song_with_name_artist_and_lyrics(answer['name'], answer['artist'])  # See if the song found has lyrics
        if lyrics_row == None: #maybe bug found HERE. 'None' lyrics slipping through sql call
            return error_message2

        dataframe_recommended_song['text'] = lyrics_row['lyrics']   # Format song -> dict
        dataframe_recommended_song['artist'] = lyrics_row['artist']
        dataframe_recommended_song['song'] = lyrics_row['name']
        dataframe_recommended_song['link'] = lyrics_row['url']
    elif len(song_wanting_recommendation_for) == 2: # If song title and artist provided by user
        recommendation_artist = song_wanting_recommendation_for[1]
        answer = song_database.search_user_song_by_title_and_artist(song_wanting_recommendation_for[0], recommendation_artist)  # Search database by song title and artist
        if answer == -1:    # if not found
            return error_message

        print(answer['name'], ': ', answer['artist'])

        lyrics_row = song_database.find_song_with_name_artist_and_lyrics(answer['name'], answer['artist'])  # Find lyrics for the song
        if lyrics_row == None:
            return error_message2

        dataframe_recommended_song['text'] = lyrics_row['lyrics']       # Format song -> dict
        dataframe_recommended_song['artist'] = lyrics_row['artist']
        dataframe_recommended_song['song'] = lyrics_row['name']
        dataframe_recommended_song['link'] = lyrics_row['url']


    if first_time_flag: # If the user is new to the program

        connection = song_database.connection   # UHHHH CHECK THIS?!?! ERROR, Todo, UH OH
        print(connection)
        
        # Get all songs with lyrics
        sql_query = pd.read_sql_query ('''
                                SELECT DISTINCT s.url AS link, name AS song, artist, lyrics AS text  FROM songs AS s INNER JOIN lyrics AS l on s.url = l.url WHERE length(lyrics) > 0
                                ''', connection)
        dfUser = pd.DataFrame(sql_query, columns = ['artist', 'song', 'link', 'text',]) # Put songs into dataframe
        print ('Your songs as a Panda df!:\n', dfUser)

        dataframe_recommended_song = pd.DataFrame(dataframe_recommended_song, columns = ['artist', 'song', 'link', 'text',], index=[0])
        df = pd.read_csv('spotify_millsongdata.csv')    # Read csv
        df = pd.concat([df, dfUser], ignore_index=True) # WHYS THIS HERE ERROR TOdo UH OH
        df = pd.concat([dataframe_recommended_song, df], ignore_index=True) # Add recommended songs to millsongs
        df.reset_index()

        X = df.text
                    #making max_df high gets rid of stopwords, can play with this variable and ngrams
        vectorizer = TfidfVectorizer(max_df=0.7, ngram_range=(2, 4))
        Xtfid = vectorizer.fit_transform(X) # Vectorize all songs
        
        with open('millTfidVector.pickle', 'wb') as handle: # Save as pickle to go by faster evry time
            pickle.dump(Xtfid, handle)
        with open('pdDataFrame.pickle', 'wb') as handle:
            pickle.dump(df, handle)


    with open('millTfidVector.pickle', 'rb') as handle: # Open pickles made by first time
        Xtfid = pickle.load(handle)
    with open('pdDataFrame.pickle', 'rb') as handle:
        df = pickle.load(handle)

    found_index = df.loc[df['link'] == lyrics_row['url']].index.values[0]
    recommendations_found = cosine_similarity(Xtfid[found_index], Xtfid)    # Get cosine sim recommended songs

    print('\nStdev: ', np.std(recommendations_found))   # Cool data output
    meanVar = mean(recommendations_found.tolist()[0])
    print('mean: ', meanVar)
    median_value = median(recommendations_found.tolist()[0])
    print('Median: ', median_value, '\n')
    #Uncomment below to see the cosine vector score if you're curious
    topTen = sorted(recommendations_found[0], reverse=True)[2:12]

    recommendations = []
    for i, vector in enumerate(recommendations_found.tolist()[0]):
        if(vector in topTen):
            recommendations.append([i, vector]) # Add to top ten

    index_list = []
    for pair in recommendations:    # Forget what this does
        index_list.append(pair[0])

    data_recommendations = []
    for rec_index in index_list[0:11]:  # I still forget
        data_recommendations.append(str(df.iloc[[rec_index]]['song'].values[0] + ': by ' + df.iloc[[rec_index]]['artist'].values[0]))
    
    print('\nTop ten songs based on lyrics:\n')
    for song_rec in data_recommendations:
        print(song_rec, '\n')

    return 'Finished lyric execution Properly'

'''
Takes the song database client
Gets permissions to access all songs and gets the songs from the logged in spotify user
Gets the lyrics to the songs
'''
def setup(database_songs):
    album_ids = get_spotify_albums()
    album_songs_list = get_all_album_songs(album_ids, database_songs)
    
    playlist_id_list = get_spotify_playlists()
    playlist_songs_list = get_playlist_songs(playlist_id_list, database_songs)
    
    saved_songs_list = get_spotify_songs(database_songs)
    
    user_songs = album_songs_list + playlist_songs_list + saved_songs_list
    #todo: put in better spot that utilizes a first time flag
    generate_lyric_files(database_songs, user_songs)

def main():
    song_db = Songs()
    # setup(song_db)
    
    quit()
    
    '''
    #build knowledge base: add sentiment score to db
    build_knowledge_base(con, tf_idf_list)
    quit()
    '''
# if __name__ == '__main__':
    # os.environ["SPOTIPY_CLIENT_ID"] = "PUBLIC_ID"
    # os.environ["SPOTIPY_CLIENT_SECRET"] = "SECRET_KEY"
    # os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"