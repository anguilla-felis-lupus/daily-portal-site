import feedparser
import google.generativeai as genai
import os
import json

# --- 設定 ---
# 検索したいキーワード（ここを変えれば別のニュースになります）
RSS_URL = "https://news.google.com/rss/search?q=AI+Artificial+Intelligence+when:1d&hl=ja&gl=JP&ceid=JP:ja"
# 取得する記事数
MAX_ARTICLES = 5

def generate_news():
    # 1. APIキーの準備
    api_key = os.environ.get("GEMINI_API_KEY")
    # エラー時は辞書形式でエラーメッセージを返す
    if not api_key:
        return {"summary": "APIキーが設定されていません。", "articles": []}

    genai.configure(api_key=api_key)
    # JSON形式で
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    # 2. RSSからニュースを取得
    print("📰 Googleニュースから記事を取得中...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        return {"column": "記事が見つかりませんでした。", "articles": []}

    # 3. 記事データを整形
    raw_articles = feed.entries[:MAX_ARTICLES]
    
    print(f"✅ {len(articles)}件の記事を取得しました。AIに要約を依頼します...")

    # プロンプト作成
    prompt = "以下のニュース記事リストを読み、Webサイト掲載用のデータをJSON形式で作成してください。\n"
    prompt += "【要件】\n"
    prompt += "1. `items`: 各記事について『catch_copy(30文字以内の見出し)』と『summary(100文字程度の要約)』を作成。\n"
    prompt += "2. `column`: 記事全体から読み取れる『今日のAI業界の動き』を300文字程度のコラムとして作成。\n\n"
    prompt += "【記事リスト】\n"

    for i, entry in enumerate(raw_articles):
        prompt += f"ID:{i} タイトル:{entry.title}\n"

    try:
        # AIに生成させる
        response = model.generate_content(prompt)
        
        # JSONテキストをPythonの辞書データに変換
        ai_data = json.loads(response.text)
        
        # RSSの元データ(URLなど)と、AIの生成データ(要約)を合体させる
        final_articles = []
        ai_items = ai_data.get("items", [])
        
        for i, entry in enumerate(raw_articles):
            # AIの生成データがあればそれを使う、なければ空文字
            ai_item = ai_items[i] if i < len(ai_items) else {"catch_copy": entry.title, "summary": "要約生成失敗"}
            
            final_articles.append({
                "title": entry.title,
                "url": entry.link,
                "date": entry.published if 'published' in entry else "",
                "headline": ai_item.get("catch_copy", entry.title), # AI見出し
                "summary": ai_item.get("summary", "")               # AI要約
            })

        return {
            "column": ai_data.get("column", "コラム生成失敗"),
            "articles": final_articles
        }

    except Exception as e:
        print(f"エラー発生: {e}")
        return {"column": f"エラー: {e}", "articles": []}

if __name__ == "__main__":
    result = generate_news()
    print(f"コラム: {result['column'][:50]}...")
    print(f"記事数: {len(result['articles'])}")
