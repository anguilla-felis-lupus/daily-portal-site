import requests
import os
import json

def get_movies():
    print("🎬 新作映画情報を取得中...")
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print("TMDBキーがないためスキップします")
        return

    url = "https://api.themoviedb.org/3/movie/upcoming"
    params = {"api_key": api_key, "language": "ja-JP", "region": "JP"}
    
    try:
        res = requests.get(url, params=params)
        data = res.json()
        print("\n--- 🍿 公開予定の映画 ---")
        for movie in data['results'][:3]:
            print(f"タイトル: {movie['title']}")
            print(f"公開日: {movie['release_date']}")
            print(f"あらすじ: {movie['overview'][:50]}...") # 長いのでカット
            print("-" * 10)
    except Exception as e:
        print(f"映画取得エラー: {e}")

def get_anime():
    print("📺 今季のアニメ情報を取得中...")
    # Jikan API (キー不要)
    url = "https://api.jikan.moe/v4/seasons/now"
    
    try:
        res = requests.get(url)
        data = res.json()
        print("\n--- 📺 放送中の人気アニメ ---")
        # 人気順にソートしてトップ3を表示
        sorted_anime = sorted(data['data'], key=lambda x: x['members'], reverse=True)
        
        for anime in sorted_anime[:3]:
            title = anime['title_japanese'] if anime['title_japanese'] else anime['title']
            print(f"タイトル: {title}")
            print(f"URL: {anime['url']}")
            print("-" * 10)
    except Exception as e:
        print(f"アニメ取得エラー: {e}")

if __name__ == "__main__":
    get_movies()
    get_anime()
