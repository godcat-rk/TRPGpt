import openai
import operate
import re
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

# G3 世界観の入力受け取り、英訳
world_set = input("プレイするTRPGの世界観を簡単に教えてください:")

# プレイ人数の受け取り
# players_num = input("プレイする人数を入力してください:")
players_num = "1"

# G4 受け取った世界観から設定、キャラクターの生成
createWorld_input = f"""
[世界観] {world_set}
[プレイ人数] {players_num}
[想定プレイ時間] 20 minutes to 30 minutes
"""

print("世界を創造しています...")
World = operate.createWorld_JP(createWorld_input)

# ステータス部分の抽出
status_index = World.find('[Status]')
Status = World[status_index:]

# G4 シナリオの生成
print("物語を構築しています...")
Scenario = operate.createScenario_JP(World)

# プロンプトの作成
with open("systemPrompt_JP.txt", "r") as f:
  content = f.read()
system_prompt=content.replace("{{createWorld_input}}", createWorld_input)
system_prompt=system_prompt.replace("{{World}}", World)
system_prompt=system_prompt.replace("{{Scenario}}", Scenario)

# プロンプトをファイル出力
with open('export_prompt_JP.txt', 'w', encoding='utf-8') as file:
    # system_promptの内容をファイルに書き込む
    file.write(system_prompt)

user_prompt = f"""
[進捗]

[ステータス]
{Status}

[次の行動]
ゲームを開始する
"""

chat_params = [
      {"role": "system", "content":system_prompt},
      {"role": "user", "content": user_prompt}]

# G3 メインアクション
while True:  
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_params)
  gpt3_response = response['choices'][0]['message']['content']
  # G3からの応答をパラメータに追加(対話履歴の保持による文脈維持)
  chat_params.append({"role": "assistant", "content": gpt3_response})

  print("--------------------")
  print(gpt3_response)
  print("--------------------")
  user_input = input("次の行動を入力してください:")

  # 受け取ったuser_inputを送信用ユーザープロンプトのNext Actionに当てこむ
  user_prompt = re.sub(r'(?<=\[次の行動\]\n).*', user_input, gpt3_response, flags=re.DOTALL)
  user_prompt = re.sub(".*?\[進捗]", "[進捗]", user_prompt, flags=re.DOTALL)  
  # print("--------------------")
  # print(operate.translate_to_japanese(user_prompt))
  # print("--------------------")
  chat_params.append({"role": "user", "content": user_prompt})
  if len(chat_params) >= 5:
    del chat_params[1:3]
