import httpx
import re
import os
import random
import time

client = httpx.Client(http2=True)

def safe_filename(name, max_len=120):
    # remove invalid Windows characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)

    # normalize spaces
    name = re.sub(r'\s+', ' ', name).strip()

    # always keep extension if present
    ext = ""
    if "." in name:
        base, ext = name.rsplit(".", 1)
        ext = "." + ext
    else:
        base = name

    # reserved fallback
    if not base:
        base = "video"

    # compute allowed length for base
    max_base_len = max_len - len(ext)

    # if too long → KEEP END of string (important change)
    if len(base) > max_base_len:
        base = base[-max_base_len:]

    base = base.rstrip('. ')

    return base + ext


def get_list(sid, client, headers):
    cursor = int(time.time() * 1000)
    vfp = "verify_" + ''.join(random.choices('0123456789ABCDEF', k=7))
    did = str(random.randint(7250000000000000000, 7325099899999994577))
    avids = []

    while True:
        params = {
            'aid': '1988',
            'app_language': 'en',
            'app_name': 'tiktok_web',
            'browser_language': 'en-US',
            'browser_name': 'Mozilla',
            'browser_online': 'true',
            'browser_platform': 'Win32',
            'browser_version': '5.0 (Windows)',
            'channel': 'tiktok_web',
            'cookie_enabled': 'true',
            'count': '15',
            'cursor': cursor,
            'device_id': did,
            'device_platform': 'web_pc',
            'focus_state': 'true',
            'from_page': 'user',
            'history_len': '2',
            'is_fullscreen': 'false',
            'is_page_visible': 'true',
            'language': 'en',
            'os': 'windows',
            'priority_region': '',
            'referer': '',
            'region': 'US',
            'screen_height': '1080',
            'screen_width': '1920',
            'secUid': sid,
            'type': '1',
            'tz_name': 'UTC',
            'verifyFp': vfp,
            'webcast_language': 'en',
        }

        r = client.get(
            'https://www.tiktok.com/api/creator/item_list/',
            params=params,
            headers=headers
        )

        data = r.json()
        items = data.get('itemList', [])
        avids.extend(items)

        nid = sorted(v['id'] for v in items)
        existid = sorted(v['id'] for v in avids[:-len(items)])

        if nid and nid == existid:
            print("i think deviceid flagged mrrp i stopped")
            break

        if not data.get('hasMorePrevious') or not items:
            break

        cursor = int(items[-1]['createTime'] * 1000)

    return avids


def get_sid(client, username, headers):
    r = client.get(f"https://www.tiktok.com/@{username}", headers=headers, timeout=10)
    r.raise_for_status()

    data = r.text
    sidlst = re.findall(r'"secUid":"([A-Za-z0-9_-]+)"', data)

    sid = sidlst[0] if sidlst else None

    if not sid:

        print(f"erm my catboy could find sid for @{username} resp was {list(data.keys())}")

    return sid


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.tiktok.com/',
    'Origin': 'https://www.tiktok.com',
    'Sec-GPC': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache'
}

# initialize cookies
r = client.get("https://www.tiktok.com/@tiktok", headers=headers, timeout=10)
ttwid = r.cookies.get("ttwid")
client.cookies.set("ttwid", ttwid, domain=".tiktok.com")

username = input("Enter TikTok username: ")
sid = get_sid(client, username, headers)

itemList = get_list(sid, client, headers)

os.makedirs("dl", exist_ok=True)
os.makedirs("error", exist_ok=True)

for item in itemList:
    video = item.get("video") or {}
    videoid = video.get("id", "")

    author = item.get("author", {}).get("uniqueId", "unknown")
    desc = item.get("desc") or "no_title"

    videoUrl = f"https://www.tiktok.com/@{author}/video/{videoid}"

    videor = client.get(videoUrl, headers=headers)

    dlurl = re.search(r'"UrlList":\["(https:[^"]+)"', videor.text)

    if not dlurl:
        with open(f"error/{videoid}.html", "w", encoding="utf-8") as f:
            f.write(videor.text)
        continue

    dlurl = dlurl.group(1).replace("\\u002F", "/").replace("\\u0026", "&")

    print("downloading video...")

    videofile = client.get(dlurl, headers=headers)

    filename = f"{desc} - By {author} - {videoid}.mp4"
    filename = safe_filename(filename, max_len=120)

    path = os.path.join("dl", filename)

    with open(path, "wb") as f:
        f.write(videofile.content)