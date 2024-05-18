import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from ast import literal_eval
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import hdbscan
import sys
from songs import Songs # my class file

def get_dataframe(song_db, df):
  urls = []
  names = []
  artists = []
  embeddings = []

  results = song_db.get_all_summary_embeddings()
  for song in results:  # format all song info for df
    urls.append(song[0])
    names.append(song[1])
    artists.append(song[2])
    embeddings.append(song[3])

  # Add song info to df
  df['url'] = urls
  df['name'] = names
  df['artist'] = artists
  df['embedding'] = embeddings
  print(df.head()) # Check dataframe
  return df

def add_reduced_dimensions_to_df(df):
  # Instantiate tsne, specify cosine distance
  tsne = TSNE(random_state = 0, n_iter = 1000, metric = 'cosine')

  matrix = np.array(df.embedding.apply(literal_eval).to_list())  # Format embeddings for function
  vis_dims = tsne.fit_transform(matrix) # fit & transform embeddings, reduce to 2-dimensions

  # put x and y into the df
  df['x'] = vis_dims[:,0]
  df['y'] = vis_dims[:,1]
  print(df.head()) # Check dataframe
  return df

# Great at finding patterns & similarity, good at specific playlists 
def add_density_cluster_labels_to_df(df):
  mapped_embedings = df[['x','y']] # Format for function
  scaler = StandardScaler()
  scaled_data = scaler.fit_transform(mapped_embedings)  #normalize data
  # clusterer = hdbscan.HDBSCAN(min_cluster_size=4, min_samples = 2) # this is really good for tiny clusters
  clusterer = hdbscan.HDBSCAN(min_cluster_size=25, min_samples = 6) # playlist cluster parameters
  cluster_labels = clusterer.fit_predict(mapped_embedings)  # predict clusters

  # print number of clusters
  num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
  print(f'Number of clusters: {num_clusters}')

  # Put cluster label to df
  df['cluster'] = cluster_labels
  return df

# Way better for general categorizing of songs. Good for vibe playlists
def add_kmeans_cluster_labels_to_df(df):
  mapped_embedings = df[['x','y']] # Format for function
  scaler = StandardScaler()
  scaled_data = scaler.fit_transform(mapped_embedings)  #normalize data

  kmeans = KMeans(n_clusters=7, random_state=42)  # Setting random_state to ensure reproducibility
  cluster_labels = kmeans.fit_predict(scaled_data)

  # Put cluster label to df
  df['cluster'] = cluster_labels
  return df

def add_cluster_labels_to_database(labeled_df, database_client):
  print("Hello")


def display_plots(df):
  # Set figsize of plots
  fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,8))
  ax1.scatter(df.x, df.y, alpha=.3) # Scatter points, set alpha low to make points translucent
  ax1.set_title('Scatter plot of song embeddings using t-SNE')  # Set title

  # Make cluster graph
  ax2.scatter(df['x'], df['y'], c=df['cluster'], cmap='rainbow')
  ax2.set_xlabel('Feature 1')
  ax2.set_ylabel('Feature 2')
  ax2.set_title('HDBSCAN Clusters')
  plt.show()  # Display



def main():
  db_client = Songs()
  embeddings_df = pd.DataFrame()

  embeddings_df = get_dataframe(db_client, embeddings_df)
  embeddings_df = add_reduced_dimensions_to_df(embeddings_df)
  embeddings_df = add_density_cluster_labels_to_df(embeddings_df)
  # embeddings_df = add_kmeans_cluster_labels_to_df(embeddings_df)


  add_cluster_labels_to_database(embeddings_df, db_client)
  display_plots(embeddings_df)


if __name__ == '__main__':
  main()