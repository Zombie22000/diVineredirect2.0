```html
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
   ├── explore_page.html
   ├── ffmpeg\
   │   └── bin\
   │       └── ffmpeg.exe
   └── (other files)
   ```

   **Common mistakes to avoid:**
   ```
   [WRONG] ffmpeg\ffmpeg\bin\ffmpeg.exe (too many folders)
   [WRONG] ffmpeg-n5.1.5-win64-gpl-5.1\bin\ffmpeg.exe (didn't rename)
   [CORRECT] ffmpeg\bin\ffmpeg.exe (correct)
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

- `/timelines/main` or `/timelines/graph` - Home feed (also accessible via `vine://`)
- `/timelines/tags/<tag_name>` - Videos by tag or category (also accessible via `vine://tag/<tag_name>`)
- `/timelines/channel/<channel_name>` - Videos by channel (also accessible via `vine://channel/<channel_name>`)
- `/explore` (and `/timelines/explore`, `/explore/v<post_id>`) - Serves the Explore hub page (`explore_page.html`)
- `/explore/popular` / `/explore/trending` - Simple HTML list fallbacks
- `/stream/<event_id>.mp4` - Stream a video file

---

## Example API Outputs

Below are realistic example responses returned by the local server (port 2017).  
These match the exact JSON / HTML structures produced by the Flask routes.  
Replace `192.168.1.100` with your own `MY_IP` value.

### 1. Home Feed  
**Endpoints:** `GET /timelines/main` `GET /timelines/graph`

```json
{
  "code": "",
  "success": true,
  "data": {
    "count": 3,
    "records": [
      {
        "liked": 0,
        "postId": 29384756,
        "postIdStr": "29384756",
        "username": "nostr_a1b2c",
        "description": "Original stats: 293829 loops  #comedy",
        "created": "2016-08-14 22:17:03",
        "shareUrl": "https://divine.video/v/a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
        "entities": [],
        "loops": 293829,
        "thumbnailUrl": "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
          "userId": 29384756,
          "username": "nostr_a1b2c",
          "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": "http://192.168.1.100:2017/stream/a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef.mp4",
        "videoUrls": [
          {
            "videoUrl": "http://192.168.1.100:2017/stream/a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef.mp4",
            "format": "h264",
            "default": 1,
            "id": "original"
          }
        ]
      },
      {
        "liked": 0,
        "postId": 18472930,
        "postIdStr": "18472930",
        "username": "nostr_f9e8d",
        "description": "cat does a flip",
        "created": "2015-11-02 09:44:12",
        "shareUrl": "https://divine.video/v/f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a39281706f5e4d3c2b1a0",
        "entities": [],
        "loops": 8741,
        "thumbnailUrl": "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
          "userId": 18472930,
          "username": "nostr_f9e8d",
          "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": "http://192.168.1.100:2017/stream/f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a39281706f5e4d3c2b1a0.mp4",
        "videoUrls": [
          {
            "videoUrl": "http://192.168.1.100:2017/stream/f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a39281706f5e4d3c2b1a0.mp4",
            "format": "h264",
            "default": 1,
            "id": "original"
          }
        ]
      },
      {
        "liked": 0,
        "postId": 57201938,
        "postIdStr": "57201938",
        "username": "nostr_3c4d5",
        "description": "",
        "created": "2016-12-25 18:03:47",
        "shareUrl": "https://divine.video/v/3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d",
        "entities": [],
        "loops": 6123,
        "thumbnailUrl": "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
          "userId": 57201938,
          "username": "nostr_3c4d5",
          "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": "http://192.168.1.100:2017/stream/3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d.mp4",
        "videoUrls": [
          {
            "videoUrl": "http://192.168.1.100:2017/stream/3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d.mp4",
            "format": "h264",
            "default": 1,
            "id": "original"
          }
        ]
      }
    ],
    "size": 3,
    "anchorStr": "999"
  }
}
```

### 2. Channel / Tag Feed  
**Endpoints:**  
`GET /timelines/channel/classic`  
`GET /vine/channel/classic`  
`GET /api/v1/channels/classic`  
`GET /timelines/tag/comedy`  
`GET /vine/tag/comedy`  
`GET /api/v1/tags/comedy`  
`GET /timelines/tags/classic?sort=top`  
`GET /timelines/tags/popular?sort=recent`

```json
{
  "code": "",
  "success": true,
  "data": {
    "count": 2,
    "records": [
      {
        "liked": 0,
        "postId": 91827364,
        "postIdStr": "91827364",
        "username": "nostr_7b6a5",
        "description": "pre-2017 classic vine",
        "created": "2015-03-19 14:22:01",
        "shareUrl": "https://divine.video/v/7b6a5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6",
        "entities": [],
        "loops": 15420,
        "thumbnailUrl": "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
          "userId": 91827364,
          "username": "nostr_7b6a5",
          "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": "http://192.168.1.100:2017/stream/7b6a5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6.mp4",
        "videoUrls": [
          {
            "videoUrl": "http://192.168.1.100:2017/stream/7b6a5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6.mp4",
            "format": "h264",
            "default": 1,
            "id": "original"
          }
        ]
      },
      {
        "liked": 0,
        "postId": 45678901,
        "postIdStr": "45678901",
        "username": "nostr_2e1d0",
        "description": "another classic clip",
        "created": "2014-07-08 11:55:33",
        "shareUrl": "https://divine.video/v/2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1",
        "entities": [],
        "loops": 9821,
        "thumbnailUrl": "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
          "userId": 45678901,
          "username": "nostr_2e1d0",
          "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": "http://192.168.1.100:2017/stream/2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1.mp4",
        "videoUrls": [
          {
            "videoUrl": "http://192.168.1.100:2017/stream/2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1.mp4",
            "format": "h264",
            "default": 1,
            "id": "original"
          }
        ]
      }
    ],
    "size": 2,
    "anchorStr": "999"
  }
}
```

*(When `sort=recent` is used the `created` field is sorted newest-first.  
When the tag is `popular` or `trending` the records are sorted by `loops` descending.)*

### 3. Categories List  
**Endpoint:** `GET /categories`

```json
{
  "code": "",
  "success": true,
  "data": {
    "count": 10,
    "records": [
      {
        "name": "Comedy",
        "slug": "comedy",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Music",
        "slug": "music",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Sports",
        "slug": "sports",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Arts",
        "slug": "arts",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Tricks",
        "slug": "tricks",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Nature",
        "slug": "nature",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Science & Tech",
        "slug": "tech",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Food",
        "slug": "food",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Animation",
        "slug": "animation",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      },
      {
        "name": "Gaming",
        "slug": "gaming",
        "thumb": "https://picsum.photos/480/480",
        "vine_count": 999
      }
    ],
    "size": 10
  }
}
```

### 4. Authentication  
**Endpoint:** `POST /users/authenticate`

```json
{
  "code": "",
  "data": {
    "key": "v27",
    "userId": 1
  },
  "success": true
}
```

### 5. Explore Hub Page  
**Endpoints:** `GET /explore` `GET /timelines/explore` `GET /explore/v<number>`

Returns the full contents of `explore_page.html` (Content-Type: `text/html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Explore</title>
    <style>
        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: rgba(0,0,0,0);
            -webkit-touch-callout: none;
        }
        body {
            background-color: #f0f2f5;
            font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 12px 12px 20px 12px;
            user-select: none;
            -webkit-user-select: none;
        }

        .hub-matrix {
            overflow: hidden;
            margin-bottom: 14px;
        }
        .hub-card {
            float: left;
            width: 50%;
            padding: 0 6px;
            box-sizing: border-box;
            text-decoration: none;
            color: #4a4e54;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: -0.2px;
        }
        .hub-card-inner {
            background-color: #ffffff;
            border: 1px solid #e1e3e6;
            border-radius: 5px;
            height: 94px;
            display: inline-block;
            width: 100%;
            text-align: center;
            vertical-align: middle;
            box-shadow: 0 1px 1px rgba(0,0,0,0.02);
            padding-top: 10px;
        }
        .hub-card:first-child {
            padding-left: 0;
        }
        .hub-card:last-child {
            padding-right: 0;
        }
        .hub-card:active .hub-card-inner {
            background-color: #f9fafb;
        }

        .hub-vector {
            height: 32px;
            margin-bottom: 5px;
            display: block;
            text-align: center;
        }
        .hub-vector img {
            height: 28px;
            width: auto;
            display: block;
            margin: 0 auto;
        }
        .hub-vector span {
            font-size: 26px;
            display: none;
        }

        .color-star { color: #f9a825; }
        .color-arrow { color: #5ac8fa; }

        .section-label {
            color: #92969c;
            font-size: 13px;
            text-align: center;
            margin: 14px 0 10px 0;
            font-weight: normal;
        }

        .channel-stack {
            overflow: hidden;
        }
        .channel-row {
            display: block;
            height: 72px;
            border-radius: 5px;
            padding: 0 16px;
            text-decoration: none;
            color: #ffffff;
            font-size: 19px;
            font-weight: bold;
            letter-spacing: -0.3px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08);
            margin-bottom: 10px;
        }
        .channel-row:active {
            opacity: 0.92;
        }

        .icon-frame {
            margin-right: 15px;
            width: 44px;
            height: 44px;
            display: block;
            float: left;
            text-align: center;
            line-height: 44px;
            margin-top: 14px;
        }
        .icon-frame img {
            width: 34px;
            height: 34px;
            display: block;
            margin: 5px auto 0;
        }
        .icon-frame span {
            font-size: 30px;
            display: none;
            line-height: 44px;
            text-align: center;
        }
        .channel-text {
            line-height: 72px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .channel-classics  { background-color: #00bf8f; }
        .channel-animals   { background-color: #4a89dc; }
        .channel-art       { background-color: #9b59b6; }
        .channel-comedy    { background-color: #ed5565; }
        .channel-diy       { background-color: #4ecdc4; }
        .channel-scitech   { background-color: #ec87c0; }
        .channel-style     { background-color: #f5b041; }
        .channel-family    { background-color: #72d072; }

        .clearfix:after {
            content: ".";
            display: block;
            height: 0;
            clear: both;
            visibility: hidden;
        }
        .clearfix { display: inline-block; }
        .clearfix { display: block; }
    </style>
</head>
<body>

    <div class="hub-matrix clearfix">
        <div class="hub-card">
            <a href="vine://tag/popular" class="hub-card-inner clearfix" >
                <div class="hub-vector">
                    <img src="" onerror="this.style.display='none';this.nextSibling.style.display='inline';" alt="Popular Now" />
                    <span class="color-star">&#9733;</span>
                </div>
                Popular Now
            </a>
        </div>
        <div class="hub-card">
            <a href="vine://tag/trending" class="hub-card-inner clearfix" >
                <div class="hub-vector">
                    <img src="" onerror="this.style.display='none';this.nextSibling.style.display='inline';" alt="On the Rise" />
                    <span class="color-arrow">&#9650;</span>
                </div>
                On the Rise
            </a>
        </div>
    </div>

    <div class="section-label">Channels</div>

    <div class="channel-stack clearfix">
        <a href="vine://tag/classic" class="channel-row channel-classics">
            <div class="icon-frame"><img src="" onerror="this.style.display='none';this.nextSibling.style.display='inline';" alt="Classics" /><span style="display:none;">&#127909;</span></div>
            <span class="channel-text">Classics</span>
        </a>

        <a href="vine://tag/animals" class="channel-row channel-animals">
            <div class="icon-frame"><span>&#128049;</span></div>
            <span class="channel-text">Animals</span>
        </a>

        <a href="vine://tag/art" class="channel-row channel-art">
            <div class="icon-frame"><span>&#127912;</span></div>
            <span class="channel-text">Art</span>
        </a>

        <a href="vine://tag/comedy" class="channel-row channel-comedy">
            <div class="icon-frame"><img src="" onerror="this.style.display='none';this.nextSibling.style.display='inline';" alt="Comedy" /><span style="display:none;">&#128565;</span></div>
            <span class="channel-text">Comedy</span>
        </a>

        <a href="vine://tag/diy" class="channel-row channel-diy">
            <div class="icon-frame"><span>&#127912;</span></div>
            <span class="channel-text">DIY</span>
        </a>

        <a href="vine://tag/style" class="channel-row channel-style">
            <div class="icon-frame"><span>&#128376;</span></div>
            <span class="channel-text">Style</span>
        </a>

        <a href="vine://tag/family" class="channel-row channel-family">
            <div class="icon-frame"><span>&#127968;</span></div>
            <span class="channel-text">Family</span>
        </a>

        <a href="vine://tag/tech" class="channel-row channel-scitech">
            <div class="icon-frame"><span>&#128187;</span></div>
            <span class="channel-text">Science &amp; Tech</span>
        </a>
    </div>

</body>
</html>
```

### 6. Explore / Popular / Trending (HTML fallback)  
**Endpoints:**  
`GET /explore/popular`  
`GET /explore/trending`

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Popular Now</title>
</head>
<body style="background:#000;color:#fff;font-family:Helvetica,Arial,sans-serif;margin:0;padding:10px;">
  <h2 style="font-size:18px;">Popular Now</h2>
  <table style="width:100%;">
    <tr>
      <td style="padding:8px;border-bottom:1px solid #222;">
        <img src="https://picsum.photos/480/480" width="80" height="80" style="vertical-align:middle;">
        <span style="margin-left:8px;">Original stats: 293829 loops  #comedy</span>
      </td>
    </tr>
    <tr>
      <td style="padding:8px;border-bottom:1px solid #222;">
        <img src="https://picsum.photos/480/480" width="80" height="80" style="vertical-align:middle;">
        <span style="margin-left:8px;">cat does a flip</span>
      </td>
    </tr>
  </table>
</body>
</html>
```

*(The title becomes “On the Rise” when the path ends with `/trending`.)*

### 7. Video Stream  
**Endpoint:** `GET /stream/<event_id>.mp4`

- **Success:** binary MP4 file (Content-Type: `video/mp4`) after FFmpeg has transcoded the source to 480×480 H.264 + AAC.
- **Missing mapping:** plain-text response  
  ```
  Missing link for a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef
  ```
  with HTTP 404.
- **Transcode failure:** plain-text response  
  ```
  Transcode Error: ...
  ```
  with HTTP 500.

### 8. Catch-all / Unknown Path  
**Endpoint:** any unmatched `GET` or `POST`

```json
{
  "code": "",
  "data": {},
  "success": true
}
```

*(If the path happens to be a real file on disk the server returns the file instead.)*
