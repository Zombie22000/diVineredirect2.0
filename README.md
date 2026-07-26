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
   - Create a new folder for the project
   - Place `main.py` in this folder
   - Place your FFmpeg folder in this directory
   
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

diVineredirect creates a local server that redirects Vine API calls, allowing you to access Vine content through a patched mobile app. The application currently supports the following features:

### Working Features
- Home/new videos feed (non-placeholder)
- Explore section (non-placeholder, search not available)
- Tags
- Non-placeholder video playback

### In Development
Additional features are planned for future updates.
