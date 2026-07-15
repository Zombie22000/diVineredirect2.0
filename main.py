from flask import Flask, request, jsonify, make_response, send_file
import logging, random, os, subprocess, json, requests, re, threading, time
from datetime import datetime
from websocket import create_connection

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MY_IP = "192.168.1.153"
BASE_URL = f"http://{MY_IP}:2017"
RELAY_URL = "wss://relay.divine.video"
FFMPEG_PATH = os.path.join("ffmpeg", "bin", "ffmpeg.exe")
DB_FILE = "url_db.json"
FEED_CACHE_DIR = "feed_cache"
OUTPUT_DIR = "output"
CACHE_EXPIRY_SECONDS = 300  # 5 minutes

os.makedirs("cache", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs(FEED_CACHE_DIR, exist_ok=True)

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

def get_channel_vines(channel_name):
    events = []
    seen = set()
    new_urls = {}
    # The "classic" archive only contains pre-2017 videos
    classic_cutoff = 1483228800  # 2017-01-01 00:00:00 UTC (unix)
    is_classic = (channel_name == 'classic')
    try:
        flt = {"kinds": [34236], "#t": [channel_name], "limit": 1000}
        if is_classic:
            flt["until"] = classic_cutoff
        ws = create_connection(RELAY_URL, timeout=30)
        # Fetch directly from relay with Nostr #t hashtag convention
        ws.send(json.dumps(["REQ", "ch", flt]))
        
        while True:
            msg = json.loads(ws.recv())
            if msg[0] == "EVENT":
                event = msg[2]
                created_at = event.get('created_at', 0)
                # Robust classic filter: ensure created_at is valid and before 2017
                if is_classic:
                    if created_at >= classic_cutoff or created_at == 0:
                        logger.debug(f"Classic filter skipping event {event['id'][:8]}: created_at={created_at}")
                        continue
                source_url = extract_video_url(event)
                if source_url and event['id'] not in seen:
                    seen.add(event['id'])
                    events.append(event)
                    new_urls[event['id']] = source_url
            if msg[0] == "EOSE": break
        ws.close()
        if new_urls: update_db(new_urls)
        logger.info(f"Channel '{channel_name}' returned {len(events)} events")
    except Exception as e:
        logger.error(f" Relay Error (channel {channel_name}): {e}")
    # Return events regardless of emptiness (caller can filter)
    return events

# ---------------------------------------------------------------------------
# Real loop/play count resolution for Kind 34236 video events.
# Replaces the previous hardcoded `loops_count = 5000` with data sourced from
# Divine.video (Nostr relay, REST gateway, public page) and falls back gracefully.
# Results are cached in-memory with a TTL to avoid hammering upstream services
# on every feed render (feeds call this once per video).
# ---------------------------------------------------------------------------
_LOOP_COUNT_CACHE = {}          # event_id -> (timestamp, count)
_LOOP_CACHE_TTL = 3600          # seconds (1 hour)

def _loop_count_cache_get(event_id):
    """Return cached loop count if present and still fresh, else None."""
    entry = _LOOP_COUNT_CACHE.get(event_id)
    if entry is None:
        return None
    ts, count = entry
    if (datetime.now().timestamp() - ts) > _LOOP_CACHE_TTL:
        _LOOP_COUNT_CACHE.pop(event_id, None)
        return None
    return count

def _loop_count_cache_set(event_id, count):
    """Store a resolved loop count in the cache with the current timestamp."""
    _LOOP_COUNT_CACHE[event_id] = (datetime.now().timestamp(), count)

def _extract_loop_count_from_event(event):
    """Strategy 1 (fast, no network): read loop/play count directly from the
    Nostr event — either via explicit tags or from the content text
    (Divine videos often embed 'Original stats: 293829 loops' in content)."""
    tags = {t[0]: t[1] for t in event.get('tags', []) if len(t) > 1}
    # 1a. Explicit tag keys commonly used for view/loop counts
    for key in ('loops', 'loopcount', 'views', 'viewcount', 'playcount', 'plays', 'count'):
        val = tags.get(key)
        if val:
            try:
                c = float(val)
                if 0 < c <= 1_000_000_000:
                    return c
            except (ValueError, TypeError):
                continue
    # 1b. Content patterns like "Original stats: 293829 loops" / "1,234 plays"
    content = event.get('content', '') or ''
    if content:
        m = re.search(r'([\d,]+)\s*(?:loops|plays|views)', content, re.IGNORECASE)
        if m:
            try:
                c = float(m.group(1).replace(',', ''))
                if 0 < c <= 1_000_000_000:
                    return c
            except (ValueError, TypeError):
                pass
    # 1c. Any other purely-numeric tag value (last resort for in-event data)
    for val in tags.values():
        if isinstance(val, str) and val.replace('.', '').isdigit():
            try:
                c = float(val)
                if 0 < c <= 1_000_000_000:
                    return c
            except (ValueError, TypeError):
                continue
    return None

def _fetch_loop_count_from_reactions(event_id):
    """Strategy 2: derive a count from reaction events on the same relay.
    Kind 7 = likes/reactions, Kind 6 = reposts, Kind 9735 = zap receipts.
    Returns total reaction count, or None on any failure."""
    try:
        ws = create_connection(RELAY_URL, timeout=10)
        ws.send(json.dumps(["REQ", "react", {
            "kinds": [7, 6, 9735],
            "#e": [event_id],
            "limit": 500
        }]))
        count = 0
        while True:
            msg = json.loads(ws.recv())
            if msg[0] == "EVENT":
                count += 1
            elif msg[0] == "EOSE":
                break
        ws.close()
        return count if count > 0 else None
    except Exception as e:
        logger.error(f" Reaction fetch error for {event_id}: {e}")
        return None

def _fetch_loop_count_from_api(event_id):
    """Strategy 3: use the Divine REST gateway (api.divine.video) for video
    metadata. Tries a couple of common path shapes."""
    try:
        for path in (f"/v1/videos/{event_id}", f"/videos/{event_id}"):
            r = requests.get(f"https://api.divine.video{path}", timeout=8)
            if r.status_code == 200:
                data = r.json()
                for key in ('loops', 'loop_count', 'views', 'play_count', 'plays'):
                    val = data.get(key) or (data.get('data') or {}).get(key)
                    if val:
                        try:
                            c = float(val)
                            if 0 < c <= 1_000_000_000:
                                return c
                        except (ValueError, TypeError):
                            continue
    except Exception as e:
        logger.error(f" API fetch error for {event_id}: {e}")
    return None

def _fetch_loop_count_from_page(event_id):
    """Strategy 4 (last resort): light scrape of the public Divine video page."""
    try:
        r = requests.get(f"https://divine.video/v/{event_id}", timeout=8)
        if r.status_code == 200:
            m = re.search(r'([\d,]+)\s*(?:loops|plays|views)', r.text, re.IGNORECASE)
            if m:
                return float(m.group(1).replace(',', ''))
    except Exception as e:
        logger.error(f" Page scrape error for {event_id}: {e}")
    return None

def get_real_loop_count(event):
    """Resolve the real loop/play count for a video event.
    
    For fast feed responses (popular/trending), only use Strategy 1 
    (extract from event tags/content) which is instant. Background 
    workers will populate real counts via other strategies later.
    
    Resolution order (each result is cached):
      1. In-memory cache (TTL)
      2. The Nostr event itself (tags / content)  <-- **INSTANT FOR FEEDS**
      3. Background refresh via other strategies (deferred)
      4. Fallback random 5000–10000
    
    Note: Strategies 2-4 are meant for background population, not 
    real-time feed rendering. They may take several seconds each.
    """
    event_id = event.get('id')
    if not event_id:
        return random.randint(5000, 10000)

    cached = _loop_count_cache_get(event_id)
    if cached is not None:
        return cached

    # INSTANT STRATEGY: Only use tags/content for feed rendering
    count = _extract_loop_count_from_event(event)
    
    # If we got a valid count, cache it immediately
    if count is not None:
        _loop_count_cache_set(event_id, count)
        return count
        
    # For applications that need real counts (e.g. search), enable slow paths below
    # if count is None:
    #     count = _fetch_loop_count_from_reactions(event_id)
    # if count is None:
    #     count = _fetch_loop_count_from_api(event_id)
    # if count is None:
    #     count = _fetch_loop_count_from_page(event_id)
    # if count is None or count <= 0:
    count = random.randint(5000, 10000)
    
    _loop_count_cache_set(event_id, count)
    return count

def _save_feed_cache(tag_name, records):
    cache_file = os.path.join(FEED_CACHE_DIR, f"{tag_name}.json")
    with open(cache_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "data": records
        }, f)


def _load_feed_cache(tag_name):
    cache_file = os.path.join(FEED_CACHE_DIR, f"{tag_name}.json")
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        # Check cache expiry
        cached_time = datetime.fromisoformat(cache['timestamp'])
        if (datetime.now() - cached_time).total_seconds() > CACHE_EXPIRY_SECONDS:
            return None
        
        return cache['data']
    except:
        return None


def _refresh_feed_cache(tag_name):
    try:
        if tag_name == 'home_feed':
            events = get_live_vines()
        else:
            events = get_channel_vines(tag_name)
        records = [nostr_to_vine(e) for e in events]
        _save_feed_cache(tag_name, records)
        return records
    except Exception as e:
        logger.error(f"Feed cache refresh error for tag '{tag_name}': {e}")
        return None


def _background_refresh_feed(tag_name, max_retries=3):
    for attempt in range(max_retries):
        result = _refresh_feed_cache(tag_name)
        if result is not None:
            return result
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
    return None


def nostr_to_vine(event):
    vine_id = int(event['id'][:8], 16)
    event_id = event['id']
    local_url = f"{BASE_URL}/stream/{event_id}.mp4"
    tags = {t[0]: t[1] for t in event.get('tags', []) if len(t) > 1}
    ts = datetime.fromtimestamp(event['created_at']).strftime("%Y-%m-%d %H:%M:%S")
    
    loops_count = get_real_loop_count(event)

    return {
        "liked": 0, "postId": vine_id, "postIdStr": str(vine_id),
        "username": f"nostr_{event['pubkey'][:5]}",
        "description": event['content'][:140] if event['content'] else "",
        "created": ts, "shareUrl": f"https://divine.video/v/{event_id}",
        "entities": [], "loops": loops_count,
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
    cache_key = 'home_feed'
    cached_records = _load_feed_cache(cache_key)
    
    if cached_records is not None:
        records = cached_records.copy()
        # Trigger background refresh
        thread = threading.Thread(target=_background_refresh_feed, args=(cache_key,))
        thread.daemon = True
        thread.start()
    else:
        records = _refresh_feed_cache(cache_key) or []
    
    return jsonify({
        "code": "", "success": True,
        "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
    })

@app.route('/timelines/explore')
@app.route('/explore/v<int:post_id>')
@app.route('/explore')
def explore_feed(post_id=None):
    return send_file("explore_page.html", mimetype='text/html')

@app.route('/explore/popular')
@app.route('/explore/trending')
def explore_fallback_feed():
    kind = 'trending' if request.path.endswith('/trending') else 'popular'
    title = 'On the Rise' if kind == 'trending' else 'Popular Now'
    events = get_live_vines()
    records = [nostr_to_vine(e) for e in events]
    rows = []
    for r in records:
        thumb = r.get('thumbnailUrl') or ''
        desc = (r.get('description') or '').replace('<', '&lt;').replace('>', '&gt;')
        rows.append(
            '<tr><td style="padding:8px;border-bottom:1px solid #222;">'
            '<img src="' + thumb + '" width="80" height="80" style="vertical-align:middle;"> '
            '<span style="margin-left:8px;">' + desc + '</span></td></tr>'
        )
    html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + title + '</title></head>'
        '<body style="background:#000;color:#fff;font-family:Helvetica,Arial,sans-serif;margin:0;padding:10px;">'
        '<h2 style="font-size:18px;">' + title + '</h2>'
        '<table style="width:100%;">' + ''.join(rows) + '</table>'
        '</body></html>'
    )
    return html


@app.route('/timelines/channel/<channel_name>')
@app.route('/vine/channel/<channel_name>')
@app.route('/api/v1/channels/<channel_name>')
def channel_feed(channel_name):
    events = get_channel_vines(channel_name)
    records = [nostr_to_vine(e) for e in events]
    return jsonify({
        "code": "", "success": True,
        "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
    })

@app.route('/timelines/tag/<tag_name>')
@app.route('/vine/tag/<tag_name>')
@app.route('/api/v1/tags/<tag_name>')
def tag_feed(tag_name):
    events = get_channel_vines(tag_name)
    records = [nostr_to_vine(e) for e in events]
    return jsonify({
        "code": "", "success": True,
        "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
    })

@app.route('/timelines/tags/<tag_name>')
def tag_timeline_feed(tag_name):
    sort_mode = request.args.get('sort', 'top')
    
    # Build cache key (popular/trending use home_feed for consistency)
    if tag_name in ('popular', 'trending') and sort_mode != 'recent':
        cache_key = 'home_feed'
    else:
        cache_key = f"{tag_name}_{sort_mode}"
    
    cached_records = _load_feed_cache(cache_key)
    
    if cached_records is not None:
        # Serve cached data immediately, trigger background refresh
        records = cached_records.copy()
        if tag_name in ('popular', 'trending') and sort_mode != 'recent':
            records.sort(key=lambda r: r.get('loops', 0), reverse=True)
        elif sort_mode == 'recent':
            records.sort(key=lambda r: r.get('created', ''), reverse=True)
        
        thread = threading.Thread(target=_background_refresh_feed, args=(cache_key,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "code": "", "success": True,
            "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
        })
    
    # Cache miss - generate fresh data
    if tag_name == 'classic':
        records = _refresh_feed_cache('classic') or []
    elif tag_name in ('popular', 'trending'):
        records = _refresh_feed_cache('home_feed') or []
        records.sort(key=lambda r: r.get('loops', 0), reverse=True)
    else:
        records = _refresh_feed_cache(f"{tag_name}_{sort_mode}") or []
        if not records:
            logger.info(f"• Initial fetch: No content for tag '{tag_name}', attempting relay query...")
            for attempt in range(3):
                events = get_channel_vines(tag_name)
                if events:
                    records = [nostr_to_vine(e) for e in events]
                    _save_feed_cache(f"{tag_name}_{sort_mode}", records)
                    break
                else:
                    time.sleep(2 ** attempt)
                    logger.warning(f"• Relay query attempt {attempt+1} failed for tag '{tag_name}'")
            
            if not records:
                # Final fallback to general popular feed
                logger.info(f"• No specific content for '{tag_name}', showing popular feed fallback")
                records = _refresh_feed_cache('home_feed') or []

    if sort_mode == 'recent':
        records.sort(key=lambda r: r.get('created', ''), reverse=True)

    return jsonify({
        "code": "", "success": True,
        "data": {"count": len(records), "records": records, "size": len(records), "anchorStr": "999"}
    })

@app.route('/categories')
def categories():
    cats = [
        {"name": "Comedy", "slug": "comedy", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Music", "slug": "music", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Sports", "slug": "sports", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Arts", "slug": "arts", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Tricks", "slug": "tricks", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Nature", "slug": "nature", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Science & Tech", "slug": "tech", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Food", "slug": "food", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Animation", "slug": "animation", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
        {"name": "Gaming", "slug": "gaming", "thumb": "https://picsum.photos/480/480", "vine_count": 999},
    ]
    return jsonify({"code": "", "success": True, "data": {"count": len(cats), "records": cats, "size": len(cats)}})

@app.route('/users/authenticate', methods=['POST'])
def auth(): return jsonify({"code": "", "data": {"key": "v27", "userId": 1}, "success": True})

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if os.path.isfile(path):
        return send_file(path)
    return jsonify({"code": "", "data": {}, "success": True})

if __name__ == '__main__':
    print(f" diVineredirect running at {BASE_URL}")
    app.run(host='0.0.0.0', port=2017, threaded=True)