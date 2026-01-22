import yfinance as yf
import google.generativeai as genai
import os

def generate_market_report():
    print("📈 株価データを取得中...")
    
    # 1. データ取得（日経平均とドル円）
    tickers = {'^N225': '日経平均', 'JPY=X': 'ドル円'}
    market_data = ""
    
    for symbol, name in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # 直近のデータを取得
            hist = ticker.history(period="2d")
            
            if len(hist) >= 1:
                # 最新の終値
                price = hist['Close'].iloc[-1]
                
                # 前日比の計算（データが2日分あれば）
                if len(hist) >= 2:
                    prev_price = hist['Close'].iloc[-2]
                    change = price - prev_price
                    sign = "+" if change > 0 else ""
                    market_data += f"{name}: {price:.2f} (前日比 {sign}{change:.2f})\n"
                else:
                    market_data += f"{name}: {price:.2f}\n"
                    
        except Exception as e:
            print(f"データ取得エラー ({name}): {e}")

    print(f"取得データ:\n{market_data}")

    # 2. AIに市況コメントを依頼
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    以下の市場データを元に、投資家向けの短い「夕刊コメント」を作成してください。
    数字に基づいた客観的な事実と、それが経済に与える影響を一言で添えてください。
    150文字以内でお願いします。
    
    データ:
    {market_data}
    """
    
    try:
        response = model.generate_content(prompt)
        # データとコメントをセットで返す
        return f"【市況データ】\n{market_data}\n\n【AIコメント】\n{response.text}"
    except Exception as e:
        return f"AI生成エラー: {e}"

if __name__ == "__main__":
    print(generate_market_report())
