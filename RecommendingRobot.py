import os
import sys  # to get the system parameter
import re
import sqlite3
import ssl
import random

from songs import Songs
from WebCrawlSpotify import lyric_recommendation
from WebCrawlSpotify import setup


def random_classifier(song_database):
    song = input('Enter a song (e.x Radioactive by Imagine Dragons): ')

    while len(song) <= 1:
        song = input('Please enter a valid song: ')

    song_data = song.split(" by ")
    song_artist = song_data[0]
    song_title = song_data[1]

    print('you entered: ', song_title, ':', song_artist)

    result = song_database.get_random_rows()
    print('\nHere are some random songs you might like!\n')
    for row in result:
        print(row['name'], ': ', row['artist'])

def category_classifier(song_database):

    categories = ['rock', 'pop', 'disco', 'piano', 'scremo', 'ska', 'jazz']
    #uncomment this block if you're starting the data base from scratch!
    
    #Add arbitraty categories
    # song_database.connection.execute('Update Song SET Category = NULL')
    # all = song_database.get_all_songs()
    # for row in all:
    #     song_database.connection.execute('UPDATE Song SET Category = ? WHERE url = ?', [random.choice(categories), row['url']])
    # song_database.connection.commit()
    
    #Re comment above here
    print('Enter a category for song recommendations:\n\n')
    for cat in categories:
        print(cat)
    
    category = input("Type Category: ").lower()
    result = song_database.get_category_rows(category)
    if result == -1:
        return '\nI couldn\'t find that category\n'

    print('\nHere are some',category, 'songs you might like!\n')
    for row in random.choices(result, k=10):
        print(row['name'], ': ', row['artist'])
    
    return 'Finished category execution Properly'


def lyric_classifier(song_database, first_time_flag):
    song_wanting = input('Please enter a song you want recommendations for: ')
    song_artist_wanting = input('Please enter the artist (type N/A for unknown or unwanted): ')
    lyric_args = []
    
    if song_artist_wanting.lower() == 'n/a':
        lyric_args.append(song_wanting)
    else:
        lyric_args.append(song_wanting)
        lyric_args.append(song_artist_wanting)

    return_message = lyric_recommendation(song_database, lyric_args, first_time_flag)
    print(return_message)




def main():
    song_db = Songs()
    setup(song_db)
    first_time = False

    while True:
        print('Choose how you\'d like your recommendations!\n')
        classifier_choice = input('1. random\n2. by category\n3. by lyrics\n(type 1, 2, or 3): ')
        if classifier_choice == '1':
            random_classifier(song_db)
        elif classifier_choice == '2':
            print(category_classifier(song_db))
        elif classifier_choice == '3':
            lyric_classifier(song_db, first_time)
            first_time = False

        print('\nDo you want another recommendation?')
        keep_playing = input('y/n: ').lower()
        if keep_playing == 'n':
            print('Okay have a good day!')
            break
    quit()


if __name__ == '__main__':
    os.environ["SPOTIPY_CLIENT_ID"] = "PUBLIC_KEY"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "SECRET_KEY"
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"

    main()
