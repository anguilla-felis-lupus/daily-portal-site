import google.generativeai as genai
import os
import random
import requests
import json
import time

def get_animal_image(query):
    """Pixabay APIで動物の画像を検索する"""
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        return None
        
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "lang": "ja",
        "image_type": "photo",
        "per_page": 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["totalHits"] > 0:
            return data["hits"][0]["webformatURL"]
        else:
            return None
    except Exception as e:
        print(f"Pixabay検索エラー: {e}")
        return None

def generate_single_column(theme_category):
    """1つのテーマでコラムと画像を生成する関数"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

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
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
            
        ai_data = json.loads(text)
        
        animal_name = ai_data.get("theme_animal", theme_category)
        title = ai_data.get("column_title", f"{animal_name}の豆知識")
        body_text = ai_data.get("column_text", "コラム生成失敗")

        print(f"✨ テーマ: {animal_name} の画像を検索します...")
        image_url = get_animal_image(animal_name)

        return {
            "headline": title,
            "text": body_text,
            "image": image_url,
            "theme": animal_name
        }
        
    except Exception as e:
        print(f"AI生成エラー: {e}")
        return None

def generate_animal_column():
    print("🦁 動物コラムを作成中...")
    
    # テーマの候補
    themes = [
        "深海生物", "犬の不思議な行動", "猫の秘密", "最強の昆虫", 
        "絶滅危惧種", "動物園の人気者", "サバンナの生き物", 
        "極寒の地の動物", "身近な鳥の意外な生態", "危険な生物",
        "アマゾンの動物", "砂漠の生き物", "身近な生き物の生態",
        "水族館の人気者", "絶滅動物", "生き物たちの特殊能力"
    ]
    
    # ランダムに「2つ」選ぶ（重複なし）
    selected_themes = random.sample(themes, 2)
    
    columns_list = []
    
    for theme in selected_themes:
        col_data = generate_single_column(theme)
        if col_data:
            columns_list.append(col_data)
        # 連続アクセスを防ぐため少し待つ
        time.sleep(2)

    # リスト形式で返す
    return {"columns": columns_list}

if __name__ == "__main__":
    result = generate_animal_column()
    print(f"生成されたコラム数: {len(result['columns'])}")
