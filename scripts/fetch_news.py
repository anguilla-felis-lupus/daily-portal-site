import feedparser
import google.generativeai as genai
import os
import json
import requests
import urllib.parse

# --- 設定エリア --------------------------
# 検索したいキーワードをここに追加します
KEYWORDS = [
    "AI", 
    "人工知能", 
    "機械学習", 
    "ディープラーニング", 
    "フィジカルAI",
    "画像認識",
    "生成AI"
]

# 取得する記事数
MAX_ARTICLES = 5
# ----------------------------------------

def get_rss_url():
    """設定したキーワードと期間(1日以内)から検索用URLを作成する"""
    # キーワードを " OR " でつなぐ (例: "AI OR 機械学習 OR ...")
    query_string = " OR ".join(KEYWORDS)
    
    # 期間指定(when:1d)を追加してグループ化
    # query -> "(AI OR 機械学習 ...) when:1d"
    final_query = f"({query_string}) when:1d"
    
    # URLで使える文字に変換（日本語などをエンコード）
    encoded_query = urllib.parse.quote(final_query)
    
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"

def generate_news():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"column": "APIキーエラー", "articles": []}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-1.5-flash-001',
        generation_config={"response_mime_type": "application/json"}
    )

    rss_url = get_rss_url()
    print(f"📰 Googleニュースから記事を取得中... (キーワード数: {len(KEYWORDS)})")
    
    # ブラウザのふりをする設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        return {"column": f"RSS取得エラー: {e}", "articles": []}

    if not feed.entries:
        print("指定された条件（1日以内）で記事が見つかりませんでした。")
        return {"column": "直近24時間での関連ニュースは見つかりませんでした。", "articles": []}

    articles = feed.entries[:MAX_ARTICLES]
    
    # AIへの指示
    prompt = "以下のニュース記事リストを読み、Webサイト掲載用のデータをJSON形式で作成してください。\n"
    prompt += "【要件】\n"
    prompt += "1. `items`: 各記事について『catch_copy(30文字以内の見出し)』と『summary(100文字程度の要約)』を作成。\n"
    prompt += "2. `column`: 記事全体から読み取れる『今日のAI・テック業界の動き』を300文字程度のコラムとして作成。\n\n"
    prompt += "【記事リスト】\n"
    
    for i, entry in enumerate(articles):
        prompt += f"ID:{i} タイトル:{entry.title}\n"

    try:
        response = model.generate_content(prompt)
        text = response.text

        # JSON整形処理
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
        
        ai_data = json.loads(text)
        
        final_articles = []
        ai_items = ai_data.get("items", [])
        
        for i, entry in enumerate(articles):
            ai_item = ai_items[i] if i < len(ai_items) else {"catch_copy": entry.title, "summary": "要約生成失敗"}
            
            final_articles.append({
                "title": entry.title,
                "url": entry.link,
                "date": entry.published if 'published' in entry else "",
                "headline": ai_item.get("catch_copy", entry.title),
                "summary": ai_item.get("summary", "")
            })

        return {
            "column": ai_data.get("column", "コラム生成失敗"),
            "articles": final_articles
        }

    except Exception as e:
        print(f"エラー発生: {e}")
        return {"column": f"エラーが発生しました: {e}", "articles": []}

if __name__ == "__main__":
    result = generate_news()
    print(f"URL: {get_rss_url()}") # 確認用URL表示
    print(f"コラム: {result['column'][:50]}...")
    print(f"記事数: {len(result['articles'])}")
