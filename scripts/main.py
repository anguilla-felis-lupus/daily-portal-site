import os
import shutil
from jinja2 import Environment, FileSystemLoader
import datetime
import glob
import time  # 時間制御用

# 各スクリプトをインポート
import fetch_news
import fetch_market
import fetch_animal
import fetch_entertainment
import fetch_lifestyle
import fetch_nasa

# 出力先の基本設定
OUTPUT_DIR = "." 
ARCHIVE_ROOT = "archives"

def main():
    print("🚀 サイト生成プロセスを開始します...")

    # 1. 日本時間 (JST) の設定
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%Y-%m-%d %H:%M')

    print(f"🕒 日本時間: {time_str} の更新を開始します")

    # 2. 過去のアーカイブ一覧を取得
    archive_dates = []
    if os.path.exists(ARCHIVE_ROOT):
        dirs = [d for d in os.listdir(ARCHIVE_ROOT) if os.path.isdir(os.path.join(ARCHIVE_ROOT, d))]
        archive_dates = sorted(dirs, reverse=True)
    
    if date_str not in archive_dates:
        archive_dates.insert(0, date_str)

    # 3. データの収集
    
    # --- [TOP / AIニュース] ---
    print("📰 ニュースデータ取得中...")
    try:
        news_result = fetch_news.generate_news()
        if isinstance(news_result, dict):
            news_column = news_result.get('column', '')
            news_articles = news_result.get('articles', [])
            # ★追加: ワードクラウド画像ファイル名を取得
            news_wordcloud = news_result.get('wordcloud', None) 
        else:
            news_column = news_result
            news_articles = []
            news_wordcloud = None
    except Exception as e:
        print(f"ニュース取得エラー: {e}")
        news_column = "取得エラー"
        news_articles = []
        news_wordcloud = None
    
    print("☕ 30秒休憩中...(API制限を確実に回避)")
    time.sleep(30)

    # --- [Market / 株価] ---
    print("📈 株価データ取得中...")
    try:
        market_data = fetch_market.generate_market_report()
    except Exception as e:
        print(f"株価取得エラー: {e}")
        market_data = {"summary": "取得エラー", "data": {}}

    print("☕ 30秒休憩中...(API制限を確実に回避)")
    time.sleep(30)

    # --- [Animal / 動物] ---
    print("🦁 動物コラム生成中...")
    try:
        animal_data = fetch_animal.generate_animal_column()
    except Exception as e:
        print(f"動物取得エラー: {e}")
        animal_data = {"columns": []}
    
    print("☕ 30秒休憩中...(API制限を確実に回避)")
    time.sleep(30)

    # --- [NASA / 宇宙] ---
    print("🚀 NASAデータを取得中...")
    try:
        nasa_data = fetch_nasa.get_nasa_data()
        if animal_data:
            animal_data['nasa'] = nasa_data
    except Exception as e:
        print(f"NASA取得エラー: {e}")
    
    print("☕ 30秒休憩中...(API制限を確実に回避)")
    time.sleep(30)
    
    # --- [Entertainment / エンタメ] ---
    print("📚 エンタメデータ取得中...")
    try:
        ent_data = fetch_entertainment.get_entertainment_info()
    except Exception as e:
        print(f"エンタメ取得エラー: {e}")
        ent_data = {"manga": [], "anime": []}

    print("☕ 10秒休憩中...")
    time.sleep(10) 

    # --- [Lifestyle / 天気・占い] ---
    print("☀️ 生活情報データを取得中...")
    try:
        lifestyle_data = fetch_lifestyle.get_lifestyle_data()
    except Exception as e:
        print(f"生活情報取得エラー: {e}")
        lifestyle_data = {"weather": None, "fortune": [], "weather_list": []}


    # 4. HTMLの生成設定
    env = Environment(loader=FileSystemLoader('templates'))
    
    common_context = {
        "update_time": time_str,
        "archive_list": archive_dates,
        "is_archive": False
    }

    pages = [
        # ★修正: wordcloud をテンプレートに渡す
        ("index.html", "AI News", "index", {"column": news_column, "article_list": news_articles, "wordcloud": news_wordcloud}),
        ("market.html", "Market", "market", market_data),
        ("animal.html", "Animal", "animal", animal_data),
        ("entertainment.html", "Entertainment", "entertainment", {"manga_list": ent_data['manga'], "anime_list": ent_data['anime']}),
        ("lifestyle.html", "Lifestyle", "lifestyle", lifestyle_data)
    ]

    # (A) 最新版の生成
    for filename, title, active_tab, context in pages:
        try:
            template = env.get_template(filename)
            html = template.render(
                title=title,
                active_tab=active_tab,
                **context,
                **common_context
            )
            with open(f'{OUTPUT_DIR}/{filename}', 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(f"HTML生成エラー ({filename}): {e}")

    # 5. アーカイブの保存
    today_archive_dir = os.path.join(ARCHIVE_ROOT, date_str)
    os.makedirs(today_archive_dir, exist_ok=True)

    print(f"📂 本日のアーカイブを作成中: {today_archive_dir}")

    # ★追加: ワードクラウド画像があれば、アーカイブフォルダにもコピーする
    if news_wordcloud and os.path.exists(news_wordcloud):
        try:
            shutil.copy(news_wordcloud, os.path.join(today_archive_dir, news_wordcloud))
            print("✅ ワードクラウド画像をアーカイブに保存しました")
        except Exception as e:
            print(f"画像コピーエラー: {e}")

    # (B) アーカイブ版の生成
    common_context["is_archive"] = True
    
    for filename, title, active_tab, context in pages:
        try:
            template = env.get_template(filename)
            html = template.render(
                title=title,
                active_tab=active_tab,
                **context,
                **common_context
            )
            with open(f'{today_archive_dir}/{filename}', 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(f"アーカイブ生成エラー ({filename}): {e}")

    print("✅ サイト生成とアーカイブ保存が完了しました！")

if __name__ == "__main__":
    main()
