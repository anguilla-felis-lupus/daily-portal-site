import requests
import google.generativeai as genai
import os
import json
import time

# --- 設定: 天気を取得したい都市のリスト ---
CITIES = [
    {"name": "東京", "lat": 35.6812, "lon": 139.7671},
    {"name": "大阪", "lat": 34.6937, "lon": 135.5023},
    {"name": "札幌", "lat": 43.0618, "lon": 141.3545},
    {"name": "北京", "lat": 39.9035, "lon": 116.3880},
    {"name": "モスクワ", "lat": 55.7508, "lon": 37.6172},
    {"name": "ニューヨーク", "lat": 40.7128, "lon": -74.0060},
    {"name": "ロンドン", "lat": 51.5074, "lon": -0.1278},
    {"name": "パリ", "lat": 48.8566, "lon": 2.3522},
    {"name": "シドニー", "lat": -33.8688, "lon": 151.2093},
    {"name": "リオデジャネイロ", "lat": -22.9035, "lon": -43.2096},
    {"name": "カイロ", "lat": 30.0446, "lon": 31.2456},
    {"name": "シンガポール", "lat": 1.3521, "lon": 103.8198}
]
# ----------------------------------------

def get_weather_for_location(lat, lon, name):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        def get_icon(code):
            if code == 0: return "☀️"
            if code <= 3: return "☁️"
            if code <= 48: return "🌫"
            if code <= 67: return "🌧"
            if code <= 77: return "☃️"
            if code <= 82: return "☔"
            if code <= 99: return "⛈"
            return "❓"
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        return {
            "name": name,
            "lat": lat,
            "lon": lon,
            "current_temp": current.get("temperature_2m"),
            "current_icon": get_icon(current.get("weather_code", 0)),
            "today_max": daily.get("temperature_2m_max", [0])[0],
            "today_min": daily.get("temperature_2m_min", [0])[0],
            "rain_prob": daily.get("precipitation_probability_max", [0])[0],
            "tomorrow_icon": get_icon(daily.get("weather_code", [0,0])[1]),
            "tomorrow_max": daily.get("temperature_2m_max", [0])[1],
            "tomorrow_min": daily.get("temperature_2m_min", [0])[1],
        }
    except Exception as e:
        print(f"天気取得エラー ({name}): {e}")
        return None

def get_fortune():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return []

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # ★修正: 出力フォーマットを厳格に指定（ここが重要）
    prompt = """
    今日の「12星座占いランキング」をJSON形式で作成してください。
    運勢の良い順（1位〜12位）に並べてください。
    
    【重要】以下のJSONフォーマット(キー名)を必ず守ってください:
    [
        {"rank": 1, "sign": "おひつじ座", "item": "赤いハンカチ", "comment": "最高の一日！"},
        {"rank": 2, "sign": "おうし座", "item": "コーヒー", "comment": "落ち着いて行動を"}
    ]
    ※ rank, sign, item, comment の4つのキーを必ず含めてください。
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
            
        return json.loads(text)
    except Exception as e:
        print(f"占い生成エラー: {e}")
        return []

def get_lifestyle_data():
    print("☀️ 世界の天気と占いを生成中...")
    
    weather_list = []
    for city in CITIES:
        data = get_weather_for_location(city["lat"], city["lon"], city["name"])
        if data:
            weather_list.append(data)
        time.sleep(0.5)

    return {
        "weather": weather_list[0] if weather_list else None,
        "weather_list": weather_list,
        "fortune": get_fortune()
    }

if __name__ == "__main__":
    print(get_lifestyle_data())
