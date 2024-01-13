import urllib
from urllib.request import urlopen
from urllib.request import Request
import ssl
from bs4 import BeautifulSoup
import re
import nltk #maybe un needed
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

def process_songs(song_list, song_db):
    url = "https://genius.com/"
    db = song_db
    for song in song_list:
        #print(song)
        artist = song.get('artist')
        title = song.get('name')

        artist = re.sub('[/](?=[0-9])', '-', artist)
        artist = re.sub('[Ff]eat.*', '', artist)     #fixes formating from song titles
        artist = re.sub('\'|[?.!$+,/]|\(feat*\)|[()]', '', artist)
        artist = re.sub('[&]', 'and', artist)
        artist = re.sub('[:]', '-', artist)

        title = re.sub('[/](?=[0-9])', '-', title)
        title = re.sub('[Ff]eat.*', '', title)     #fixes formating from song titles
        title = re.sub('\'|[?.!,+$/]|\(feat*\)|[()]', '', title)     #fixes formating from song titles
        title = re.sub('[&]', 'and', title)
        title = re.sub('[:]', '-', title)

        artist = artist.split(' ')
        artist = '-'.join(artist).lower()
        artist = re.sub('-[*-]', '', artist)

        title = title.split(' ')
        title = '-'.join(title).lower()
        title = re.sub('-[*-]', '', title)

        tokens = (artist + ' ' + title).split()
        if len(tokens) != 0:
            url_string = url + tokens[0] +'-' + '-'.join(tokens[1:]).lower() + '-lyrics'
            url_string = re.sub('-[*-]', '', url_string)      #Fixes specific formatting for many spaces and a dash included in title 
            
            song['url'] = url_string
            db.insert_song(song)


def get_spotify_artists(track_limit):
    artist = []
    scope = "user-library-read"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_saved_tracks(limit=track_limit)
    for item in results['items']:
        track = item['track']
        #print(track['artists'][0]['name'], " – ", track['name'], ' - ', track['album']['name'])
        #albums.append(track['album']['name'])
        artist.append(track['artists'][0]['name'])
        


    return [*set(artist)]


def get_spotify_albums():
    album_ids = []
    album_offset = 0
    more_albums = True
    counter = 0
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    while more_albums:
        results = sp.current_user_saved_albums(limit=10, offset=album_offset)
        if len(results['items']) < 10:
            more_albums = False

        for i, album in enumerate(results['items']):
            album_ids.append(album['album']['id'])          
        album_offset += 10
        
    return album_ids

def get_album_songs(sp, album, songs):
    more_songs = True
    offset = 0

    while more_songs:
            #print("ALBUM ID = ", album)
            results = sp.album_tracks(album_id=album, limit=10, offset=offset)
            
            for item in results['items']:
                if item['is_local']:    #Skip local files
                    continue
                #print(item['name'], ': ', item['artists'][0]['name'])
                temp = {'name': item['name'], 'artist': item['artists'][0]['name']}
                songs.append(temp)

            if len(results['items']) < 10:
                offset = 0
                more_songs = False
            else:
                offset += 10

        
def get_all_album_songs(album_ids, song_db):
    songs = []
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    for album in album_ids:
        get_album_songs(sp, album, songs)

    #make a set of songs before processing
    songs_set = []
    for song in songs:
        if not song in songs_set:
            songs_set.append(song)

    process_songs(songs_set, song_db) #next to unit test   
    return songs


def get_spotify_playlists():
    more_playlists = True
    my_offset = 0
    playlists_tracks_urls = []
    scope = "playlist-read-private"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    while more_playlists:
        results = sp.current_user_playlists(limit=10, offset=my_offset)
        
        if len(results['items']) < 10:
            more_playlists = False

        for i, playlist in enumerate(results['items']):
                #print(i, ': ', playlist['name'], '\n', playlist['tracks']['href'], '\n') 
            playlists_tracks_urls.append(playlist['id'])          
        #print('LINE: ', my_offset/10)
        my_offset += 10

        
    #print("PLAYLISTS = ", playlists_tracks_urls)
    return playlists_tracks_urls



def get_playlist_songs(track_url_list, song_db):
    my_offset = 0
    songs = []
    urlList = []
    songDict = {}
    temp = {}
    more_songs = True

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    for playlist in track_url_list:
        #print('PLAYLIST: ', playlist)
        
        while more_songs:
            results = sp.playlist_tracks(playlist_id=playlist, fields='items(track(name,artists(name)))', limit=10, offset=my_offset)
            
            for item in results['items']:
                # if not item:
                #     print("Nonetype error: ", item)
                # elif item['is_local']:    #Skip local files
                #     continue
                if not item['track']: #skip empty tracks
                    continue

                temp = {'name': item['track']['name'], 'artist': item['track']['artists'][0]['name']}
                songs.append(temp)
        
            if len(results['items']) < 10:
                more_songs = False
            else:
                my_offset += 10

        more_songs = True


    #make a set of songs before processing
    set_maker = []
    for song in songs:
        if not song in set_maker:
            set_maker.append(song)

    songs = set_maker   #tested, it works

    process_songs(songs, song_db)
   
    #result = connection.execute('SELECT * FROM Song')
    #for row in result.fetchall():
    #    print(row['name'], ' - ', row['artist'])

    return songs


def get_spotify_songs(song_db):
    songs = []
    urlList = []
    songDict = {}
    more_songs = True
    song_offset = 0
    scope = "user-library-read"
    counter = 0
    #CHANGE COUNTER FOR MORE SONGS IN LIBRARY
    
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    while more_songs:
        #print('IN SONG LIBRARY')
        results = sp.current_user_saved_tracks(limit=25, offset=song_offset)
        for item in results['items']:
            track = item['track']
            temp = {'name': track['name'], 'artist': track['artists'][0]['name']}
            songs.append(temp)
            counter += 1
        if len(results['items']) < 10:# or counter >= 25:
            more_songs = False
        else:
            #print(counter)
            #print('OffSet = ', song_offset, 'len(items): ', len(results['items']))
            #print(songs[9 + song_offset])
            song_offset += 25
        

    
    process_songs(songs, song_db)    
    
    return songs



def filter_page(soup, output_file_name, filter_artist, filter_song):
    with open(output_file_name, 'w') as f:
        for link in soup.find_all('a'):
            link_str = str(link.get('href')).lower()
            tokens = filter_song.split('-')
            for token in tokens:
                if filter_artist in link_str and token in link_str and 'lyric' in link_str: 
                    #print('FOUND: ' , link_str, '\n')
                    if link_str.startswith('/url?q='):
                        link_str = link_str[7:]
                        print('MOD:', link_str)
                    if '&' in link_str:
                        i = link_str.find('&')
                        link_str = link_str[:i]
                    if link_str.startswith('http') and 'google' not in link_str:
                        f.write(link_str + '\n')
                        continue

def filter_page_append(soup, output_file_name, filter_string, more_filter_string):
    with open(output_file_name, 'a') as f:
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            print(link_str)
            if filter_string in link_str and more_filter_string in link_str: #ex. and 'Boywithuke' in link_str:
                if link_str.startswith('/url?q='):
                    link_str = link_str[7:]
                    print('MOD:', link_str)
                if '&' in link_str:
                    i = link_str.find('&')
                    link_str = link_str[:i]
                if link_str.startswith('http') and 'google' not in link_str:
                    f.write(link_str + '\n')

def handle_page_not_found(url, title, artist, songDB):
    headers = {'User-Agent': 'AppleWebKit/537.36'}
    notFound = {'url': url, 'name': title, 'artist': artist}

    artist = artist.split(' ')
    artist = '-'.join(artist).lower()
    artist = re.sub('-[*-]', '', artist)

    title = title.split(' ')
    title = '-'.join(title).lower()
    title = re.sub('-[*-]', '', title)

    artist_url = 'https://genius.com/artists/' + artist
    req = Request(url=artist_url, headers=headers)
    try:        #Future fix: https://genius.com/artists/{firstName}-{LastName}/songs
                #li class = 'ListItem__Containter* get the href ending in lyric containing 'song title''
        html = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style", "html.parser"]):
            script.extract()    # rip it out
        
        filter_page(soup, 'tryingArtist.txt', artist, title)
        
        trying = linecache.getline('tryingArtist.txt', 1)
        finding_lyrics_url = trying# + '-lyrics'

        if not finding_lyrics_url.startswith('http'):
            raise urllib.error.HTTPError(url=finding_lyrics_url, code=None, msg='empty', hdrs=headers, fp=None)

        req = Request(url=finding_lyrics_url, headers=headers)
        html = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style", "html.parser"]):
            script.extract()    # rip it out
        return soup
    
    except urllib.error.HTTPError as e:
        notFound['error'] = 'urllib.error.HTTPError'
        songDB.insertToNotFound(notFound)
        return '-1'
    except UnicodeEncodeError as typo:
        notFound['error'] = 'UnicodeEncodeError'
        songDB.insertToNotFound(notFound)
        return '-1'


def get_soup_from_website(url, title, artist, songDB):

    headers = {'User-Agent': 'AppleWebKit/537.36'}

    if not url:
        return '-1' #Find out how a None object is getting here
    elif not url.isascii():
        temp = unicodedata.normalize('NFKD', url).encode('Ascii', 'ignore')
        url = temp.decode('utf-8')    

    req = Request(url=url, headers=headers)
    #TRY CATCH 404 ERROR HERE
    try:
        html = urlopen(req).read().decode('utf-8')
        
    except urllib.error.HTTPError as errh:
        return handle_page_not_found(url, title, artist, songDB)
    

    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style", "html.parser"]):
        script.extract()    # rip it out

    # extract text
    return soup


def generate_lyric_files(song_data_base, new_songs_list):

    for song in new_songs_list:
        #print('DictGet: ', songNotWorking.get(url))
        lyric_soup = get_soup_from_website(song.get('url'), song.get('name'), song.get('artist'), song_data_base)
        
        if lyric_soup == '-1':       #Skip 404's
            #print('skipped: ', url)
            continue
        
        if isinstance(lyric_soup, int):
            print(lyric_soup)
        containers = lyric_soup.findAll('div', {"data-lyrics-container": True})

        text = ''

        for content in containers:
            text += content.getText()

        #txt clean up
        text = re.sub('\[[^\]]*\]', '', text)               #Delete everything between [] including brackets like '[Verse 1]', '[Chrous]', ect.
        text = re.sub('(?<=[?!])(?=[A-Z])', '. ', text)      #fixes lines that end in ?
        text = re.sub('\'(?=[A-Z])', '. ', text)         #Fixes "country" ' thats used to start a word e.x: 'Cause
        text = re.sub('(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z])', '. \n', text)          #space out text because the <br /> is thrown away leaving words touching and hard to tokenize. 
                                                                                        #Buuut you can seperate by capital letters because every new line they capitalize
                                                                                        #Added \n to introduce the new line in order to give chatgpt the formatted version of the lyrics
                                                                                        #Stanzas and new lines helps it recognize patterns, sections of ideas, and sentiment (mood and themes are the same without stanzas)
        text = text.replace('wanna', 'want to')         #Fix wanna to want to
        text = re.sub('[Cc]an\'t', 'can not', text)     #replace can't or Can't with can not because word tokenize stops reading past ' because it's not alpha
        text = text.replace('...', '. ')               #This line and the one below fix specific formatting found on the website. This fixes ellipses
        text = text.replace('Cause', 'Because')         #This fixes "country" grammar
        text = re.sub(' \(*x[0-9]\)*', '. ', text) #This fixes the '(x2)' text
        text = re.sub('x[0-9]', '. ', text)            #This fixes x2, x3, x4... ect when not in parenthesis
        #print(text)
        text = sent_tokenize(text)
        
        
        
        lyrics_output = ''
        for sentence in text:
            lyrics_output += sentence + " "

        temp = {'url': song.get('url'), 'lyrics': lyrics_output}
        song_data_base.insert_to_lyrics(temp)
    


#Term frequency (TF) is how often a token appears in a document 
def create_term_frequency(song_given, song_db):
    tokens = []
    stop_words = set(stopwords.words('english'))
    tf_dict = {}
    

    #cleaned_lyrics = re.sub('!', '. ', song_given['lyrics'])
    #cleaned_lyrics = re.sub('?', '. ', cleaned_lyrics)
    song_given = song_db.get_song_with_lyrics(song_given['name'], song_given['artist'])
    if song_given == None:
        return '-1'
    cleaned_lyrics = song_given['lyrics'].split('.')

    for line in cleaned_lyrics:      #for eevry line tokenize 
        tokens += word_tokenize(line.lower())
    
    tokens = [w for w in tokens if w.isalpha() and w not in stop_words] #get clean tokens #This w.isalpha() messes up apostrophies need to fix that
    
    token_set = set(tokens)
    tf_dict = {t:tokens.count(t) for t in token_set}   #create dict
    for token in tf_dict.keys():
        tf_dict[token] = tf_dict[token] / len(tokens)   #calc requency
    
    return tf_dict
#tf * idf is similar to an inportance measure for a token based on your corpus (training data)
def create_tfidf(tf, idf):
    tf_idf = {}
    for t in tf.keys():
        if t == 'Document': #skip the title i added
            continue
        tf_idf[t] = tf[t] * idf[t] 
        
    return tf_idf


def createTF_IDF_TfxIdf(songDB, userSongList):

    userSongRows = []
    #come back and see if this is usless with a better query
    for song in userSongList:
        userSongRows.append(songDB.getTitleArtistSong(song['name'], song['artist']))
    num_docs = int(len(userSongRows))
    print(num_docs)
    #create tf dictionaries
    tf = []

    #result = con.execute('SELECT lyrics FROM Lyrics')
    #rows = result.fetchall()
    #for i, row in enumerate(rows):
    #    print(i, ':###### ', row['lyrics'])
    #maybe prob here
    
    for i, songRow in enumerate(userSongRows):
        if songRow == None:
            continue
        #print(i, 'SONG: ', songRow['name'], " - ", songRow['artist'])
        temp = create_term_frequency(songRow, songDB)
        if temp == '-1':
            continue
        temp['Document'] = songRow['url']
        tf.append(temp)
    
    #create vocab
    vocab = set()
    for dictionary in tf:
        vocab = vocab.union(set(dictionary.keys()))

    #create inverse document frequency (idf) dict. If a word appears in every document its common if its in only 1 or 2 its a rare term
    idf_dict = {}
    vocab_by_topic = []
    for d in tf:
        vocab_by_topic.append(d.keys())


    for term in vocab:
        temp = ['x' for voc in vocab_by_topic if term in voc]
        idf_dict[term] = math.log((1+num_docs) / (1+len(temp))) 


    #create tf-idf
    tf_idf_list = []
    for t in tf:
        temp = create_tfidf(t, idf_dict)
        temp['Document'] = t.get('Document')
        tf_idf_list.append(temp)
    

    return tf, idf_dict, tf_idf_list





#I just keep adding peoples spotify songs into this dictionary full of songs and the related score
def build_knowledge_base(connection, term_importance_list):
    sia = SentimentIntensityAnalyzer()

    sentences = []
    #scores = []
    weighted_scores = []

    #res = connection.execute('SELECT Count(*) FROM Song')
    #num_rows = int(res.fetchone()[0])
    #print('NUM_ROWS:', num_rows, '\n')

    res = connection.execute('SELECT * FROM Song INNER JOIN Lyrics ON Song.url = Lyrics.url')
    for i, song in enumerate(res.fetchall()):

        lines = song['lyrics']
        sentences = sent_tokenize(lines)

        for sentence in sentences:
            if len(sentences) == 0:
                continue

            tokens = word_tokenize(sentence.lower())
            tokens = [w for w in tokens if w.isalpha() and w not in stopwords.words('english')] #get clean tokens

            tf_idf_weight_multiplyer = 1
            for token in tokens:        #(taken the same way as the function), multiply together term weights to get total sentence importance. Multiply sentence sentiment score by importance per sentence to get more accurate scores
                if token in term_importance_list[i]:
                    tf_idf_weight_multiplyer *= term_importance_list[i].get(token)       #Double check if this is getting the right token
                else:
                    tf_idf_weight_multiplyer *= 1/len(term_importance_list[i])       #Add smoothing here and an if statment for tokens not found #this is bad smooothing

            weighted_scores.append(sia.polarity_scores(sentence)["compound"] * tf_idf_weight_multiplyer)
            #scores.append(sia.polarity_scores(sentence)["compound"])
        
        #total = 0
        weighted_total = 0
        #for score in scores:
            #total += score
        for score in weighted_scores:
            weighted_total += score

        if len(sentences) != 0:     #need this iff statment because some songs are found and files are made but they are instrumentals with no lyrics
            connection.execute('UPDATE Song SET sentiment_Score = ? WHERE url = ?', (weighted_total/len(weighted_scores), song['url']))
            connection.commit()
    #counter = 0
    #for pair in knowledge:
    #    print('\n', pair, ': SENTI SCORE ', knowledge.get(pair))

    

    #print('\n\nKNOWLEDGE BASE\n\n')
    #for pair in knowledge:
    #    print(pair, ' SCORE: ', knowledge.get(pair))


def lyric_recommendation(song_database, song_wanting_recommendation_for, first_time_flag):
    
    dataframe_recommended_song = {}
    error_message = 'Sorry, I could not find that song from your library'
    error_message2 = 'Sorry, the song wasn\'t found in the vectorized database'
    lyrics_row = []


    if len(song_wanting_recommendation_for) == 1:
        answer = song_database.search_user_songs(song_wanting_recommendation_for[0])
        if answer == -1:
            return error_message
        print(answer['name'], ': ', answer['artist'])
        lyrics_row = song_database.get_song_with_lyrics(answer['name'], answer['artist'])
        if lyrics_row == None: #maybe bug found HERE. none lyrics slipping through sql call
            return error_message2

        dataframe_recommended_song['text'] = lyrics_row['lyrics']
        dataframe_recommended_song['artist'] = lyrics_row['artist']
        dataframe_recommended_song['song'] = lyrics_row['name']
        dataframe_recommended_song['link'] = lyrics_row['url']
    elif len(song_wanting_recommendation_for) == 2:
        recommendation_artist = song_wanting_recommendation_for[1]
        answer = song_database.search_user_song_and_artist(song_wanting_recommendation_for[0], recommendation_artist)
        if answer == -1:
            return error_message
        print(answer['name'], ': ', answer['artist'])
        lyrics_row = song_database.get_song_with_lyrics(answer['name'], answer['artist'])
        if lyrics_row == None:
            return error_message2
        dataframe_recommended_song['text'] = lyrics_row['lyrics']
        dataframe_recommended_song['artist'] = lyrics_row['artist']
        dataframe_recommended_song['song'] = lyrics_row['name']
        dataframe_recommended_song['link'] = lyrics_row['url']


    if first_time_flag:

        connection = sqlite3.connect('Songs.db') 
            
        sql_query = pd.read_sql_query ('''
                                SELECT DISTINCT s.url AS link, name AS song, artist, lyrics AS text  FROM Song AS s INNER JOIN Lyrics AS l on s.url = l.url WHERE length(lyrics) > 0
                                ''', connection)

        dfUser = pd.DataFrame(sql_query, columns = ['artist', 'song', 'link', 'text',])
        print ('Your songs as a Panda df!:\n', dfUser)

        dataframe_recommended_song = pd.DataFrame(dataframe_recommended_song, columns = ['artist', 'song', 'link', 'text',], index=[0])
        df = pd.read_csv('spotify_millsongdata.csv')
        df = pd.concat([df, dfUser], ignore_index=True)
        df = pd.concat([dataframe_recommended_song, df], ignore_index=True)
        df.reset_index()
        #print(df.head)
        #maybe don't need this variable
        X = df.text
        #print(X[0])
                            #making max_df high gets rid of stopwords, can play with this variable and ngrams
        vectorizer = TfidfVectorizer(max_df=0.7, ngram_range=(2, 4))
        Xtfid = vectorizer.fit_transform(X)
        
        with open('millTfidVector.pickle', 'wb') as handle:
            pickle.dump(Xtfid, handle)
        with open('pdDataFrame.pickle', 'wb') as handle:
            pickle.dump(df, handle)

    


    with open('millTfidVector.pickle', 'rb') as handle:
        Xtfid = pickle.load(handle)
    with open('pdDataFrame.pickle', 'rb') as handle:
        df = pickle.load(handle)

    #print('#####: ', df.loc[df['link'] == lyrics_row['url']])
    found_index = df.loc[df['link'] == lyrics_row['url']].index.values[0]
    recommendations_found = cosine_similarity(Xtfid[found_index], Xtfid)
    #print(recommendations_found)

    print('\nStdev: ', np.std(recommendations_found))
    stdev = np.std(recommendations_found)
    meanVar = mean(recommendations_found.tolist()[0])
    print('mean: ', meanVar)
    median_value = median(recommendations_found.tolist()[0])
    print('Median: ', median_value, '\n')
    #Uncomment below to see the cosine vector score if you're curious
    topTen = sorted(recommendations_found[0], reverse=True)[2:12]
    #print(topTen)
    recommendations = []
    for i, vector in enumerate(recommendations_found.tolist()[0]):
        if(vector in topTen):
            #print('vec: ', vector)
            recommendations.append([i, vector])
    #print(recommendations)

    index_list = []
    for pair in recommendations:
        index_list.append(pair[0])

    data_recommendations = []
    for rec_index in index_list[0:11]:
        #print(indexRec)
        data_recommendations.append(str(df.iloc[[rec_index]]['song'].values[0] + ': by ' + df.iloc[[rec_index]]['artist'].values[0]))
    
    print('\nTop ten songs based on lyrics:\n')
    for song_rec in data_recommendations:
        print(song_rec, '\n')

    return 'Finished lyric execution Properly'

def setup(databse_songs):
    album_ids = get_spotify_albums()
    album_songs_list = get_all_album_songs(album_ids, databse_songs)
    
    playlist_id_list = get_spotify_playlists()
    playlist_songs_list = get_playlist_songs(playlist_id_list, databse_songs)
    
    saved_songs_list = get_spotify_songs(databse_songs)


    
    new_user_songs = album_songs_list + playlist_songs_list + saved_songs_list
    #generate_lyric_files(databse_songs, new_user_songs)

def main():
    song_db = Songs()
    #setup(song_db)
    
    #SongWantingRecommendationFor = sys.argv[1]  
    #lyric_recommendation(song_db, SongWantingRecommendationFor)
        #artistList = get_spotify_artists(50)
        #print(artistList, '\n', len(artistList))
    
        #albumList = getSpotifyAlbums(50)
        #print(albumList, '\n', len(albumList))
    '''
    AlbumIDList = getSpotifyAlbums()
    albumSongsList = getAlbumSongs(AlbumIDList, song_db)
    
    playlistIDList = get_spotify_playlists()
    playlistSongsList = get_playlist_songs(playlistIDList, song_db)
    
    savedSongsList = get_spotify_songs(song_db)


    
    newUserSongs = albumSongsList + playlistSongsList + savedSongsList
    
    with open('userSongs.pickle', 'wb') as handle:
        pickle.dump(newUserSongs, handle)
    
    with open('userSongs.pickle', 'rb') as handle:
        newUserSongs = pickle.load(handle)

    #pickled and opened because this is a long process and i wanted to test and play with the code-
    #-Without webcrawling and geneerating every run
    #CHECKPOINT

    #generate_lyric_files(song_db, newUserSongs)
    
    #res = con.execute("SELECT * FROM Lyrics")
    #res = con.execute('SELECT COUNT(*) FROM Song')
    #for row in res.fetchall():
    #    print(row['url'], ': ', row['lyrics'], '\n\n')

    
    holdResults = createTF_IDF_TfxIdf(song_db, newUserSongs)
    list_of_tfs = holdResults[0]
    idf_dictionary = holdResults[1]
    tf_idf_list = holdResults[-1]
    

    print('\nPrinting top 25 terms per document:\n\n')

    # find the highest tf-idf terms for each document
    #FOR PRINTING PURPOSES
    for dic in tf_idf_list:             #bottome two lines used for printing purposes but the document name is a string and doesn't compar with floats so i delete it before sorting
        docName = dic.get('Document')
        del dic['Document']
        doc_term_weights = sorted(dic.items(), key=lambda x:x[1], reverse=True)
        #print("\n",docName, ': ', doc_term_weights[:25])
    
    allWords = []
    for dictionary in list_of_tfs:
        allWords += dictionary.keys()
    fd = nltk.FreqDist(allWords)
    print('\n\nMy top 10 terms', fd.most_common(11))
    #Document pops up but it is my palceholder element just to hold the titles of the songs it's not actually the top word

    '''
    
    quit()
    '''
    #build knowledge base
    build_knowledge_base(con, tf_idf_list)
    
    result = con.execute('SELECT * FROM Song')
    for row in result.fetchall():
        print(row['name'], ': ', row['sentiment_Score'])
    
    quit()
    '''
if __name__ == '__main__':
    os.environ["SPOTIPY_CLIENT_ID"] = "PUBLIC_ID"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "SECRET_KEY"
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"

    if len(sys.argv) < 2:
        print('Please enter a song you want recommendations for. (Type \'song_name\' \'song_artist\'(optional))\ne.x \'take me home country road\' \'John Denver\'')
        quit()
    else:
        print('All good, working now...') 
        main()










'''
    Myurl = "https://genius.com/artists/" + artistNameFromInput
    print('\n', Myurl)
    
    soup = get_soup_from_website(Myurl)
    filter_page(soup, 'urls.txt', 'album')

    
    with open('urls.txt', 'r') as f:
        AlbumUrls = f.read().splitlines()

    #Edit: nvm no need to be careful. this code clears the file before a new artist
    open('lyricPages.txt', "w").close()
    for album in AlbumUrls:
        albumSoup = get_soup_from_website(album)
        #print('\nNEW LINE\n')                         #CHANGE ARTIST NAME BELOW THE HASHTAG Edit: changed to sys arg input variable
        filter_page_append(albumSoup, 'lyricPages.txt', artistNameFromInput, 'lyrics')
#'''
