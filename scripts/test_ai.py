import os
import google.generativeai as genai

# 1. GitHubに登録した鍵を取り出す
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("エラー: APIキーが見つかりません！Secretsの設定を確認してください。")
    exit(1)

# 2. AIの設定
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# 3. AIに挨拶をお願いする
try:
    response = model.generate_content("面白い挨拶を一つしてください。")
    print("--- AIからの返事 ---")
    print(response.text)
    print("-------------------")
    print("成功！AIとの接続確認ができました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
