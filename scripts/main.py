import os
from jinja2 import Environment, FileSystemLoader
import datetime

# 作成したスクリプトをインポート
# ※ファイル名が違う場合は合わせてください
import fetch_news
import fetch_market
import fetch_animal
import fetch_entertainment

# データを保存するHTMLの出力先（ルートディレクトリ）
OUTPUT_DIR = "." 

def main():
    print("🚀 サイト生成プロセスを開始します...")

    # 1. データの収集
    # -----------------------
    
    # (A) AIニュース
    # ※fetch_news.generate_news() が return するように少し修正が必要ですが、
    # 一旦ここでは「printするだけの関数」ではなく「データを返す関数」として扱います。
    # ★重要: fetch_news.py などの各ファイルを「データをreturnする形」に直す必要がありますが、
    # 今回は簡易的に main.py の中でロジックを呼ぶか、各ファイルを修正します。
    # 
    # 取り急ぎ、まずは「各スクリプトが動くこと」を優先し、
    # 実際にはHTML生成に必要なデータを受け取る処理を書きます。
    
    # 時間取得
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 2. テンプレートエンジンの準備
    # -----------------------
    env = Environment(loader=FileSystemLoader('templates'))
    
    # 3. ページごとの生成処理
    # -----------------------

    # --- [TOP / AIニュース] ---

    print("📰 ニュースデータ取得中...")
    try:
        news_result = fetch_news.generate_news()
        
        if isinstance(news_result, dict):
            # AIが書いたコラム
            news_column = news_result.get('column', '')
            # 要約・リンク付きの記事リスト
            news_articles = news_result.get('articles', [])
        else:
            news_column = "データの取得に失敗しました"
            news_articles = []
    except Exception as e:
        news_column = f"取得エラー: {e}"
        news_articles = []

    # --- [Market / 株価] ---
    print("📈 株価データ取得中...")
    market_text = fetch_market.generate_market_report() # ※あとでreturnを追加

    # --- [Animal / 動物] ---
    print("🦁 動物コラム生成中...")
    animal_text = fetch_animal.generate_animal_column() # ※あとでreturnを追加
    
    # --- [Entertainment / 漫画] ---
    print("📚 エンタメデータ取得中...")
    ent_data = fetch_entertainment.get_entertainment_info()

    # 4. HTMLのレンダリング（書き出し）
    # -----------------------
    
    # 共通データ
    common_context = {
        "update_time": now
    }

    # (1) index.html (AI News)
    template = env.get_template('index.html')
    html = template.render(
        title="AI News",
        active_tab="index",
        column=news_column,         # コラム本文
        article_list=news_articles, # 記事リスト
        **common_context
    )
    with open(f'{OUTPUT_DIR}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # (2) market.html
    template = env.get_template('market.html')
    html = template.render(
        title="Market",
        active_tab="market",
        content=market_text,
        **common_context
    )
    with open(f'{OUTPUT_DIR}/market.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # (3) animal.html
    template = env.get_template('animal.html')
    html = template.render(
        title="Animal",
        active_tab="animal",
        content=animal_text,
        **common_context
    )
    with open(f'{OUTPUT_DIR}/animal.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # (4) entertainment.html
    template = env.get_template('entertainment.html')
    html = template.render(
        title="Entertainment",
        active_tab="entertainment",
        manga_list=ent_data['manga'],
        anime_list=ent_data['anime'],
        **common_context
    )
    with open(f'{OUTPUT_DIR}/entertainment.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ すべてのHTML生成が完了しました！")

if __name__ == "__main__":
    main()
