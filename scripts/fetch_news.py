import feedparser
import google.generativeai as genai
import os

# --- 設定 ---
# 検索したいキーワード（ここを変えれば別のニュースになります）
RSS_URL = "https://news.google.com/rss/search?q=AI+Artificial+Intelligence+when:1d&hl=ja&gl=JP&ceid=JP:ja"
# 取得する記事数
MAX_ARTICLES = 5

def generate_news():
    # 1. APIキーの準備
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("APIキーが設定されていません")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 2. RSSからニュースを取得
    print("📰 Googleニュースから記事を取得中...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("記事が見つかりませんでした。")
        return

    # 3. 記事データを整形
    articles = feed.entries[:MAX_ARTICLES]
    news_text = ""
    
    print(f"✅ {len(articles)}件の記事を取得しました。AIに要約を依頼します...")

    # AIへの指示（プロンプト）を作る
    prompt = "以下のニュース記事リストを元に、Webサイトに掲載するための記事を作成してください。\n"
    prompt += "各記事について『キャッチーな見出し（30文字以内）』と『簡潔な要約（100文字以内）』を作成してください。\n"
    prompt += "出力は読みやすいテキスト形式でお願いします。\n\n"
    
    for i, entry in enumerate(articles):
        title = entry.title
        link = entry.link
        prompt += f"記事{i+1} タイトル: {title}\nURL: {link}\n---\n"

    # 4. AIに生成させる
    try:
        response = model.generate_content(prompt)
        print("\n=== 🦁 AIニュース記者の原稿 ===\n")
        print(response.text)
        print("\n==============================")
        
    except Exception as e:
        print(f"AI生成エラー: {e}")

if __name__ == "__main__":
    generate_news()
