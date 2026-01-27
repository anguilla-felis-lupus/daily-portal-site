import requests
import google.generativeai as genai
import os
import json

LAT = 35.6812
LON = 139.7671

def get_weather():
    url = "[https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast)"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "current": "temperature_2m,weather_code",
        "timezone": "Asia/Tokyo"
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
        print(f"天気取得エラー: {e}")
        return None

def get_fortune():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return []

    genai.configure(api_key=api_key)
    # ★重要: ここも確実に 1.5-flash にする
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = """
    今日の「12星座占いランキング」をJSON形式で作成してください。
    運勢の良い順（1位〜12位）に並べてください。
    出力キー: rank, sign, item, comment
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
    print("☀️ 天気と占いを生成中...")
    return {
        "weather": get_weather(),
        "fortune": get_fortune()
    }

if __name__ == "__main__":
    print(get_lifestyle_data())
