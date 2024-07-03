
![image (8)](https://github.com/AidenEscamilla/Johann/assets/66649961/4ca99d53-2a6b-480c-aa0f-9ea68668d4b4)



# Lyric-based Music Recommendation System
## Project Title: J.O.H.A.N.N (joˈhan)
**Jukebox Orchestrator: a Harmonic Analytics, Navigational Nexus**

## Overview

The Lyric-based Music Recommendation System is a project aimed at providing personalized music recommendations by analyzing the sentiment of song lyrics. The system utilizes the Spotify API to gather a user's saved songs, web-crawls Genius.com to extract lyrics, and employs GPT sentiment analysis to suggest similar songs with matching emotional tones.

## Table of Contents

- [Background](#background)
- [Design process](#design-process)
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

## Background

Try asking your friends whether they listen to the lyrics or instrumental (beat included) part of a song more. Less often you find people who focus on just the lyrics of a song.

I am one of those people.

With the abundance of music available on streaming platforms like Spotify, users often face the challenge of discovering new songs that align with their lyrical preferences. All the data gathered on songs tends to fall around what the song sounds like, leaving us lyrics searchers in the dark and left out of recommendation algorithms.\
This project addresses the issue by combining data from the Spotify API, Genius.com, and ChatGPT to create a sentiment-driven music recommendation system.


## Design process
- Current stage of development: 6. Lyrics Extraction and Storage
### 1. Conceptualization

Define the project's objectives, focusing on creating a music recommendation system based on sentiment analysis of song lyrics. Identify the need for a web crawler, sentiment analysis algorithm, and integration with Spotify, Genius.com, and ChatGpt.

### 2. User Flow

Map out the user flow, starting from connecting their Spotify account to receiving personalized recommendations. Ensure a seamless and user-friendly experience throughout the process.

### 3. Data Flow

Design the data flow architecture to efficiently gather data from both Spotify and Genius.com. Develop a systematic process to handle exceptions, ensuring robust data collection.

### 4. Web Crawler Implementation

Problem - Spotify API does not give access to the lyrics needed for sentiment analysis.\
Solution - Write a web crawler to search for song lyrics based on a given song title and artist. Implement exception handling to retry if a song isn't found. If the song remains inaccessible, log the song and artist details to a file for manual analysis later.

### 5. Spotify API Integration

Develop code to pull data from a user's Spotify playlists, albums they follow, and saved songs. Save the songs to the database. Pass the saved songs into the web crawler, initiating the process of lyrics extraction from Genius.com.

### 6. Lyrics Extraction and Storage

Implement the functionality to parse and save the lyrics returned from Genius.com. Ensure proper storage and organization of the lyric data for efficient lyrical analysis.

### 7. Sentiment Analysis

Send the lyrics to ChatGpt asking for a 1 paragraph summary of the songs sentiment and store the summary in the database. Send the summary back to ChatGpt to gather embeddings and store the embeddings as a vector in the database.  

### 8. Mapping

Transform the users song embeddings into a 2d map to visualize the clusters. Use clustering algorithms to create clusters of the songs. E.x: Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDB Scan), K-Means, ect. Give each song a cluster label and store that in the database.

### 9. Playlist generation

Based on the cluster label for each song, generate a playlist for the user and put the playlist in their Spotify Library.

### 10. Recommendation Engine

Based on the similarity values obtained through sentiment analysis, develop a recommendation engine that suggests songs with close similarity values. Create a user-friendly output, presenting recommendations based on emotional tones found in the lyrics.

### 11. Exception Handling and Analysis

Implement comprehensive exception handling throughout the process to ensure the robustness of the system. Log any failed attempts in retrieving lyrics for later manual analysis, allowing continuous improvement of the web crawling process.

### 12. Testing and Refinement

Conduct thorough testing at each stage of the design process. Create unit tests for all major functions and processes.

### 13. Documentation

Document the entire design process, including code comments, to facilitate understanding and future development. Provide clear instructions for setting up and running the system


## Features

- **Spotify Integration**: Fetches a user's saved songs from Spotify to create a personalized music library.
- **Lyrics Extraction**: Web-crawls Genius.com to extract lyrics for each song in the library.
- **Sentiment Analysis**: Analyzes the sentiment of song lyrics to determine emotional tones.
- **Playlist Generation**: Generates a playlist title and description based on the cluster of songs.
- **Playlist Picture**: Generates a playlist picture based on the title and description.
- **Recommendation Engine**: Provides personalized song recommendations based on similar sentiment analysis on a single song.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up Spotify API credentials.
3. Run the main program:

   ```bash
   python3 RecommendingRobot.py
   ```

4. Follow on-screen instructions to authenticate Spotify and initiate the recommendation process.

## Tech Stack

**Database:** Postgres

**Program:** Python

## Technologies Used

- Spotify API
- Selenium (for dynamic web crawling)
- Beautiful Soup (for static web crawling)
- Clustering algorithms
- ChatGpt API
