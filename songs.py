import psycopg2
import os

class MockSongs:
    def __init__(self) -> None:
        pass

    def insert_into_not_found(self, songNotFound):                                                    #Maybe prob here
        pass

    def insert_song(self, songDict):
        pass


class Songs:
# conn = psycopg2.connect(database="johann_songs",
#                         host="localhost",
#                         user="postgres",
#                         password="taako",
#                         port="5433")

# cursor = conn.cursor()
# cursor.execute("SELECT * FROM songs")
# print(cursor.fetchall())

# conn.close()
    def __init__(self):
        pg_pass = os.environ['PG_PASS']
        conn = psycopg2.connect(database="johann",
                            host="localhost",
                            user="aidenescamilla",
                            password=pg_pass,
                            port="5432")
        
        self.connection = conn

    def __str__(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs INNER JOIN lyrics on songs.url = lyrics.url LIMIT 1')
        row = cursor.fetchone()
        # returns (songs.url, songs.name, songs.artist, songs.embeddings, lyrics.url, lyrics.lyrics)
        return(str(row[1] + ': ' + row[2]))

    def all_songs_with_lyrics(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT songs.url, name, artist, lyrics FROM songs INNER JOIN lyrics on songs.url = lyrics.url WHERE length(lyrics) > 0')
        return cursor.fetchall()
    
    def all_user_songs_missing_summaries(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, l.lyrics \
                       FROM songs as s \
                       INNER JOIN lyrics as l ON s.url = l.url  \
                       INNER JOIN user_songs as us ON s.url = us.url \
                       LEFT JOIN open_ai_data as oai ON oai.url = s.url \
                       WHERE us.user_id = %s AND length(l.lyrics) > 0 AND oai.summary IS NULL', [user_id])
        return cursor.fetchall()
    

    ##### Search functions
        ##### User search functions

    def search_user_song_by_title(self, user_id, title):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs as s\
                        INNER JOIN user_songs as us\
                        ON s.url = us.url \
                        WHERE us.user_id = %s AND name LIKE %s', [user_id,title])
        result = cursor.fetchone()

        if result == None:
            half_input = title[:int(len(title)/2)]
            psql_formatted_half_input = "%"+half_input+"%"
            cursor.execute('SELECT * \
                           FROM songs as s \
                           INNER JOIN user_songs as us ON url \
                           WHERE us.user_id = %s AND name ILIKE %s',[user_id, psql_formatted_half_input])
            result = cursor.fetchone()
        
        if result == None:
            return -1
        else:
            result_dict = {
                'url' : result[0],
                'name' : result[1],
                'artist' : result[2]
            }
            return result_dict
    
    def search_user_song_by_title_and_artist(self, user_id, title, artist):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * \
                       FROM songs as s \
                       INNER JOIN user_songs as us ON s.url = us.url \
                       WHERE us.user_id = %s AND name ILIKE %s AND artist ILIKE %s', [user_id, title, artist])
        result = cursor.fetchone()

        if result == None:
            half_input = title[:int(len(title)/2)]
            cursor.execute('SELECT * \
                           FROM songs as s\
                           INNER JOIN user_songs as us ON s.url = us.url \
                           WHERE us.user_id = %s AND s.name ILIKE %s AND s.artist ILIKE %s',[user_id,'%'+half_input+'%', artist])
            result = cursor.fetchone()
        
        if result == None:  # If still no result
            return -1
        else:
            result_dict = {
                'url' : result[0],
                'name' : result[1],
                'artist' : result[2],
                'embedding' : result[3]
            }
            return result_dict
        

        ##### Database search functions

    def is_song_in_database(self, search_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * \
                       FROM songs as s \
                       WHERE s.spot_id = %s OR (s.name = %s AND s.artist = %s)', [search_dict['spot_id'], search_dict['name'], search_dict['artist']])
        song_result = cursor.fetchone()

        cursor.execute('SELECT * \
                       FROM not_found as nf \
                       WHERE nf.spot_id = %s', [search_dict['spot_id']])
        not_found_result = cursor.fetchone()


        if (song_result or not_found_result):
            return True
        else:
            return False
        
    def is_song_in_not_found(self, search_dict):
        cursor = self.connection.cursor()

        cursor.execute('SELECT * \
                       FROM not_found as nf \
                       WHERE nf.spot_id = %s OR (nf.name = %s AND nf.artist = %s)', [search_dict['spot_id'], search_dict['name'], search_dict['artist']])
        not_found_result = cursor.fetchone()

        if not_found_result:
            return True
        else:
            return False


    def find_song_with_name_artist_and_lyrics(self, title, artist):
        cursor = self.connection.cursor()
        cursor.execute('SELECT lyrics.lyrics, songs.artist, songs.name, songs.url \
                        FROM songs INNER JOIN lyrics on songs.url = lyrics.url \
                        WHERE name ILIKE %s AND artist ILIKE %s AND length(lyrics) > 0', (title, artist,))
        result = cursor.fetchone()

        if len(result) >= 4:
            result_dict = {
                    'lyrics' : result[0],
                    'artist' : result[1],
                    'name' : result[2],
                    'url' : result[3]
                }
        else:
            result_dict = None

        return result_dict
    
    def find_song(self, search_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * \
                        FROM songs \
                        WHERE spot_id = %s OR (name = %s AND artist = %s)', 
                        [search_dict['spot_id'], search_dict['name'], search_dict['artist']])
        result = cursor.fetchone()

        if len(result) >= 4:
            result_dict = {
                    'url' : result[0],
                    'name' : result[1],
                    'artist' : result[2],
                    'spot_id' : result[3]
                }
        else:
            result_dict = None

        return result_dict
    
    '''
    Probably depriciated
    '''
    def find_song_with_name_and_artist(self, name, artist):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs WHERE name = %s AND artist = %s', [name, artist])
        result = cursor.fetchone()
        return result

    def find_song_by_spot_id(self, spot_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs WHERE spot_id = %s', [spot_id])
        result = cursor.fetchone()

        if len(result) >= 4:
            result_dict = {
                    'url' : result[0],
                    'name' : result[1],
                    'artist' : result[2],
                    'spot_id' : result[3]
                }
        else:
            result_dict = None

        return result_dict
    
    #### Database fetch functions

    def get_random_rows(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs ORDER BY RANDOM() LIMIT 5')
        result = cursor.fetchall()
        return result
    
    def get_all_songs(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM songs')
        result = cursor.fetchall()
        return result
    
    def get_random_song_with_lyrics(self, limit):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, l.lyrics, s.embedding \
                       FROM songs as s \
                       INNER JOIN lyrics as l ON s.url = l.url \
                       WHERE LENGTH(l.lyrics) > 0 \
                       ORDER BY random() \
                       LIMIT %s::integer', [limit])
        results = cursor.fetchall()
        return results
    
    def get_all_embeddings(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, oai.embedding \
                        FROM songs as s \
                        INNER JOIN open_ai_data as oai \
                        ON s.url = oai.url  \
                        WHERE embedding IS NOT NULL')
        results = cursor.fetchall()
        return results
    
    def get_all_summary_embeddings(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, oai.summary_embedding \
                        FROM songs as s \
                        INNER JOIN open_ai_data as oai \
                        ON s.url = oai.url  \
                        WHERE summary_embedding IS NOT NULL')
        results = cursor.fetchall()
        return results
    
    def get_all_user_summary_embeddings(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, oai.summary_embedding, oai.summary \
                        FROM songs as s \
                        INNER JOIN user_songs as us ON s.url = us.url\
                        INNER JOIN open_ai_data as oai ON s.url = oai.url  \
                        WHERE us.user_id = %s AND summary_embedding IS NOT NULL', [user_id])
        results = cursor.fetchall()
        return results
    
    def get_all_song_summaries(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.url, s.name, s.artist, oai.summary \
                        FROM songs as s \
                        INNER JOIN open_ai_data as oai \
                        ON s.url = oai.url  \
                        WHERE summary IS NOT NULL AND summary_embedding IS NULL')
        results = cursor.fetchall()
        return results
    
    def get_song_openai_data(self, url):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * \
                        FROM open_ai_data as oai \
                        WHERE url = %s', [url])
        results = cursor.fetchone()
        return results
    

    def get_oath_token(self, access_token):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * \
                        FROM oath_flow \
                        WHERE access_token = %s', [access_token])
        result = cursor.fetchone()

        if len(result) == 7:
            result_dict = {
                    # Skip [0] because it's the user_id
                    'access_token' : result[1],
                    'token_type' : result[2],
                    'expires_in' : result[3],
                    'scope' : result[4],
                    'expires_at' : result[5],
                    'refresh_token' : result[6],
                }
        else:
            result_dict = None

        return result_dict
    
    def get_all_user_cluster_songs(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT s.spot_id, oai.summary, s.cluster \
                        FROM songs as s \
                        INNER JOIN user_songs as us ON s.url = us.url \
                        INNER JOIN open_ai_data as oai ON s.url = oai.url \
                        WHERE us.user_id = %s AND s.cluster IS NOT NULL', [user_id])
        results = cursor.fetchall()

        return results
    
    def get_user_cluster_info(self, user_id, cluster_number):
        cursor = self.connection.cursor()
        cursor.execute('SELECT title, description \
                        FROM cluster_info \
                        WHERE user_id = %s AND cluster = %s', [user_id, cluster_number])
        result = cursor.fetchone()

        if len(result) == 2:
            result_dict = {
                    'title' : result[0],
                    'description' : result[1],
                }
        else:
            result_dict = None

        return result_dict
    
    
    ##### Insert functions
    def insert_user(self, user_id, user_display_name):
        cursor = self.connection.cursor()

        # Note user_id is not getting updated because on conflict I don't think we should change the user
        cursor.execute('INSERT INTO spotify_user(user_id, display_name) \
                        VALUES(%s, %s) \
                        ON CONFLICT(user_id) DO UPDATE SET \
                        display_name = EXCLUDED.display_name', [user_id, user_display_name])

        self.connection.commit()

    def insert_user_song(self, user_id, song_url):
        cursor = self.connection.cursor()

        # Note user_id is not getting updated because on conflict I don't think we should change the user. Url's may change over time (but really shouldn't)
        cursor.execute('INSERT INTO user_songs(user_id, url) \
                        VALUES(%s, %s) \
                        ON CONFLICT(user_id, url) DO UPDATE SET \
                        url = EXCLUDED.url', [user_id, song_url])

        self.connection.commit()

    def insert_oath_token(self, oath_token):
        cursor = self.connection.cursor()
        row_info = [oath_token['user_id'], oath_token['access_token'], oath_token['refresh_token'], \
                    oath_token['token_type'], oath_token['scope'], oath_token['expires_in'], \
                    oath_token['expires_at']
                ]

        mogrified_query = cursor.mogrify('INSERT INTO oath_flow(user_id, access_token, refresh_token, token_type, scope, expires_in, expires_at) \
                        VALUES(%s, %s, %s, %s, %s, %s, %s) \
                        ON CONFLICT(user_id) DO UPDATE SET \
                        user_id = EXCLUDED.user_id, \
                        access_token = EXCLUDED.access_token, \
                        refresh_token = EXCLUDED.refresh_token, \
                        token_type = EXCLUDED.token_type, \
                        scope = EXCLUDED.scope, \
                        expires_in = EXCLUDED.expires_in, \
                        expires_at = EXCLUDED.expires_at', row_info)
        cursor.execute(query=mogrified_query)

        self.connection.commit()

    def insert_song(self, songDict):
        cursor = self.connection.cursor()
        row_info = (songDict['url'], songDict['name'], songDict['artist'], songDict['spot_id'])

        cursor.execute('INSERT INTO songs(url, name, artist, spot_id) \
                        VALUES(%s, %s, %s, %s) \
                        ON CONFLICT(url) DO UPDATE SET \
                        url = EXCLUDED.url, \
                        name = EXCLUDED.name, \
                        artist = EXCLUDED.artist, \
                        spot_id = EXCLUDED.spot_id', row_info)

        self.connection.commit()

    def insert_embedding(self, embedding_dict):
        cursor = self.connection.cursor()

        cursor.execute('INSERT INTO open_ai_data(url, embedding) \
                        VALUES(%s, %s) \
                        ON CONFLICT(url) DO UPDATE SET \
                        embedding = EXCLUDED.embedding', [embedding_dict['url'], embedding_dict['embedding']])

        self.connection.commit()
    
    def insert_summary_embedding(self, embedding_dict):
        cursor = self.connection.cursor()

        cursor.execute('INSERT INTO open_ai_data(url, summary_embedding) \
                        VALUES(%s, %s) \
                        ON CONFLICT(url) DO UPDATE SET \
                        summary_embedding = EXCLUDED.summary_embedding', [embedding_dict['url'], embedding_dict['embedding']])

        self.connection.commit()

    def insert_summary(self, summary_dict):
        cursor = self.connection.cursor()

        cursor.execute('INSERT INTO open_ai_data(url, summary) \
                        VALUES(%s, %s) \
                        ON CONFLICT(url) DO UPDATE SET \
                        summary = EXCLUDED.summary', [summary_dict['url'], summary_dict['summary']])

        self.connection.commit()

    def add_cluster_to_song(self, url, cluster_number):
        cursor = self.connection.cursor()

        cursor.execute('INSERT INTO songs(url, cluster) \
                       VALUES(%s, %s) \
                       ON CONFLICT(url) DO UPDATE SET \
                       cluster = EXCLUDED.cluster', [url, cluster_number])
        
        self.connection.commit()

    def clear_user_cluster_info(self, user_id):
        cursor = self.connection.cursor()

        # Clear all cluster info already in db
        cursor.execute('DELETE FROM cluster_info WHERE user_id = %s', [user_id])
        self.connection.commit()

    def insert_user_cluster_info(self, user_id, cluster_number, playlist_data):
        cursor = self.connection.cursor()

        cursor.execute('INSERT INTO cluster_info(user_id, cluster, title, description) \
                        VALUES(%s, %s, %s, %s) \
                        ON CONFLICT(user_id, cluster) DO UPDATE SET \
                        title = EXCLUDED.title, \
                        description = EXCLUDED.description', [user_id, cluster_number, playlist_data['title'], playlist_data['description']])

        self.connection.commit()


    ''' Takes a dict {url : url-example.com, lyrics : 'These are cool lyrics'}'''
    def insert_into_lyrics(self, lyrics_and_url):
        cursor = self.connection.cursor()

        row_info = (lyrics_and_url['url'], lyrics_and_url['lyrics'])
        cursor.execute('INSERT INTO lyrics(url, lyrics) \
                        VALUES(%s, %s)\
                        ON CONFLICT(url) DO UPDATE SET\
                        url = EXCLUDED.url, \
                        lyrics = EXCLUDED.lyrics', row_info)

        self.connection.commit()

    ''' Takes a dict {url : 'url-example.com', error : 'BrokenCodeError', name : song_title, artist : artist_name}'''
    def insert_into_not_found(self, song_not_found):
        cursor = self.connection.cursor()
        row_info = (song_not_found['url'], song_not_found['name'], song_not_found['artist'], song_not_found['error'], song_not_found['spot_id'])
        cursor.execute('INSERT INTO not_found(url, name, artist, error, spot_id) \
                        VALUES( %s,  %s,  %s,  %s, %s) \
                        ON CONFLICT(url) DO UPDATE SET \
                        url = EXCLUDED.url, \
                        name = EXCLUDED.name, \
                        artist = EXCLUDED.artist, \
                        error = EXCLUDED.error, \
                        spot_id = EXCLUDED.spot_id', row_info)
        self.connection.commit()
        print("INSERTED")
        



# if __name__ == '__main__':
    # test = songs()
    # test.__str__()
    # results = test.search_user_song_by_title('show')
    # print(results)
    # results = test.search_user_song_by_title_and_artist('call your ', 'Noah Kahan')
    # print(results)
    # print(test.find_song_with_name_artist_and_lyrics('Call your mom','noah Kahan'))
    # print(test.get_random_rows())
    # print(test.get_all_songs())
    # print(test.find_song_with_name_and_artist('shower song','fredo disco'))
    # info = {
    #     'url' : 'https://genius.com/the-backseat-lovers-growingdying-lyrics',
    #     'name'  : 'Growing/Dying',
    #     'artist' : 'The Backseat Lovers'
    # }
    # test.insert_song(info)

    # test.insert_into_lyrics({ 'url' : 'https://genius.com/noah-kahan-call-your-mom-lyrics', 
    #     'lyrics' : '''Oh, you're spiralin' again. The moment right before it ends you're most afraid of. But don't you cancel any plans. Because I won't let you get the chance to never make them. Stayed on the line with you the entire night. Til you let it out and let it in. Don't let this darkness fool you. All lights turned off can be turned on. I'll drive, I'll drive all night. I'll call your mom. Oh, dear,\
    #         don't be discouraged. I've been exactly where you are. I'll drive, I'll drive all night. I'll call your mom. I'll call your mom. Waiting room, no place to stand. Just greatest fears and wringing hands and the loudest silence. If you could see yourself like this. If you could see yourself like this, you'd've never tried it. Stayed on the line with you the entire night. Til you told me that you had to go. \
    #         Don't let this darkness fool you. All lights turned off can be turned on. I'll drive, I'll drive all night. I'll call your mom. Oh, dear, don't be discouraged. I've been exactly where you are. I'll drive, I'll drive all night. I'll call your mom. Medicate, meditate, swear your soul to Jesus. Throw a punch, fall in love, give yourself a reason. Don't want to drive another mile wonderin' if you're breathin. So won't you stay, won't you stay, won't you stay with me?.\
    #         Medicate, meditate, save your soul for Jesus. Throw a punch, fall in love, give yourself a reason. Don't want to drive another mile without knowin' you're breathin. So won't you stay, won't you stay, won't you stay with me?. Don't let this darkness fool you. All lights turned off can be turned on. I'll drive, I'll drive all night. I'll call your mom. Oh, dear, don't be discouraged. \
    #         I've been exactly where you are. I'll drive, I'll drive all night. I'll call your mom. I'll call your mom'''})
    # not_found_test = {
    #     'url' : 'https://genius.com/the-backseat-lovers-growingdying-lyrics',
    #     'name' : 'Growing/Dying',
    #     'artist' : 'The Backseat Lovers',
    #     'error' : 'urllib.error.HTTPError'
    # }
    # test.insert_into_not_found(not_found_test)