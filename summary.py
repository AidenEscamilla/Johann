import os
import tiktoken
import sys
import time
from anyascii import anyascii
import json
from songs import Songs # my class file
import openai
from openai import OpenAI
from spot_oath import get_fresh_spotify_client


SYSTEM_SETUP = '''
You are a sentiment analysis program used to analyze underlying meanings, emotions, themes, and overarching morals of the poems provided.  When given a poem, format the analysis in a single paragraph with no line breaks and no title or author. 

Example interaction:

- Input: 
I've got some bad, bad news
I can't get over you
I tried 'til my face turned blue
Baby, you got me held down by a string
'Cause you're the only one I see my future with
Buy a happy home and have at least two kids
Stay together longer than my parents did
Is that a stupid wish?
Try to give you a little time
Try to give you a little space
But blasting off into space is taking up all of my breath away
Do you love somebody else or not?
I need the answer quick
The water is running too cold under the bridge to go swimming in
Don't act like you don't feel it too
Don't act like you don't like this bad, bad news
I don't care if I live my whole life confused
I'll be clueless with you
My God, I hate to tell you
All of this bad, bad news
I don't know what to do
But be clueless with you
There you go calling me again past midnight
We've had our battles, brawls and fights
But we made it through World War III
And I just want you here with me
Try to give you a little time
Try to give you a little space
But blasting off into space is taking up all of my breath away
Do you love somebody else or not?
I need the answer quick
The water is running too cold under the bridge to go swimming in
Don't act like you don't feel it too
Don't act like you don't like this bad, bad news
I don't care if I live my whole life confused
I'll be clueless with you
I'll be
I'll be
I'll be clueless
Clueless with you
My God, I hate to tell you
All this bad, bad news

- Output: "The poem is a heartfelt expression of the speaker's deep emotional turmoil and longing for a romantic partner. The speaker is grappling with the pain of unrequited love, as they express their inability to move on from the person they desire. The speaker's feelings are intense and consuming, as they describe feeling held down by a string and unable to breathe due to the overwhelming emotions. The speaker also expresses a desire for a future with this person, envisioning a happy home and a family together. However, the speaker is also aware of the uncertainty and confusion in their relationship, as they question whether their love interest loves somebody else and express frustration with the lack of clarity. Despite the challenges, the speaker is willing to endure the confusion and pain, as they express a willingness to be clueless with the person they love. The poem captures the complexity of love and the deep emotional impact it can have on an individual"
'''

def write_batch_file(database_client, spotify_client):
  embedding_model = "gpt-4o-mini"
  user_id = spotify_client.me()['id']
  songs = database_client.all_user_songs_missing_summaries(user_id)

  if os.path.exists("batch_data.jsonl"):  # Clear file for new batch
    os.remove("batch_data.jsonl")

  song_batches = [songs]
  songs_per_batch = 1800

  if len(songs) > songs_per_batch:
    song_batches = [songs[i:i + songs_per_batch] for i in range(0, len(songs), songs_per_batch)]
  
  for batch in song_batches:
    print(len(batch))
  print("batches total: ", len(song_batches))
  sys.exit(1)

  for song in songs:
    print(f"{song[1]} : {song[2]}")
    url = song[0]
    lyrics = song[3]
    single_request = {
      "custom_id": url,
      "method": "POST",
      "url": "/v1/chat/completions",
      "body": {
        "model": embedding_model,
        "messages": [
          {"role": "system", "content": SYSTEM_SETUP},
          {"role": "user", "content": lyrics}
        ],
        "max_tokens": 1000
      }
    }

    with open("batch_data.jsonl", "a") as f:
      f.write(json.dumps(single_request))
      f.write("\n")

def generate_batch(api_client):
  #Create batch object
  batch_input_file = api_client.files.create(
    file=open("batch_data.jsonl", "rb"),
    purpose="batch"
  )
  #Get id
  batch_input_file_id = batch_input_file.id
  
  #Send off batch to process
  full_batch = api_client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
      "description": "Generate summary of lyrics"
    }
  )
  print(full_batch)

def get_num_tokens(lyric_string: str) -> int:
  embedding_encoding = "cl100k_base"

  encoding = tiktoken.get_encoding(embedding_encoding)
  num_tokens = len(encoding.encode(lyric_string))
  return num_tokens

def check_batch_status(api_client, batch_id, db_client):
  status = 'in_progess'
  while status != "completed":
    try:
      response = api_client.batches.retrieve(batch_id)
      status = response.status
      if status == 'in_progress':
        print('OpenAi is still processing the batch.')
      elif status == 'completed':
        print("Batch complete, saving results...")
        get_and_save_batch_results(api_client, batch_id)
        print("Inserting to database...")
        batch_results = get_batch_responses("batch_results.jsonl") # Takes file_name as argument
        insert_response_summaries(db_client,batch_results)
        break # Don't wont 10 min after finished inserting
      else:
        print("Soemthing went wrong. Take a closer look")
        break # exit while loop
    except openai.NotFoundError as e:
      print(f"The batch_id:{batch_id} was incorrect. Please try again with a correct batch_id")
    time.sleep(600)

def get_and_save_batch_results(api_client, batch_id):
  finished_batch_id = api_client.batches.retrieve(batch_id).output_file_id
  result = api_client.files.content(finished_batch_id).content

  
  result_file_name = "batch_results.jsonl"
  with open(result_file_name, 'wb') as file:
    file.write(result)

def dig_for_response(response_data):
  return response_data.get('response', {}).get('body', {}).get('choices')[0].get('message', {}).get('content')

def get_batch_responses(file_name):
  data = []

  with open(file_name) as response_file:
    for response in response_file:
      formatted_response = {}
      json_response = json.loads(response)
      formatted_response['url'] = json_response.get('custom_id')
      formatted_response['summary'] = dig_for_response(json_response)
      data.append(formatted_response)
    
  return data

def insert_response_summaries(database, responses):
  for response in responses:
    database.insert_summary(response)


def main():
  batch_id = ''
  input_functionality = sys.argv[1]
  if input_functionality == '--check_status' and len(sys.argv) == 3:
    batch_id = sys.argv[-1] # Last arg is the batch id
  
  ai_client = OpenAI(
      # This is the default and can be omitted
      api_key=os.environ.get("OPENAI_API_KEY")
    )
  embedding_model = "gpt-4o-mini"
  db_client = Songs()
  sp_client = get_fresh_spotify_client(db_client)

  if input_functionality == '--check_status': # Most likely
    print("Getting status...")
    check_batch_status(ai_client, batch_id, db_client)
  elif input_functionality == '--generate_batch': # Second likely
    print("Generating batch...")
    write_batch_file(db_client, sp_client)
    generate_batch(ai_client) # Check stdout for the Batch(id='<look here>') and manually copy paste that to BATCH_ID if you can


if __name__ == '__main__':  # Command line flag for desired functionality
  valid_args = ['--generate_batch', '--check_status']
  if len(sys.argv) <= 1:
    print("No arguments provided. Specify '--generate_batch', or '--check_status <BATCH_ID>'")
    exit(1)
  elif sys.argv[1] not in valid_args: # input validation
    print(f"{sys.argv[1]} not a valid argument. Try '--generate_batch', or '--check_status <BATCH_ID>'")
    exit(1)
  elif sys.argv[1] == '--check_status' and len(sys.argv) < 3:
    print("No batch_id included. Correct usage: '--check_status <BATCH_ID_HERE>'")
    exit(1)
  else:
    main()