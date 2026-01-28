import requests
import time

def get_entertainment_info():
    print("📚 エンタメ情報（漫画・アニメ）を取得中...")
    
    # --- 1. 人気の漫画ランキング (Jikan API) ---
    manga_url = "https://api.jikan.moe/v4/top/manga"
    manga_list = []
    
    try:
        # filter="bypopularity" で人気順, limit=5件
        res = requests.get(manga_url, params={"filter": "bypopularity", "limit": 5}, timeout=10)
        if res.status_code == 200:
            data = res.json()['data']
            for item in data:
                # ジャンルタグのリストを作成
                genres = [g['name'] for g in item.get('genres', [])[:3]]
                
                manga_list.append({
                    "title": item.get('title_japanese') or item.get('title'),
                    "rank": item.get('rank'),
                    "url": item.get('url'),
                    "image": item['images']['jpg']['image_url'],
                    # あらすじを120文字でカット
                    "synopsis": (item.get('synopsis') or "あらすじ情報なし")[:120] + "...",
                    "score": item.get('score', '-'),
                    "genres": genres,
                    "status": item.get('status') # 連載中など
                })
        else:
            print(f"漫画取得エラー: {res.status_code}")
            
    except Exception as e:
        print(f"漫画APIエラー: {e}")

    # API負荷軽減のため少し待機
    time.sleep(2)

    # --- 2. 今放送中の人気アニメ (Jikan API) ---
    anime_url = "https://api.jikan.moe/v4/seasons/now"
    anime_list = []
    
    try:
        # メンバー数（注目度）順にソートしてトップ5を取得
        res = requests.get(anime_url, timeout=10)
        if res.status_code == 200:
            data = res.json()['data']
            sorted_data = sorted(data, key=lambda x: x.get('members', 0), reverse=True)[:5]
            
            for item in sorted_data:
                genres = [g['name'] for g in item.get('genres', [])[:3]]
                
                anime_list.append({
                    "title": item.get('title_japanese') or item.get('title'),
                    "url": item.get('url'),
                    "image": item['images']['jpg']['image_url'],
                    "synopsis": (item.get('synopsis') or "あらすじ情報なし")[:120] + "...",
                    "score": item.get('score', '-'),
                    "episodes": item.get('episodes', '?'),
                    "genres": genres,
                    "source": item.get('source') # 原作（漫画、オリジナル等）
                })
        else:
            print(f"アニメ取得エラー: {res.status_code}")

    except Exception as e:
        print(f"アニメAPIエラー: {e}")

    return {"manga": manga_list, "anime": anime_list}

if __name__ == "__main__":
    # テスト実行用
    info = get_entertainment_info()
    print(f"Manga: {len(info['manga'])}件, Anime: {len(info['anime'])}件")
    if info['anime']:
        print(info['anime'][0])
