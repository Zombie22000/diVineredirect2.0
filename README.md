<p align="center">
  <img src="divineredirect-logo-green.png" alt="diVineredirect logo green">
</p>

---

## Installation

### System Requirements
- Windows 8.1 or later
- [Python](https://www.python.org/)
- [FFmpeg n5.1.6 win64 gpl 5.1](https://github.com/BtbN/FFmpeg-Builds/releases?page=4)

### Setup Steps

1. **Install Python Dependencies**
   ```bash
   pip install flask requests websocket-client
   ```

2. **Organize Your Files**
   - Extract the diVineredirect release zip (v2.1+) or place `main.py` in a new folder (v2.0)
   - Place your FFmpeg folder in the same directory
   
   **Important:** Your directory structure must look like:
   ```
   ffmpeg\bin\ffmpeg.exe
   ```
   Not like:
   ```
   ffmpeg\ffmpeg\bin\ffmpeg.exe
   ffmpeg-n5.1.5-win64-gpl-5.1\bin\ffmpeg.exe
   ```

3. **Configure Your IP Address**
   - Open `main.py` with Notepad
   - Find the line: `MY_IP = "insertyouriphere"`
   - Replace `insertyouriphere` with your IP address
   - Save the file

4. **Prepare Your Vine App Patcher**
   - Use one of these tested Vine app versions:
     - 1.1.2 iOS
     - 1.4.5 iOS
     - 1.4.8 iOS
     - 5.7.0 iOS
   
   **Recommended Patcher:** vineredirect - A Jailbreak tweak designed specifically for redirecting Vine API calls

## How It Works

diVineredirect runs a Flask web server that intercepts and redirects Vine API calls to a Nostr relay (Divine.video), fetching archived Vine videos and serving them through a patched mobile app.

### Architecture

1. **Local API Server** - Runs on port 2017 and mimics Vine API endpoints, redirecting requests to the Nostr relay
2. **Nostr Relay Integration** - Queries Divine.video relay for Kind 34236 Nostr events (video posts)
3. **Video Processing** - Downloads and transcodes videos to 480x480 H.264 format using FFmpeg
4. **Caching System** - Stores video URLs and feed data to reduce relay queries and improve performance

### Features

#### Working
- **Home/New Videos Feed** - Displays live Vine videos from the Nostr relay
- **Explore Section** - Browse channels and categories:
  - Popular Now / On the Rise
  - Channels: Classics (pre-2017 videos), Animals, Art, Comedy, DIY, Style, Family, Science & Tech
- **Tags** - Search videos by hashtag
- **Video Playback** - Streams transcoded videos at 480x480 resolution with loop count metadata

#### In Development
Additional features are planned for future updates.

### Supported Endpoints

- `/timelines/main` - Home feed
- `/timelines/tags/<tag_name>` - Tag-based feeds (popular, trending, recent)
- `/timelines/channel/<channel_name>` - Channel feeds
- `/explore` - Interactive explore page with categories
- `/stream/<event_id>.mp4` - Video streaming
