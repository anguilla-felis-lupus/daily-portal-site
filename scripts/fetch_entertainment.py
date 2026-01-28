import requests
import time
import os
import json
import google.generativeai as genai

def translate_data(data_dict):
    """取得したエンタメ情報のあらすじをまとめて日本語翻訳する"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return data_dict

    print("🤖 AIによる翻訳・要約を実行中...")
    genai.configure(api_key=api_key)
    # 動作確認済みの軽量モデル
    model = genai.GenerativeModel('gemini-2.5-flash')

    # AIへの指示（データ構造を保ったまま翻訳させる）
    prompt = f"""
    以下のJSONデータに含まれる全ての作品の `synopsis`（あらすじ）を、
    日本語に翻訳し、かつ120文字程度に魅力的に要約してください。
    
    【重要】
    ・出力は入力と同じJSONフォーマットのみにしてください。
    ・`synopsis` 以外の値（title, imageなど）は変更しないでください。
    ・Markdown記法（```jsonなど）は不要です。
    
    入力データ:
    {json.dumps(data_dict, ensure_ascii=False)}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # JSONクリーニング
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
            
        return json.loads(text)
    except Exception as e:
        print(f"翻訳エラー: {e}")
        return data_dict # 失敗したら元の（英語の）データを返す

def get_entertainment_info():
    print("📚 エンタメ情報（漫画・アニメ）を取得中...")
    
    manga_list = []
    anime_list = []

    # --- 1. 人気の漫画ランキング (Jikan API) ---
    try:
        res = requests.get("https://api.jikan.moe/v4/top/manga", 
                         params={"filter": "bypopularity", "limit": 5}, timeout=10)
        if res.status_code == 200:
            for item in res.json()['data']:
                genres = [g['name'] for g in item.get('genres', [])[:3]]
                manga_list.append({
                    "title": item.get('title_japanese') or item.get('title'),
                    "rank": item.get('rank'),
                    "url": item.get('url'),
                    "image": item['images']['jpg']['image_url'],
                    "synopsis": item.get('synopsis') or "あらすじ情報なし",
                    "score": item.get('score', '-'),
                    "genres": genres,
                    "status": item.get('status')
                })
    except Exception as e:
        print(f"漫画APIエラー: {e}")

    time.sleep(2) # 負荷軽減

    # --- 2. 今放送中の人気アニメ (Jikan API) ---
    try:
        res = requests.get("https://api.jikan.moe/v4/seasons/now", timeout=10)
        if res.status_code == 200:
            data = res.json()['data']
            sorted_data = sorted(data, key=lambda x: x.get('members', 0), reverse=True)[:5]
            
            for item in sorted_data:
                genres = [g['name'] for g in item.get('genres', [])[:3]]
                anime_list.append({
                    "title": item.get('title_japanese') or item.get('title'),
                    "url": item.get('url'),
                    "image": item['images']['jpg']['image_url'],
                    "synopsis": item.get('synopsis') or "あらすじ情報なし",
                    "score": item.get('score', '-'),
                    "episodes": item.get('episodes', '?'),
                    "genres": genres,
                    "source": item.get('source')
                })
    except Exception as e:
        print(f"アニメAPIエラー: {e}")

    # データをまとめて翻訳へ
    raw_data = {"manga": manga_list, "anime": anime_list}
    
    # どちらか片方でもデータがあれば翻訳を試みる
    if manga_list or anime_list:
        return translate_data(raw_data)
    else:
        return raw_data

if __name__ == "__main__":
    info = get_entertainment_info()
    print(f"Manga: {len(info['manga'])}件, Anime: {len(info['anime'])}件")
    if info['anime']:
        print(f"Sample: {info['anime'][0]['synopsis'][:50]}...")
