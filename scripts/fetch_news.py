import feedparser
import google.generativeai as genai
import os
import json

RSS_URL = "[https://news.google.com/rss/search?q=AI+Artificial+Intelligence+when:1d&hl=ja&gl=JP&ceid=JP:ja](https://news.google.com/rss/search?q=AI+Artificial+Intelligence+when:1d&hl=ja&gl=JP&ceid=JP:ja)"
MAX_ARTICLES = 5

def generate_news():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"column": "APIキーエラー", "articles": []}

    # AI設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    print("📰 Googleニュースから記事を取得中...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        return {"column": "記事が見つかりませんでした。", "articles": []}

    # 変数名を 'articles' に統一
    articles = feed.entries[:MAX_ARTICLES]
    
    # プロンプト作成
    prompt = "以下のニュース記事リストを読み、Webサイト掲載用のデータをJSON形式で作成してください。\n"
    prompt += "【要件】\n"
    prompt += "1. `items`: 各記事について『catch_copy(30文字以内の見出し)』と『summary(100文字程度の要約)』を作成。\n"
    prompt += "2. `column`: 記事全体から読み取れる『今日のAI業界の動き』を300文字程度のコラムとして作成。\n\n"
    prompt += "【記事リスト】\n"
    
    for i, entry in enumerate(articles):
        prompt += f"ID:{i} タイトル:{entry.title}\n"

    try:
        # AIに生成させる
        response = model.generate_content(prompt)
        text = response.text

        # エラー回避：Markdown記法が含まれている場合に取り除く処理
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
        
        # JSONテキストをPythonの辞書データに変換
        ai_data = json.loads(text)
        
        # 結果を結合
        final_articles = []
        ai_items = ai_data.get("items", [])
        
        for i, entry in enumerate(articles):
            # AIのデータがあるか確認して結合
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
        # エラー時も最低限の情報を返す
        return {"column": f"エラーが発生しました: {e}", "articles": []}

if __name__ == "__main__":
    result = generate_news()
    print(f"コラム: {result['column'][:50]}...")
    print(f"記事数: {len(result['articles'])}")
