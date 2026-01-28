import yfinance as yf
import google.generativeai as genai
import os
import datetime

def generate_market_report():
    print("📈 市場データと履歴を取得中...")
    
    # 取得したい銘柄リスト
    targets = {
        'nikkei': {'symbol': '^N225', 'name': '日経平均'},
        'sp500': {'symbol': '^GSPC', 'name': '米国S&P500'},
        'usdjpy': {'symbol': 'JPY=X', 'name': 'ドル円'},
        'gold': {'symbol': 'GC=F', 'name': '金先物'},
        'btc': {'symbol': 'BTC-JPY', 'name': 'ビットコイン'}
    }
    
    chart_data = {}  # グラフ用データ
    text_data = ""   # AIへの入力用テキスト

    for key, item in targets.items():
        try:
            ticker = yf.Ticker(item['symbol'])
            # 過去1ヶ月分のデータを取得
            hist = ticker.history(period="1mo")
            
            if len(hist) > 0:
                # 1. グラフ用のデータ作成 (日付と終値のリスト)
                # 日付を "1/26" のような文字列に変換
                dates = [d.strftime('%m/%d') for d in hist.index]
                prices = hist['Close'].tolist()
                
                # 最新価格
                current_price = prices[-1]
                
                # 前日比
                diff = 0
                sign = ""
                if len(prices) >= 2:
                    prev_price = prices[-2]
                    diff = current_price - prev_price
                    sign = "+" if diff > 0 else ""

                # 保存
                chart_data[key] = {
                    'name': item['name'],
                    'current': f"{current_price:,.2f}",
                    'diff': f"{sign}{diff:,.2f}",
                    'dates': dates,   # 横軸（日付）
                    'prices': prices, # 縦軸（価格）
                    'color': 'red' if diff > 0 else 'blue' # 上昇なら赤、下落なら青
                }
                
                # AI用テキストの蓄積
                text_data += f"{item['name']}: {current_price:.2f} (前日比 {sign}{diff:.2f})\n"
                
        except Exception as e:
            print(f"エラー ({item['name']}): {e}")

    # AIにコメントを書かせる
    api_key = os.environ.get("GEMINI_API_KEY")
    ai_comment = "APIキーがありません"
    
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        以下の市場データを元に、投資家向けの「今日の市況概況」を書いてください。
        特に大きな動きがある銘柄に注目し、経済への影響を一言加えてください。
        全体で200文字以内でまとめてください。
        
        データ:
        {text_data}
        """
        try:
            response = model.generate_content(prompt)
            ai_comment = response.text
        except Exception as e:
            ai_comment = f"AI生成エラー: {e}"

    # データをまとめて返す
    return {
        "summary": ai_comment,
        "data": chart_data
    }

if __name__ == "__main__":
    result = generate_market_report()
    print(result['summary'])
    print(result['data'].keys())
