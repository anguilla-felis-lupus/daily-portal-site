import feedparser
import google.generativeai as genai
import os
import json
import requests # 追加: データを確実に取るために使用

# 検索クエリ（少し緩めて確実に記事がヒットするように変更）
RSS_URL = "https://news.google.com/rss/search?q=AI+Artificial+Intelligence&hl=ja&gl=JP&ceid=JP:ja"
MAX_ARTICLES = 5

def generate_news():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"column": "APIキーエラー", "articles": []}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    print("📰 Googleニュースから記事を取得中...")
    
    # --- 修正ポイント: ブラウザのふりをしてアクセスする ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # requestsを使ってデータを取得してから解析する
        response = requests.get(RSS_URL, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        return {"column": f"RSS取得エラー: {e}", "articles": []}
    # ------------------------------------------------

    if not feed.entries:
        # それでも取れない場合のデバッグ用
        print("RSSのエントリーが空でした。")
        return {"column": "記事が見つかりませんでした（Google Newsへのアクセスがブロックされた可能性があります）。", "articles": []}

    # 変数名を 'articles' に統一
    articles = feed.entries[:MAX_ARTICLES]
    
    prompt = "以下のニュース記事リストを読み、Webサイト掲載用のデータをJSON形式で作成してください。\n"
    prompt += "【要件】\n"
    prompt += "1. `items`: 各記事について『catch_copy(30文字以内の見出し)』と『summary(100文字程度の要約)』を作成。\n"
    prompt += "2. `column`: 記事全体から読み取れる『今日のAI業界の動き』を300文字程度のコラムとして作成。\n\n"
    prompt += "【記事リスト】\n"
    
    for i, entry in enumerate(articles):
        prompt += f"ID:{i} タイトル:{entry.title}\n"

    try:
        response = model.generate_content(prompt)
        text = response.text

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
    print(f"コラム: {result['column'][:50]}...")
    print(f"記事数: {len(result['articles'])}")
