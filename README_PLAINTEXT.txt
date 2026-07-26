diVineredirect - Vine Video Archive Server

diVineredirect is a Windows-based server application that allows you to browse and watch diVine videos through a patched vine app. It works by intercepting API calls from the patched Vine app and redirecting them to Divine.video, a Nostr relay that hosts archived Vine content.

WHAT YOU NEED:
- Windows 8.1 or later (v2.1 and earlier are Windows-only)
- Python (latest version from python.org)
- FFmpeg n5.1.6 win64 gpl 5.1

QUICK SETUP:
1. Install Python dependencies: pip install flask requests websocket-client
2. Extract diVineredirect files and place FFmpeg folder in the same directory
3. Edit main.py and add your computer's IP address where it says MY_IP = "insertyouriphere"
4. Use a patched Vine app (tested versions: 1.1.2, 1.4.5, 1.4.8, 5.7.0 iOS) with the vineredirect Jailbreak tweak

FEATURES:
- Browse home feed with live Vine videos from the archive
- Explore by category: Classics, Animals, Art, Comedy, DIY, Style, Family, Science & Tech
- Search videos by hashtag
- Watch archived Vine videos with accurate view counts
- Runs on port 2017 on your local network

HOW IT WORKS:
The server intercepts your patched Vine app's API requests and fetches videos from Divine.video (a Nostr relay). It then processes and transcodes videos to 480x480 format using FFmpeg before serving them to your app. Video URLs and feed data are cached locally for faster performance.

TESTED VINE APP VERSIONS:
- 1.1.2 iOS
- 1.4.5 iOS
- 1.4.8 iOS
- 5.7.0 iOS

RECOMMENDED PATCHER:
Use the vineredirect Jailbreak tweak to patch your Vine app to connect to diVineredirect.

COMING SOON:
Additional features are planned for future updates.
