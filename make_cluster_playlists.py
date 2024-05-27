import pandas as pd
from songs import Songs
import spotipy
from spot_oath import get_fresh_spotify_client

#For image generation & manipulation
from openai import OpenAI
import base64
import requests
from PIL import Image 
from io import BytesIO
import sys



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

def get_and_save_playlist_image(playlist_description):
  ai_client = OpenAI()
  # Get image from api
  try:
    response = ai_client.images.generate(
      model="dall-e-2",
      prompt="A "+ playlist_description +" WITH NO WORDS ON THE PICTURE. Follow all content safety rules",
      size="512x512",
      quality="standard",
      response_format="url",
      n=1,
    )
  except openai.BadRequestError as e:
    print("OpenAi error: ", e)
    print("No image :()")
    return None


  image_url=response.data[0].url # get response url

  # Download the image
  headers = {'User-Agent': 'AppleWebKit/537.36'}
  image_response = requests.get(image_url, headers=headers)
  # Open the image using PIL
  image = Image.open(BytesIO(image_response.content))
  # Resize the image to Spotify's recommended resolution (640x640 pixels)
  image = image.resize((300, 300), Image.LANCZOS)
  image.save("ai_image.jpg", format='JPEG', quality=95)

  return True #If valid image creation, return true, 1, ect., else return None

def create_cluster_playlist(songs_to_add, playlist_info, spotify_client):
    spot_track_prefix = "spotify:track:"

    # Get the current user's ID
    user_id = spotify_client.me()['id']

    # Create a new playlist
    playlist = spotify_client.user_playlist_create(user=user_id, name=playlist_info['title'], public=True, description=playlist_info['description'])
    playlist_id = playlist['id']

    # Add image to playlist
    image_created = get_and_save_playlist_image(playlist_info['description'])
    if image_created:
      image_path = "ai_image.jpg"
      # Read the image and encode it to base64
      with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

      if sys.getsizeof(encoded_image) < 256000:
        # Upload the image to the playlist
        spotify_client.playlist_upload_cover_image(playlist_id, encoded_image)
      else:
        print("Image was too large for playlist")

    # Add tracks to the playlist
    track_uris = []
    for song in songs_to_add:
      track_uris.append(spot_track_prefix+song['spot_id'])

    # Add tracks to the playlist
    counter = 0
    while len(track_uris) > counter:
      if len(track_uris) > counter and len(track_uris) > (counter + 99):
        spotify_client.playlist_add_items(playlist_id, track_uris[counter:(counter+99)])  # 100 song append max (api limit)
      else:
        spotify_client.playlist_add_items(playlist_id, track_uris[counter:])
      counter += 99

def make_playlists(user_cluster_df, db_client, spot_client):
  user_id = spot_client.me()['id']
  cluster_labels = set(user_cluster_df['cluster'].to_list())
  if -1 in cluster_labels:
    cluster_labels.remove(-1) # Remove noise points

  for cluster in cluster_labels:
    cluster_songs = user_cluster_df[user_cluster_df['cluster'] == cluster]
    playlist = []
    playlist = get_cluster_songs(cluster_songs)
    playlist_info = db_client.get_user_cluster_info(user_id, cluster)
    create_cluster_playlist(playlist, playlist_info, spot_client)

def main():
  db_client = Songs()
  user_cluster_df = pd.DataFrame()
  spot_client = get_fresh_spotify_client(db_client)

  user_cluster_df = get_user_cluster_dataframe(db_client, user_cluster_df, spot_client) # Pass df by reference might be worth it here
  make_playlists(user_cluster_df, db_client, spot_client)
  






if __name__ == '__main__':
  main()