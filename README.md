
![image (8)](https://github.com/AidenEscamilla/Johann/assets/66649961/4ca99d53-2a6b-480c-aa0f-9ea68668d4b4)



# Lyric-based Music Recommendation System
## Project Title: J.O.H.A.N.N (joˈhan)
**Jukebox Orchestrator: a Harmonic Analytics, Navigational Nexus**

## Overview

The Lyric-based Music Recommendation System is a project aimed at providing personalized music recommendations by analyzing the sentiment of song lyrics. The system utilizes the Spotify API to gather a user's saved songs, web-crawls Genius.com to extract lyrics, and employs GPT sentiment analysis to suggest similar songs with matching emotional tones.

## Table of Contents

- [Background](#background)
- [Design process]([#design-process](https://github.com/AidenEscamilla/Johann/wiki/Design-1.0))
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

## Background

Try asking your friends whether they listen to the lyrics or instrumental (beat included) part of a song more. Less often you find people who focus on just the lyrics of a song.

I am one of those people.

With the abundance of music available on streaming platforms like Spotify, users often face the challenge of discovering new songs that align with their lyrical preferences. All the data gathered on songs tends to fall around what the song sounds like, leaving us lyrics searchers in the dark and left out of recommendation algorithms.\
This project addresses the issue by combining data from the Spotify API, Genius.com, and ChatGPT to create a sentiment-driven music recommendation system.


## [Design process](https://github.com/AidenEscamilla/Johann/wiki/Design-1.0)
- Current stage of development: 12 & 13. Tests & Documentation


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
