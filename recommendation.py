import sys
from songs import Songs
from spot_oath import get_fresh_spotify_client
import pandas as pd
import os
import base64
from openai import OpenAI
from make_cluster_playlists import get_and_save_playlist_image


def is_positive_int(var):
  return var.isdigit() and int(var) > 0 # Should short circuit if not a digit and not throw a type casting error


def get_recommendation_playlist_description(recommendations_summary):
  ai_model = "gpt-3.5-turbo"
  SYSTEM_SETUP = '''
  Synthesize a 3-to-8 word title and 20 word playlist description of the following few paragraphs. Focus on the morals and themes described in the paragraphs. Don't say poem.

  Example output: 
  Title: <3-to-8 word response>
  Description: <20 word response>

  Paragraphs to analyze:
  '''
  client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
  )
  response = client.chat.completions.create(  # Hit api for response
    model= ai_model,
    messages=[
      {"role": "system", "content": SYSTEM_SETUP},
      {"role": "user", "content": recommendations_summary}
    ]
  )

  # Extract the AI output embedding as a list of floats
  text = response.choices[0].message.content
  temp = text.split('\n')
  title = temp[0].split(':')[-1]  # Last element after ':'
  description = temp[1].split(':')[-1]
  playlist_data = {'title': title, 'description': description} # Add to results dict

  return playlist_data

def add_songs_to_recommendation_playlist(spot_ids, playlist_id, spot_client):
  spot_track_prefix = "spotify:track:"
  # Add tracks to the playlist
  track_uris = []
  for id in spot_ids:
    track_uris.append(spot_track_prefix+id)

  # Add tracks to the playlist
  counter = 0
  while len(track_uris) > counter:
    if len(track_uris) > counter and len(track_uris) > (counter + 99):
      spot_client.playlist_add_items(playlist_id, track_uris[counter:(counter+99)])  # 100 song append max (api limit)
    else:
      spot_client.playlist_add_items(playlist_id, track_uris[counter:])
    counter += 99


def make_playlist(recommendation_root_song, recommendations_summary, spot_ids, spot_client):
  playlist_data = {}
  playlist_data = get_recommendation_playlist_description(recommendations_summary)

  # Get the current user's ID
  user_id = spot_client.me()['id']

  # Create a new playlist
  playlist_name = recommendation_root_song['name'] + ": recommendations"
  playlist = spot_client.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_data['description'])
  playlist_id = playlist['id']

  # Add image to playlist
  get_and_save_playlist_image(playlist_data['description'])
  image_path = "ai_image.jpg"
  # Read the image and encode it to base64
  with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

  if sys.getsizeof(encoded_image) < 256000:
    # Upload the image to the playlist
    spot_client.playlist_upload_cover_image(playlist_id, encoded_image)
  else:
    print("Image was too large for playlist")

  add_songs_to_recommendation_playlist(spot_ids, playlist_id, spot_client)
  

def main():
  HELLO = '''
  Hello! Welcome to Johann's lyrics based recommendation generation!

  Here you can type in a song 'Baby' followed by the artist 'Justin Bieber'.
  If the song is in the database, I'll ask for the number of recommendations you'd like.
  Finally, i'll put all the recommendations into a playlist on your spotify!

  Let's get started
  '''

  still_running = True
  db = Songs()
  spot_client = get_fresh_spotify_client(db)
  spot_ids = []
  summaries = []

  print(HELLO)
  while still_running:  # Do while menu loop
    print()
    song_name = input("Enter a song name: ").lower()
    song_artist = input("Enter the songs artist: ").lower()

    song_found = db.find_song_with_name_and_artist(song_name, song_artist)
    if song_found:
      print(f"I found \"{song_found['name']}: {song_found['artist']}\" in the database.")
      is_correct_song = input("Is this the correct song? (yes, no): ").lower()
      if is_correct_song == 'yes':
        playlist_length = 0 # Seems to += input
        playlist_length = input("And how many recommendations would you like in the playlist?: ")
        while not is_positive_int(playlist_length): # Clean user input
          playlist_length = input("Not a positive number. Enter the number of recommendations you'd like: ")

        result_rows = db.get_recommendations(song_found['spot_id'],playlist_length)
        print(result_rows)
        for row in result_rows:
          spot_ids.append(row[2])
          summaries.append(row[3])
        joined_summaries = '\n\n'.join(summaries)
        make_playlist(song_found, joined_summaries, spot_ids, spot_client)

      want_to_retry = input("Would you like another playlist? (yes, no): ")  # Ask to continue 
      if want_to_retry == "no":
        still_running = False
    else:
      want_to_retry = input("Sorry, I couldn't find that song. Would you like to try again? (yes, no): ") # start over and type in song again if the song's not found
      if want_to_retry == "no":
        still_running = False


if __name__ == "__main__":
  main()