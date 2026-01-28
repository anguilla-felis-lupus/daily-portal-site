import feedparser
import google.generativeai as genai
import os
import json
import requests
import urllib.parse
from wordcloud import WordCloud
from janome.tokenizer import Tokenizer

# --- 設定エリア --------------------------
# 検索したいキーワードをここに追加します
KEYWORDS = [
    "AI", 
    "人工知能", 
    "機械学習", 
    "ディープラーニング", 
    "フィジカルAI",
    "画像認識",
    "生成AI",
    "LLM",
    "マルチモーダルAI",
    "AGI"
]

# 取得する記事数 (5 -> 10に変更)
MAX_ARTICLES = 10

# ワードクラウド用日本語フォントの設定
FONT_URL = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
FONT_PATH = "NotoSansCJKjp-Regular.otf"
# ----------------------------------------

def download_font():
    """ワードクラウド用の日本語フォントをダウンロードする"""
    if not os.path.exists(FONT_PATH):
        print("🔤 日本語フォントをダウンロード中...")
        try:
            response = requests.get(FONT_URL, timeout=30)
            with open(FONT_PATH, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"フォントダウンロードエラー: {e}")

def create_wordcloud(text_list):
    """ニュースのテキストからワードクラウド画像を生成する"""
    print("☁️ ワードクラウドを生成中...")
    
    # 1. テキストを結合
    full_text = " ".join(text_list)
    
    # 2. 形態素解析で名詞だけ抽出 (Janome使用)
    t = Tokenizer()
    tokens = t.tokenize(full_text)
    words = []
    
    # 除外したい一般的な単語（ストップワード）
    stop_words = ["こと", "もの", "ため", "よう", "それ", "これ", "さん", "の", "ん", "AI", "活用", "対応", "開発", "発表", "提供", "機能", "サービス", "技術", "利用", "日本", "企業"]
    
    for token in tokens:
        # 名詞のみ抽出し、かつストップワードに含まれないもの
        if token.part_of_speech.split(',')[0] == '名詞' and token.surface not in stop_words:
            words.append(token.surface)
    
    if not words:
        print("ワードクラウド生成用の単語が見つかりませんでした。")
        return None

    # 3. スペース区切りの文字列にする
    text_space = " ".join(words)
    
    # 4. フォントの準備
    download_font()
    
    # 5. 画像生成
    try:
        wc = WordCloud(
            font_path=FONT_PATH if os.path.exists(FONT_PATH) else None, # フォント指定
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis', # 色使い
            regexp=r"[\w']+"    # 日本語対応のための正規表現
        )
        wc.generate(text_space)
        
        # 画像を保存
        output_filename = "wordcloud.png"
        wc.to_file(output_filename)
        return output_filename
    except Exception as e:
        print(f"ワードクラウド生成エラー: {e}")
        return None

def get_rss_url():
    """設定したキーワードと期間(1日以内)から検索用URLを作成する"""
    query_string = " OR ".join(KEYWORDS)
    final_query = f"({query_string}) when:1d"
    encoded_query = urllib.parse.quote(final_query)
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"

def generate_news():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"column": "APIキーエラー", "articles": [], "wordcloud": None}

    genai.configure(api_key=api_key)
    # 安定して動作する gemini-2.5-flash-lite を指定
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    rss_url = get_rss_url()
    print(f"📰 Googleニュースから記事を取得中... (キーワード数: {len(KEYWORDS)})")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        return {"column": f"RSS取得エラー: {e}", "articles": [], "wordcloud": None}

    if not feed.entries:
        print("指定された条件（1日以内）で記事が見つかりませんでした。")
        return {"column": "直近24時間での関連ニュースは見つかりませんでした。", "articles": [], "wordcloud": None}

    articles = feed.entries[:MAX_ARTICLES]
    
    # AIへの指示
    prompt = "以下のニュース記事リストを読み、Webサイト掲載用のデータをJSON形式で作成してください。\n"
    prompt += "【要件】\n"
    prompt += "1. `items`: 各記事について『catch_copy(30文字以内の見出し)』と『summary(100文字程度の要約)』を作成。\n"
    prompt += "2. `column`: 記事全体から読み取れる『今日のAI・テック業界の動き』を300文字程度のコラムとして作成。\n\n"
    prompt += "【記事リスト】\n"
    
    for i, entry in enumerate(articles):
        prompt += f"ID:{i} タイトル:{entry.title}\n"

    ai_data = {}
    try:
        response = model.generate_content(prompt)
        text = response.text

        # JSON整形処理
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.replace("```", "")
        
        ai_data = json.loads(text)
        
    except Exception as e:
        print(f"AI生成エラー: {e}")
        ai_data = {"column": f"AI生成エラー: {e}", "items": []}

    final_articles = []
    ai_items = ai_data.get("items", [])
    
    # ワードクラウド生成用のテキストリスト
    text_for_wordcloud = []
    
    for i, entry in enumerate(articles):
        ai_item = ai_items[i] if i < len(ai_items) else {"catch_copy": entry.title, "summary": "要約生成失敗"}
        
        headline = ai_item.get("catch_copy", entry.title)
        summary = ai_item.get("summary", "")

        final_articles.append({
            "title": entry.title,
            "url": entry.link,
            "date": entry.published if 'published' in entry else "",
            "headline": headline,
            "summary": summary
        })
        
        # タイトル、見出し、要約をワードクラウドの素材に追加
        text_for_wordcloud.append(entry.title)
        text_for_wordcloud.append(headline)
        text_for_wordcloud.append(summary)

    # ワードクラウド画像の生成を実行
    wc_image_file = create_wordcloud(text_for_wordcloud)

    return {
        "column": ai_data.get("column", "コラム生成失敗"),
        "articles": final_articles,
        "wordcloud": wc_image_file # 生成された画像ファイル名を追加
    }

if __name__ == "__main__":
    result = generate_news()
    print(f"URL: {get_rss_url()}")
    print(f"コラム: {result['column'][:50]}...")
    print(f"記事数: {len(result['articles'])}")
    print(f"ワードクラウド画像: {result['wordcloud']}")
