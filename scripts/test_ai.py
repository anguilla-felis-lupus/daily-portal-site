import os
import google.generativeai as genai

# 1. GitHubに登録した鍵を取り出す
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("エラー: APIキーが見つかりません！Secretsの設定を確認してください。")
    exit(1)

# 2. AIの設定
genai.configure(api_key=api_key)

# print("利用可能なモデルの一覧を取得します...\n")

# # 利用可能なモデルをリストアップ
# for model in genai.list_models():
#     # 'generateContent'（文章生成）が可能なモデルのみを表示する
#     if 'generateContent' in model.supported_generation_methods:
#         print(model.name)

model = genai.GenerativeModel('models/gemini-2.0-flash')

# 3. AIに挨拶をお願いする
try:
    response = model.generate_content("面白い挨拶を一つしてください。")
    print("--- AIからの返事 ---")
    print(response.text)
    print("-------------------")
    print("成功！AIとの接続確認ができました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
