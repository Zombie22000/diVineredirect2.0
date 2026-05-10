from flask import Flask, request, jsonify, make_response, send_file
import logging, random, os, subprocess, json, requests, re
from datetime import datetime
from websocket import create_connection

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MY_IP = "insertyouriphere"
BASE_URL = f"http://{MY_IP}:2017"
RELAY_URL = "wss://relay.divine.video"
FFMPEG_PATH = os.path.join("ffmpeg", "bin", "ffmpeg.exe")
DB_FILE = "url_db.json"

os.makedirs("cache", exist_ok=True)
os.makedirs("videos", exist_ok=True)

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {}

def update_db(new_mappings):
    db = load_db()
    db.update(new_mappings)
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

def extract_video_url(event):
    for tag in event.get('tags', []):
        if tag[0] in ['url', 'm', 'r'] and len(tag) > 1:
            val = tag[1].lower()
            if '.mp4' in val or 'blossom' in val or 'cdn' in val:
                return tag[1]
        
        if tag[0] == 'imeta':
            for item in tag[1:]:
                if item.startswith('url '):
                    return item.replace('url ', '').strip()

    content = event.get('content', '')
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
    for u in urls:
        if '.mp4' in u.lower():
            return u
    return None

def get_live_vines():
    events = []
    new_urls = {}
    try:
        ws = create_connection(RELAY_URL, timeout=10)
        ws.send(json.dumps(["REQ", "v", {"kinds": [34236], "limit": 1000}]))
        
        while len(events) < 20:
            msg = json.loads(ws.recv())
            if msg[0] == "EVENT":
                event = msg[2]
                source_url = extract_video_url(event)
                if source_url:
                    events.append(event)
                    new_urls[event['id']] = source_url
                    logger.info(f" Found Video: {source_url[:60]}...")
            if msg[0] == "EOSE": break
        ws.close()
        if new_urls: update_db(new_urls)
    except Exception as e:
        logger.error(f" Relay Error: {e}")
    return events

def nostr_to_vine(event):
    vine_id = int(event['id'][:8], 16)
    local_url = f"{BASE_URL}/stream/{event['id']}.mp4"
    tags = {t[0]: t[1] for t in event['tags'] if len(t) > 1}
    ts = datetime.fromtimestamp(event['created_at']).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "liked": 0, "postId": vine_id, "postIdStr": str(vine_id),
        "username": f"nostr_{event['pubkey'][:5]}",
        "description": event['content'][:140] if event['content'] else "",
        "created": ts, "shareUrl": f"https://vine.co/v/{vine_id}",
        "entities": [], "loops": {"count": float(random.randint(500, 9999))},
        "thumbnailUrl": tags.get('thumb') or "https://picsum.photos/480/480",
        "avatarUrl": "https://divine.video/favicon.ico",
        "user": {
            "userId": vine_id, "username": f"nostr_{event['pubkey'][:5]}",
            "avatarUrl": "https://divine.video/favicon.ico"
        },
        "videoUrl": local_url,
        "videoUrls": [{"videoUrl": local_url, "format": "h264", "default": 1, "id": "original"}]
    }

@app.route('/stream/<event_id>.mp4')
def stream_video(event_id):
    output = f"cache/{event_id}.mp4"
    temp_raw = f"cache/raw_{event_id}.mp4"
    
    if os.path.exists(output):
        return send_file(output, mimetype='video/mp4')

    db = load_db()
    source_url = db.get(event_id)
    if not source_url:
        return f"Missing link for {event_id}", 404

    try:
        logger.info(f" Downloading: {source_url}")
        r = requests.get(source_url, timeout=20)
        with open(temp_raw, 'wb') as f: f.write(r.content)

        subprocess.run([
            FFMPEG_PATH, "-y", "-i", temp_raw,
            "-vf", "scale=480:480:force_original_aspect_ratio=increase,crop=480:480",
            "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", 
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "128k", output
        ], check=True)
        
        if os.path.exists(temp_raw): os.remove(temp_raw)
        return send_file(output, mimetype='video/mp4')
    except Exception as e:
        return f"Transcode Error: {e}", 500

@app.route('/timelines/graph')
@app.route('/timelines/main')
def home_feed():
    events = get_live_vines()
    records = [nostr_to_vine(e) for e in events]
    return jsonify({
        "code": "", "success": True,
        "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
    })

@app.route('/users/authenticate', methods=['POST'])
def auth(): return jsonify({"code": "", "data": {"key": "v27", "userId": 1}, "success": True})

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path): return jsonify({"code": "", "data": {}, "success": True})

if __name__ == '__main__':
    print(f" diVineredirect running at {BASE_URL}")
    app.run(host='0.0.0.0', port=2017, threaded=True)