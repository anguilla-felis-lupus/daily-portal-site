import google.generativeai as genai
import os
import random

def generate_animal_column():
    print("🦁 動物コラムを作成中...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("APIキーがありません")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # ランダム性を出すために、テーマをいくつか用意
    themes = ["珍しい深海生物", "意外と知らない犬の行動", "最強の昆虫", "絶滅危惧種の豆知識", "動物園の人気者", "水族館の人気者","意外と知らない猫の行動", "絶滅動物の生態", "危険生物の生態", "身近にいる生き物たちの生態"]
    theme = random.choice(themes)

    prompt = f"""
    「{theme}」というテーマで、面白くて誰かに話したくなる動物の豆知識コラムを1つ書いてください。
    
    条件:
    1. 対象とする動物の名前を見出しにすること。
    2. 子供でも読める親しみやすい口調（〜だよ、〜なんだ、など）にすること。
    3. 全体で300文字程度にまとめること。
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI生成エラー: {e}"

if __name__ == "__main__":
    print(generate_animal_column())
