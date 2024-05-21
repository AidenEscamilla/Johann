import random

from songs import Songs
from WebCrawlSpotify import lyric_recommendation
from WebCrawlSpotify import setup
from spot_oath import create_oath_token


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

'''
Probably depriciated and broken
'''
def lyric_classifier(song_database, first_time_flag, spot_client):
    sp_objects = create_oath_token(song_database)
    sp_client = sp_objects['client']
    sp_oath = sp_objects['oath']

    song_wanting = input('Please enter a song you want recommendations for: ')
    song_artist_wanting = input('Please enter the artist (type N/A for unknown or unwanted): ')
    lyric_args = []
    
    if song_artist_wanting.lower() == 'n/a':
        lyric_args.append(song_wanting)
    else:
        lyric_args.append(song_wanting)
        lyric_args.append(song_artist_wanting)

    return_message = lyric_recommendation(song_database, lyric_args, first_time_flag, sp_client)
    print(return_message)




def main():
    song_db = Songs()
    setup(song_db)
    first_time = False

    while True:
        print('Choose how you\'d like your recommendations!\n')
        classifier_choice = input('1. random\n2. by lyrics\n(type 1, or 2): ')
        if classifier_choice == '1':
            random_classifier(song_db)
        elif classifier_choice == '2':
            lyric_classifier(song_db, first_time)
            first_time = False

        print('\nDo you want another recommendation?')
        keep_playing = input('y/n: ').lower()
        if keep_playing == 'n':
            print('Okay have a good day!')
            break
    quit()


if __name__ == '__main__':
    main()
