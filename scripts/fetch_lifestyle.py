import requests
import google.generativeai as genai
import os
import json

# --- 設定エリア: あなたの地域の座標 ---
# Googleマップで右クリックするとわかります
LAT = 35.6812  # 緯度 (例: 東京駅)
LON = 139.7671 # 経度 (例: 東京駅)
# -----------------------------------

def get_weather():
    """Open-Meteo APIから天気予報を取得"""
    # 登録不要・無料で使えるAPI
    url = "https://api.open-meteo.com/v1/forecast"
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
        
        # 天気コード(WMO)を絵文字に変換
        # 0:快晴, 1-3:曇り, 45-48:霧, 51-67:雨, 71-77:雪, 80-82:激しい雨, 95-99:雷雨
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
        
        # 必要なデータだけ抽出
        return {
            "current_temp": current.get("temperature_2m"),
            "current_icon": get_icon(current.get("weather_code", 0)),
            # 今日の予報
            "today_max": daily.get("temperature_2m_max", [0])[0],
            "today_min": daily.get("temperature_2m_min", [0])[0],
            "rain_prob": daily.get("precipitation_probability_max", [0])[0],
            # 明日の予報
            "tomorrow_icon": get_icon(daily.get("weather_code", [0,0])[1]),
            "tomorrow_max": daily.get("temperature_2m_max", [0])[1],
            "tomorrow_min": daily.get("temperature_2m_min", [0])[1],
        }
    except Exception as e:
        print(f"天気取得エラー: {e}")
        return None

def get_fortune():
    """Geminiで12星座占いを作成"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return []

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = """
    今日の「12星座占いランキング」をJSON形式で作成してください。
    運勢の良い順（1位〜12位）に並べてください。
    
    出力フォーマット:
    [
        {"rank": 1, "sign": "おひつじ座", "item": "赤いハンカチ", "comment": "最高の一日になりそう！"},
        ...
    ]
    rank, sign, item, comment のキーを必ず含めてください。
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Markdown削除処理
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
    # テスト実行用
    print(get_lifestyle_data())
