<p align="center">
  <img src="divineredirect-logo-green.png" alt="diVineredirect logo green">
</p>

---

## Installation

### What You Need

- **Windows 8.1 or later** (v2.1 and earlier are Windows-only. macOS and Linux support may come in future versions)
- **[Python](https://www.python.org/)** - Download the latest version and install it (click the green button on the website). During installation, make sure to check the box that says "Add Python to PATH"
- **[FFmpeg n5.1.6 win64 gpl 5.1](https://github.com/BtbN/FFmpeg-Builds/releases?page=4)** - A video processing tool. Look for the file named `ffmpeg-n5.1.6-win64-gpl-5.1.zip` and download it

### Step-by-Step Setup

#### Step 1: Install Python Libraries
Open Command Prompt (press `Win + R`, type `cmd`, then press Enter) and copy-paste this command:
```bash
pip install flask requests websocket-client
```
Press Enter and wait for it to finish.

#### Step 2: Prepare Your Folder
1. Create a new folder on your computer (e.g., `C:\diVineredirect`)
2. Extract the diVineredirect release zip file into this folder (v2.1+) OR place `main.py` here (v2.0)
3. Extract your FFmpeg zip file so the folder structure looks like this inside your diVineredirect folder:
   ```
   ffmpeg\bin\ffmpeg.exe
   ```
   
   **This is the most important part!** Your folder should look like:
   ```
   C:\diVineredirect\
   ├── main.py
   ├── ffmpeg\
   │   └── bin\
   │       └── ffmpeg.exe
   └── (other files)
   ```
   
   **Common mistakes to avoid:**
   ```
   [WRONG] ffmpeg\ffmpeg\bin\ffmpeg.exe  (too many folders)
   [WRONG] ffmpeg-n5.1.5-win64-gpl-5.1\bin\ffmpeg.exe  (didn't rename)
   [CORRECT] ffmpeg\bin\ffmpeg.exe  (correct)
   ```

#### Step 3: Add Your IP Address
1. Open `main.py` with Notepad (right-click → Open with → Notepad)
2. Find this line:
   ```
   MY_IP = "insertyouriphere"
   ```
3. Replace `insertyouriphere` with your computer's IP address (for example: `MY_IP = "192.168.1.100"`)
   - To find your IP: Open Command Prompt and type `ipconfig`. Look for "IPv4 Address"
4. Save the file (Ctrl+S)

#### Step 4: Get a Patched Vine App
- Use one of these tested Vine app versions:
  - 1.1.2 iOS
  - 1.4.5 iOS
  - 1.4.8 iOS
  - 5.7.0 iOS
  
- **Recommended:** Use the **vineredirect** Jailbreak tweak to patch your Vine app to connect to diVineredirect

---

## How It Works

diVineredirect runs a server on your computer that pretends to be Vine. When you open the patched Vine app on your iPhone, it connects to your server instead of the real Vine servers. Your server fetches videos from Divine.video (a Nostr relay that has archived Vine videos) and sends them to your app.

### What Happens Behind the Scenes

1. **Local API Server** - Runs on port 2017 on your computer and mimics Vine API endpoints
2. **Video Source** - Queries Divine.video relay for archived Vine videos (these are stored as Nostr events)
3. **Video Processing** - Downloads videos and converts them to 480x480 format using FFmpeg
4. **Caching** - Stores video information locally so it doesn't have to ask Divine.video every time

### What You Can Do

#### Working Features
- **Home/New Videos Feed** - Browse live Vine videos from the archive
- **Explore Section** - Browse by category:
  - Popular Now / On the Rise
  - Channels: Classics (pre-2017 videos), Animals, Art, Comedy, DIY, Style, Family, Science & Tech
- **Tags** - Search videos by hashtag
- **Video Playback** - Watch videos with accurate view counts

#### Coming Soon
Additional features are planned for future updates.

### API Endpoints (Technical Reference)

**Note:** `vine://` protocol URLs map to `/timelines/` endpoints

- `/timelines/main` - Home feed (also accessible via `vine://`)
- `/timelines/tags/<tag_name>` - Videos by tag or category (also accessible via `vine://tag/<tag_name>`)
- `/timelines/channel/<channel_name>` - Videos by channel (also accessible via `vine://channel/<channel_name>`)
- `/explore` - Browse categories
- `/stream/<event_id>.mp4` - Stream a video file
