import requests
import time

def get_entertainment_info():
    print("📚 エンタメ情報（漫画・アニメ）を取得中...")
    
    # 1. 人気の漫画ランキングを取得 (Jikan API)
    manga_url = "https://api.jikan.moe/v4/top/manga"
    manga_list = []
    
    try:
        # filter="bypopularity" で人気順
        res = requests.get(manga_url, params={"filter": "bypopularity", "limit": 3})
        if res.status_code == 200:
            data = res.json()['data']
            for item in data:
                manga_list.append({
                    "title": item['title_japanese'] if item['title_japanese'] else item['title'],
                    "rank": item['rank'],
                    "url": item['url'],
                    "image": item['images']['jpg']['image_url'],
                    "synopsis": item['synopsis'][:80] + "..." if item['synopsis'] else "あらすじなし"
                })
        else:
            print(f"漫画取得エラー: {res.status_code}")
            
    except Exception as e:
        print(f"漫画APIエラー: {e}")

    # APIの負荷を下げるため少し待機
    time.sleep(1)

    # 2. 今放送中の人気アニメを取得
    anime_url = "https://api.jikan.moe/v4/seasons/now"
    anime_list = []
    
    try:
        # メンバー数（視聴者数）順にソートしてトップ3を取得
        res = requests.get(anime_url)
        if res.status_code == 200:
            data = res.json()['data']
            sorted_data = sorted(data, key=lambda x: x['members'], reverse=True)[:3]
            
            for item in sorted_data:
                anime_list.append({
                    "title": item['title_japanese'] if item['title_japanese'] else item['title'],
                    "url": item['url'],
                    "image": item['images']['jpg']['image_url']
                })
        else:
            print(f"アニメ取得エラー: {res.status_code}")

    except Exception as e:
        print(f"アニメAPIエラー: {e}")

    return {"manga": manga_list, "anime": anime_list}

if __name__ == "__main__":
    # テスト実行用
    info = get_entertainment_info()
    print(info)
