import os
import shutil
from jinja2 import Environment, FileSystemLoader
import datetime
import glob

# 各スクリプトをインポート
import fetch_news
import fetch_market
import fetch_animal
import fetch_entertainment

# 出力先の基本設定
OUTPUT_DIR = "." 
ARCHIVE_ROOT = "archives"

def main():
    print("🚀 サイト生成プロセスを開始します...")

    # --- 修正箇所: 日本時間 (JST) を設定 ---
    # サーバーの時刻に関係なく、強制的に日本時間 (+9時間) を使う
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    
    date_str = now.strftime('%Y-%m-%d') # 例: 2026-01-23
    time_str = now.strftime('%Y-%m-%d %H:%M')
    # ------------------------------------

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
        else:
            news_column = news_result
            news_articles = []
    except Exception as e:
        news_column = f"エラー: {e}"
        news_articles = []

    # --- [Market / 株価] ---
    print("📈 株価データ取得中...")
    # 辞書データ {"summary": "...", "data": {...}} を受け取る
    market_data = fetch_market.generate_market_report()

    # --- [Animal / 動物] ---
    print("🦁 動物コラム生成中...")
    animal_data = fetch_animal.generate_animal_column()
    
    # --- [Entertainment / エンタメ] ---
    print("📚 エンタメデータ取得中...")
    ent_data = fetch_entertainment.get_entertainment_info()

    # 4. HTMLの生成
    env = Environment(loader=FileSystemLoader('templates'))
    
    common_context = {
        "update_time": time_str,
        "archive_list": archive_dates,
        "is_archive": False
    }

    pages = [
        ("index.html", "AI News", "index", {"column": news_column, "article_list": news_articles}),
        ("market.html", "Market", "market", market_data),
        ("animal.html", "Animal", "animal", animal_data),
        ("entertainment.html", "Entertainment", "entertainment", {"manga_list": ent_data['manga'], "anime_list": ent_data['anime']})
    ]

    # (A) 最新版の生成
    for filename, title, active_tab, context in pages:
        template = env.get_template(filename)
        html = template.render(
            title=title,
            active_tab=active_tab,
            **context,
            **common_context
        )
        with open(f'{OUTPUT_DIR}/{filename}', 'w', encoding='utf-8') as f:
            f.write(html)

    # 5. アーカイブの保存
    today_archive_dir = os.path.join(ARCHIVE_ROOT, date_str)
    os.makedirs(today_archive_dir, exist_ok=True)

    print(f"📂 本日のアーカイブを作成中: {today_archive_dir}")

    # (B) アーカイブ版の生成
    common_context["is_archive"] = True
    
    for filename, title, active_tab, context in pages:
        template = env.get_template(filename)
        html = template.render(
            title=title,
            active_tab=active_tab,
            **context,
            **common_context
        )
        with open(f'{today_archive_dir}/{filename}', 'w', encoding='utf-8') as f:
            f.write(html)

    print("✅ サイト生成とアーカイブ保存が完了しました！")

if __name__ == "__main__":
    main()
