import google.generativeai as genai
import os
import random
import requests # 追加
import json

def get_animal_image(query):
    """Pixabay APIで動物の画像を検索する"""
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        return None
        
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,          # 検索キーワード（動物名）
        "lang": "ja",        # 日本語で検索
        "image_type": "photo", # 写真に限定
        "per_page": 3        # 3枚だけ取得
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["totalHits"] > 0:
            # 最初の画像のURL（webformatURLは程よいサイズ）を返す
            return data["hits"][0]["webformatURL"]
        else:
            # ヒットしなければNone
            return None
            
    except Exception as e:
        print(f"Pixabay検索エラー: {e}")
        return None

def generate_animal_column():
    print("🦁 動物コラムを作成中...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # エラー時は画像なしで返す
        return {"text": "APIキーがありません。", "image": None, "theme": "エラー"}

    genai.configure(api_key=api_key)
    # AIにJSONで返させる設定
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    themes = ["深海生物", "犬の不思議な行動", "最強の昆虫", "絶滅危惧種", "動物園の人気者", "サバンナの生き物"]
    theme_category = random.choice(themes)

    # プロンプトを修正し、JSON形式で「テーマ（生き物名）」と「本文」を分けさせる
    prompt = f"""
    「{theme_category}」というカテゴリから、具体的な生き物を1つ選び、面白くて誰かに話したくなる豆知識コラムを書いてください。
    出力は以下のJSON形式でお願いします。
    
    {{
        "theme_animal": "ここに選んだ生き物の具体的な名前（例: ダイオウイカ）",
        "column_title": "コラムの見出し（30文字以内）",
        "column_text": "コラムの本文（子供でも読める親しみやすい口調で、300文字程度）"
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        # Markdown記号の除去
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
            
        ai_data = json.loads(text)
        
        # AIが決めた生き物名を取得
        animal_name = ai_data.get("theme_animal", theme_category)
        title = ai_data.get("column_title", f"{animal_name}の豆知識")
        body_text = ai_data.get("column_text", "コラム生成失敗")

        print(f"✨ 今日のテーマ: {animal_name} で画像を検索します...")
        
        # その名前で画像を検索
        image_url = get_animal_image(animal_name)

        # 本文、画像URL、タイトルをまとめて返す
        return {
            "title": title,
            "text": body_text,
            "image": image_url,
            "theme": animal_name
        }
        
    except Exception as e:
        print(f"AI生成エラー: {e}")
        return {"title": "エラー", "text": f"生成中にエラーが発生しました: {e}", "image": None, "theme": "エラー"}

if __name__ == "__main__":
    result = generate_animal_column()
    print(f"タイトル: {result['title']}")
    print(f"画像URL: {result['image']}")
    print(f"本文: {result['text'][:50]}...")
