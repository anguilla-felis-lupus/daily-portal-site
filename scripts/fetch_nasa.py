import requests
import google.generativeai as genai
import os
import json

def get_nasa_data():
    """NASA APODを取得して日本語化する"""
    print("🚀 NASA APODデータを取得中...")
    
    # 1. NASA APIからデータ取得 (DEMO_KEY利用: 登録不要の無料枠)
    url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"NASA API Error: {response.status_code}")
            return None
            
        data = response.json()
        
        # 必要なデータを抽出
        title_en = data.get("title", "")
        explanation_en = data.get("explanation", "")
        media_type = data.get("media_type", "image") # image か video
        media_url = data.get("url", "")
        
        # 2. Geminiで日本語翻訳・要約
        api_key = os.environ.get("GEMINI_API_KEY")
        
        title_jp = title_en
        text_jp = "解説の翻訳に失敗しました。"
        
        if api_key:
            genai.configure(api_key=api_key)
            # 動作確認済みの軽量モデルを使用
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            prompt = f"""
            以下のNASA「今日の宇宙写真」の解説を、日本の一般読者向けにわかりやすく翻訳・要約してください。
            専門用語はなるべく噛み砕いて、知的好奇心をそそる文章にしてください。
            
            Title: {title_en}
            Explanation: {explanation_en}
            
            出力は以下のJSON形式のみでお願いします:
            {{
                "title": "日本語タイトル",
                "text": "日本語解説文(200文字程度)"
            }}
            """
            
            try:
                ai_res = model.generate_content(prompt)
                raw_text = ai_res.text
                # JSONクリーニング
                if "```json" in raw_text:
                    raw_text = raw_text.replace("```json", "").replace("```", "")
                elif "```" in raw_text:
                    raw_text = raw_text.replace("```", "")
                
                ai_data = json.loads(raw_text)
                title_jp = ai_data.get("title", title_en)
                text_jp = ai_data.get("text", explanation_en)
            except Exception as e:
                print(f"翻訳エラー: {e}")
                text_jp = explanation_en # 失敗時は英語のまま

        return {
            "title": title_jp,
            "text": text_jp,
            "url": media_url,
            "media_type": media_type
        }

    except Exception as e:
        print(f"NASA取得プロセスエラー: {e}")
        return None

if __name__ == "__main__":
    print(get_nasa_data())
