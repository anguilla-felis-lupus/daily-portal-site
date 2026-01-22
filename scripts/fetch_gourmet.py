import requests
import google.generativeai as genai
import os
import urllib.parse
import random

def generate_gourmet_report():
    print("☕ カフェ情報を取得中...")
    
    # APIキーの確認
    hp_api_key = os.environ.get("HOTPEPPER_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not hp_api_key:
        print("エラー: HOTPEPPER_API_KEYがありません")
        return

    # 1. ホットペッパーAPIで「東京のカフェ」を検索
    # ランダムにエリアを変えるなどの工夫も可能ですが、まずは固定で
    url = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
    params = {
        "key": hp_api_key,
        "keyword": "カフェ",
        "address": "東京都", 
        "format": "json",
        "count": 3, # 3件取得
        "order": 4  # おすすめ順
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        shops = data['results']['shop']
    except Exception as e:
        print(f"ホットペッパー取得エラー: {e}")
        return

    # 2. Geminiの設定
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("\n=== ☕ 今日の東京カフェ ===\n")
    
    for shop in shops:
        name = shop['name']
        address = shop['address']
        catch = shop['genre']['catch']
        open_time = shop['open']
        hp_link = shop['urls']['pc']
        
        # Googleマップ検索リンク生成
        query = urllib.parse.quote(f"{name} {address}")
        map_link = f"https://www.google.com/maps/search/?api=1&query={query}"

        print(f"店名: {name}")
        print(f"キャッチ: {catch}")
        print(f"地図: {map_link}")
        
        # 3. Geminiにイメージ描写を依頼（画像生成ではなく、魅力的な紹介文を書かせる）
        # ※実際の画像生成機能は少し複雑なため、今回は「魅力的なテキスト描写」にします
        prompt = f"""
        カフェ「{name}」のキャッチコピーは「{catch}」です。
        このカフェに行きたくなるような、おしゃれな紹介文を1行（50文字以内）で書いてください。
        """
        try:
            res = model.generate_content(prompt)
            print(f"AI紹介: {res.text.strip()}")
        except:
            pass
        print("-" * 20)

if __name__ == "__main__":
    generate_gourmet_report()
