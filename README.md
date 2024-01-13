



# Lyric-based Music Recommendation System
## Project Title: J.O.H.A.N.N (joˈhan)
**Jukebox Orchestrator: a Harmonic Analytics, Navigational Nexus**

## Overview

The Lyric-based Music Recommendation System is a research project aimed at providing personalized music recommendations by analyzing the sentiment of song lyrics. The system utilizes the Spotify API to gather a user's saved songs, web-crawls Genius.com to extract lyrics, and employs sentiment analysis to suggest similar songs with matching emotional tones.

## Table of Contents

- [Background](#background)
- [Design process](#design-process)
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

## Background

With the abundance of music available on streaming platforms like Spotify, users often face the challenge of discovering new songs that align with their emotional preferences. This project addresses this issue by combining data from the Spotify API and Genius.com to create a sentiment-driven music recommendation system.


## Design process
- Current stage of development: 6. Lyrics Extraction and Storage
### 1. Conceptualization

Define the project's objectives, focusing on creating a music recommendation system based on sentiment analysis of song lyrics. Identify the need for a web crawler, sentiment analysis algorithm, and integration with Spotify and Genius.com.

### 2. User Flow

Map out the user flow, starting from connecting their Spotify account to receiving personalized recommendations. Ensure a seamless and user-friendly experience throughout the process.

### 3. Data Flow

Design the data flow architecture to efficiently gather data from both Spotify and Genius.com. Develop a systematic process to handle exceptions, ensuring robust data collection.

### 4. Web Crawler Implementation

Problem - Spotify API does not give access to the lyrics needed for sentiment analysis.\
Solution - Write a web crawler to search for song lyrics based on a given song title and artist. Implement exception handling to retry if a song isn't found. If the song remains inaccessible, log the song and artist details to a file for manual analysis later.

### 5. Spotify API Integration

Develop code to pull data from a user's Spotify playlists, albums they follow, and saved songs. Save the songs to the database. Organize the saved songs into the web crawler, initiating the process of lyrics extraction from Genius.com.

### 6. Lyrics Extraction and Storage

Implement the functionality to parse and save the lyrics returned from Genius.com. Ensure proper storage and organization of the lyrics data for efficient sentiment analysis.\
\
***Work in progress - Keep new line characters for poem-like formatting. This helps ChatGpt in analyzing the Sentiment.***

### 7. Sentiment Analysis

Apply sentiment analysis to the extracted lyrics. Utilize libraries like NLTK for sentiment analysis and scikit-learn to create a vector space, generating similarity values for song comparisons.\
\
***Work in progress - Implement the Openai API to get better sentiment analysis from ChatGPT***

### 8. Recommendation Engine

Based on the similarity values obtained through sentiment analysis, develop a recommendation engine that suggests songs with close similarity values. Create a user-friendly output, presenting recommendations based on emotional tones found in the lyrics.

### 9. Exception Handling and Analysis

Implement comprehensive exception handling throughout the process to ensure the robustness of the system. Log any failed attempts in retrieving lyrics for later manual analysis, allowing continuous improvement of the web crawling process.

### 10. Testing and Refinement

Conduct thorough testing at each stage of the design process.\
***In the future: Refine the recommendation system based on testing results, and iterate as necessary to enhance overall performance and user satisfaction.***

### 11. Documentation

Document the entire design process, including code comments, to facilitate understanding and future development. Provide clear instructions for setting up and running the system


## Features

- **Spotify Integration**: Fetches a user's saved songs from Spotify to create a personalized music library.
- **Lyrics Extraction**: Web-crawls Genius.com to extract lyrics for each song in the library.
- **Sentiment Analysis**: Analyzes the sentiment of song lyrics to determine emotional tones.
- **Recommendation Engine**: Provides personalized song recommendations based on similar sentiment analysis results.

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

## Technologies Used

- Python
- Spotify API
- Beautiful Soup (for web crawling)
- Natural Language Toolkit (NLTK) for sentiment analysis
