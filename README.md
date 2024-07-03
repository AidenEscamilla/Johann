
![image (8)](https://github.com/AidenEscamilla/Johann/assets/66649961/4ca99d53-2a6b-480c-aa0f-9ea68668d4b4)


# Lyric-based Music Recommendation System 🎵

## Project Title: **J.O.H.A.N.N** (joˈhan)
**Just One Hip Algorithm for Navigating Narratives**

---

## Overview

The Lyric-based Music Recommendation System, J.O.H.A.N.N, aims to provide personalized music recommendations by analyzing the sentiment of song lyrics. Utilizing the Spotify API to gather a user's saved songs, web-crawling Genius.com to extract lyrics, and employing GPT sentiment analysis, the system suggests songs with matching emotional tones.

---

## Table of Contents

- [Background](#background)
- [Design Process](#design-process)
- [Features](#features)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

---

## Background

Have you ever wondered whether your friends pay more attention to the lyrics or the instrumental part of a song? Many focus on the beat, leaving lyric enthusiasts like me in the dark when it comes to recommendation algorithms. This project addresses that gap by creating a sentiment-driven music recommendation system that combines data from the Spotify API, Genius.com, and ChatGPT.

---

## [Design Process](https://github.com/AidenEscamilla/Johann/wiki/Design-1.0) 🛠️

**Current stage of development:** 
- 12 & 13. Tests & Documentation

---

## Features

- **Spotify Integration**: Fetches a user's saved songs from Spotify to create a personalized music library. 🎧
- **Lyrics Extraction**: Web-crawls Genius.com to extract lyrics for each song in the library.
- **Sentiment Analysis**: Analyzes the sentiment of song lyrics to determine emotional tones. ❤️
- **Playlist Generation**: Generates a playlist title and description based on the cluster of songs.
- **Playlist Picture**: Generates a playlist picture based on the title and description.
- **Recommendation Engine**: Provides personalized song recommendations based on similar sentiment analysis on a single song. 🔍

---

## Usage

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set up Spotify API credentials:**
   - Visit the [Spotify Developers page](https://developer.spotify.com/). Create an account, a project (Spotify calls it an 'app'), and find the client ID & client secret in 'settings'.

3. **Set up Postgres:**
   - Use the provided [schema file](https://github.com/AidenEscamilla/Johann/blob/9157c778074503d705f5e2c29c608d1a36a3fa64/schema.sql).

4. **Set up .env file:**
   - Follow the instructions in the [.env file](https://github.com/AidenEscamilla/Johann/blob/2176460b0202e98336e1d181f470626782e2b273/.env).

5. **Run the webcrawler:**
   ```bash
   python3 webcrawl_lyrics.py
   ```

6. **Authenticate Spotify and initiate the recommendation process:**
   - Follow the on-screen instructions.

7. **Run the summary making program:**
   ```bash
   python3 summary.py --generate_batch
   ```
   - Check the status at any time:
   ```bash
   python3 summary.py --check_status
   ```
   - Note: This checks status every 10 min. Use 'ctrl+c' to stop manually.

8. **Run the embeddings:**
   ```bash
   python3 embeddings.py
   ```

9. **Run the mapping with HDB or K-Means:**
   ```bash
   python3 mapping.py --dense <CLUSTER_MIN_SIZE_INT> <CLUSTER_MIN_SAMPLES_INT>
   ```
   - Example:
   ```bash
   python3 mapping.py --dense 10 4
   ```
   - Note: Run multiple times to dial in the right clusters.

11. **Create the playlists:**
   ```bash
   python3 make_cluster_playlists.py
   ```

---

## Tech Stack

**Database:** Postgres 🗄️

**Program:** Python 🐍

---

## Technologies Used

- Spotify API 🎵
- Selenium (for dynamic web crawling) 🌐
- Beautiful Soup (for static web crawling) 🍲
- Clustering algorithms 📊
- ChatGPT API 🤖
