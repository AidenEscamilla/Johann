import pandas as pd
from mapping import get_dataframe, add_reduced_dimensions_to_df, add_density_cluster_labels_to_df
from songs import Songs
import spotipy
from spot_oath import get_fresh_spotify_client



def get_user_cluster_dataframe(db_client, cluster_df, spotify_client):
  user_id = spotify_client.me()['id']
  spot_ids = []
  summaries = []
  cluster_number = []

  results = db_client.get_all_user_cluster_songs(user_id)

  for song in results:  # format all song info for df
    spot_ids.append(song[0])
    summaries.append(song[1])
    cluster_number.append(song[2])


  # Add song info to df
  cluster_df['spot_id'] = spot_ids
  cluster_df['summary'] = summaries
  cluster_df['cluster'] = cluster_number
  print(cluster_df.head()) # Check dataframe
  return cluster_df


def get_cluster_songs(cluster_songs_df):
  songs = []
  for index in cluster_songs_df.index:
    spot_id = cluster_songs_df['spot_id'][index]
    summary = cluster_songs_df['summary'][index]

    songs.append({'summary': summary, 'spot_id': spot_id}) # temp not in here

  return songs


def create_cluster_playlist(songs_to_add, cluster_number, spotify_client):
    scope = "playlist-modify-public"
    spot_track_prefix = "spotify:track:"

    # Get the current user's ID
    user_id = spotify_client.me()['id']

    # Create a new playlist
    playlist_name = f"Cluster playlist #{cluster_number}"
    playlist_description = "This is a new playlist created with Spotipy"
    playlist = spotify_client.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)
    playlist_id = playlist['id']

    # Add tracks to the playlist
    track_uris = []
    for song in songs_to_add:
      track_uris.append(spot_track_prefix+song['spot_id'])
    print(len(track_uris))

    # Add tracks to the playlist
    counter = 0
    while len(track_uris) > counter:
      if len(track_uris) > counter and len(track_uris) > (counter + 99):
        spotify_client.playlist_add_items(playlist_id, track_uris[counter:(counter+99)])  # 100 song append max (api limit)
      else:
        spotify_client.playlist_add_items(playlist_id, track_uris[counter:])
      counter += 99

def make_playlists(user_cluster_df, spot_client):
  cluster_labels = set(user_cluster_df['cluster'].to_list())

  for cluster in cluster_labels:
    cluster_songs = user_cluster_df[user_cluster_df['cluster'] == cluster]
    playlist = []
    playlist = get_cluster_songs(cluster_songs)
    create_cluster_playlist(playlist, int(cluster), spot_client)

def main():
  db_client = Songs()
  user_cluster_df = pd.DataFrame()
  spot_client = get_fresh_spotify_client(db_client)

  user_cluster_df = get_user_cluster_dataframe(db_client, user_cluster_df, spot_client) # Pass df by reference might be worth it here
  make_playlists(user_cluster_df, spot_client)
  






if __name__ == '__main__':
  main()