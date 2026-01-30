import yfinance as yf
import google.generativeai as genai
import os
import datetime
import requests

def get_fear_greed_index():
    """CNNのFear & Greed Indexを取得する"""
    print("😨 恐怖指数(Fear & Greed)を取得中...")
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            fg_data = data.get('fear_and_greed', {})
            score = fg_data.get('score')
            rating = fg_data.get('rating')
            
            if score is not None:
                return {"score": round(float(score), 1), "rating": rating}
    except Exception as e:
        print(f"Fear & Greed取得エラー: {e}")
        
    return None

def generate_market_report():
    print("📈 市場データと履歴を取得中...")
    
    targets = {
        'nikkei': {'symbol': '^N225', 'name': '日経平均'},
        'sp500': {'symbol': '^GSPC', 'name': '米国S&P500'},
        'usdjpy': {'symbol': 'JPY=X', 'name': 'ドル円'},
        'gold': {'symbol': 'GC=F', 'name': '金先物'},
        'btc': {'symbol': 'BTC-JPY', 'name': 'ビットコイン'}
    }
    
    chart_data = {}
    text_data = ""

    for key, item in targets.items():
        try:
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(period="1mo")
            
            if len(hist) > 0:
                dates = [d.strftime('%m/%d') for d in hist.index]
                prices = hist['Close'].tolist()
                current_price = prices[-1]
                
                diff = 0
                sign = ""
                if len(prices) >= 2:
                    prev_price = prices[-2]
                    diff = current_price - prev_price
                    sign = "+" if diff > 0 else ""

                chart_data[key] = {
                    'name': item['name'],
                    'current': f"{current_price:,.2f}",
                    'diff': f"{sign}{diff:,.2f}",
                    'dates': dates,
                    'prices': prices,
                    'color': 'red' if diff > 0 else 'blue'
                }
                
                text_data += f"{item['name']}: {current_price:.2f} (前日比 {sign}{diff:.2f})\n"
                
        except Exception as e:
            print(f"エラー ({item['name']}): {e}")

    # 恐怖指数の取得
    fg_index = get_fear_greed_index()
    if fg_index:
        text_data += f"\nFear & Greed Index: {fg_index['score']} ({fg_index['rating']})"

    api_key = os.environ.get("GEMINI_API_KEY")
    ai_comment = "APIキーがありません"
    
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""
        以下の市場データを元に、投資家向けの「今日の市況概況」を書いてください。
        特に「Fear & Greed Index（恐怖指数）」の値に触れ、
        市場が今「強気（買い）」なのか「弱気（恐怖）」なのかを分析してください。
        全体で200文字以内でまとめてください。
        
        データ:
        {text_data}
        """
        try:
            response = model.generate_content(prompt)
            ai_comment = response.text
        except Exception as e:
            ai_comment = f"AI生成エラー: {e}"

    return {
        "summary": ai_comment,
        "data": chart_data,
        "fg_index": fg_index # テンプレートに渡すデータを追加
    }

if __name__ == "__main__":
    result = generate_market_report()
    print(result['summary'])
    print(f"Fear & Greed: {result.get('fg_index')}")
