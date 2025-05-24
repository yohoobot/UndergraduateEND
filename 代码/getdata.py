"""
Spotify音乐爬虫：
每关键词获取10个有描述的歌单；
每歌单提取3首歌曲；
歌单必须有描述，歌手必须有genre，否则跳过；
"""

import requests
import pandas as pd
import time
import base64

# Spotify developer凭据 【替换】
CLIENT_ID = ""
CLIENT_SECRET = ""

# 获取access_token
def get_access_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    resp = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return resp.json().get("access_token") if resp.status_code == 200 else None
ACCESS_TOKEN = get_access_token(CLIENT_ID, CLIENT_SECRET)
if not ACCESS_TOKEN:
    raise RuntimeError("获取access_token【失败】")
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 关键词列表设置
KEYWORDS = [
    "buffet restaurant"
]

data_pairs = [] # 存放数据结果

# 数据爬取
for keyword in KEYWORDS:
    print(f"\n===========搜索关键词========：{keyword}")
    search_url = f"https://api.spotify.com/v1/search?q={keyword}&type=playlist&limit=50"
    resp = requests.get(search_url, headers=HEADERS)
    if resp.status_code != 200:
        print("*****  *搜索失败*  ***：", resp.text)
        continue
    all_playlists = resp.json().get("playlists", {}).get("items", [])
    print(f"=>==>返回歌单总数：{len(all_playlists)}")
    # 歌单有效性检查
    valid_playlists = []

    for pl in all_playlists:
        if not pl or not isinstance(pl, dict):
            continue
        desc = pl.get("description", "")
        if desc.strip():
            valid_playlists.append(pl)
        if len(valid_playlists) >= 10:
            break
    print(f"✅有描述的歌单数：{len(valid_playlists)}")

    for pl in valid_playlists:
        playlist_id = pl.get("id")
        playlist_name = pl.get("name", "")
        playlist_desc = pl.get("description", "")
        playlist_url = pl.get("external_urls", {}).get("spotify", "")

        print(f"==========>抓取歌单：{playlist_name}")
        tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=3"
        track_resp = requests.get(tracks_url, headers=HEADERS)
        if track_resp.status_code != 200:
            print("❗歌单曲目抓取失败")
            continue

        tracks = track_resp.json().get("items", [])
        for item in tracks:
            if not item or "track" not in item:
                continue

            track_info = item.get("track")
            if not track_info or not isinstance(track_info, dict):
                continue  # 跳过无效 track

            track_name = track_info.get("name", "")
            artists = track_info.get("artists", [])
            if not artists:
                continue

            artist = artists[0]
            artist_name = artist.get("name", "")
            artist_id = artist.get("id")
            if not artist_id:
                continue

            # artist genres检查
            artist_genres = ""
            artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
            artist_resp = requests.get(artist_url, headers=HEADERS)
            if artist_resp.status_code != 200:
                continue
            genre_list = artist_resp.json().get("genres", [])
            if not genre_list:
                print(f"❗跳过无 genre 的歌曲：{track_name} - {artist_name}")
                continue
            artist_genres = ", ".join(genre_list)

            track_url = track_info.get("external_urls", {}).get("spotify", "")
            data_pairs.append({
                "keyword": keyword,
                "playlist_name": playlist_name,
                "playlist_description": playlist_desc,
                "playlist_url": playlist_url,
                "track_name": track_name,
                "artist": artist_name,
                "artist_genres": artist_genres,
                "track_url": track_url
            })

        time.sleep(1)

# 保存数据
df = pd.DataFrame(data_pairs)
df.to_csv("spotify_scene_playlists.csv", index=False, encoding="utf-8-sig")
print("✅数据已保存为spotify_scene_playlists.csv")
