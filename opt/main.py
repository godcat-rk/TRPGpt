import openai
import operate
import re
import os
import datetime
import readline
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config['DEFAULT']['OPENAI_API_KEY']

# G3 世界観の入力受け取り、英訳
lang = input("言語設定 en OR ja:")
world_set = operate.translate_to_english(input("プレイするTRPGの世界観を簡単に教えてください:"))

# プレイ人数の受け取り
# players_num = input("プレイする人数を入力してください:")
players_num = "1"

# G4 受け取った世界観から設定、キャラクターの生成
if(lang == "en"):
  createWorld_input = f"""
  ## Worldview
  {world_set}

  ## Number of players
  {players_num}

  ## Required time
  1 hour 
  """
else:
  createWorld_input = f"""
  ## 世界観
  {world_set}

  ## プレイ人数
  {players_num}

  ## 必要時間
  20分から30分
  """

print("世界を創造しています...")
World = operate.createWorld(createWorld_input, lang)

# ステータス部分の抽出
status_index = World.find('## Status')
Status = World[status_index:]

# G4 シナリオの生成
print("物語を構築しています...")
Scenario = operate.createScenario(World, lang)

# プロンプトの作成
if(lang == "en"):
  with open("prompt/systemPrompt.txt", "r") as f:
    content = f.read()
  system_prompt=content.replace("{{createWorld_input}}", createWorld_input)
  system_prompt=system_prompt.replace("{{World}}", World)
  system_prompt=system_prompt.replace("{{Scenario}}", Scenario)
else:
  with open("prompt/systemPrompt_JP.txt", "r") as f:
    content = f.read()
  system_prompt=content.replace("{{createWorld_input}}", createWorld_input)
  system_prompt=system_prompt.replace("{{World}}", World)
  system_prompt=system_prompt.replace("{{Scenario}}", Scenario)

# プロンプトをファイル出力
now = datetime.datetime.now()
date_string = now.strftime('%Y%m%d%H%M%S')

# with open(f"scenario/{date_string}_scenario_en.txt", 'w', encoding='utf-8') as file:
#     file.write(system_prompt)

with open(f"scenario/{date_string}_scenario_jp.txt", 'w', encoding='utf-8') as file:
    file.write(operate.translate_to_japanese(system_prompt))

# 初期入力パラメータ
if(lang == "en"):
  user_prompt = f"""
## History
{Status}

## Next Action
Start the game
"""
else:
  user_prompt = f"""
## History
{Status}

## Next Action
ゲームを開始する
"""

chat_params = [
      {"role": "system", "content":system_prompt},
      {"role": "user", "content": user_prompt}]


# G3 シナリオ進行
while True:  
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_params)
  gpt3_response = response['choices'][0]['message']['content']
  # G3からの応答をパラメータに追加(対話履歴の保持による文脈維持)
  chat_params.append({"role": "assistant", "content": gpt3_response})

  print("--------res---------")
  print(gpt3_response)
  print("--------------------")
  if(lang == "en"):
    user_input = input("Next Action:")
  else:
    user_input = operate.translate_to_english(input("次の行動を入力してください:"))

  # 受け取ったuser_inputを送信用ユーザープロンプトのNext Actionに当てこむ
  if(lang == "en"):
    user_prompt = re.sub(r'(?<=## Next Action\n).*', user_input, gpt3_response, flags=re.DOTALL)
  else:
    user_prompt = re.sub(r'(?<=## Next Action\n).*', operate.translate_to_japanese(user_input), gpt3_response, flags=re.DOTALL)    
  user_prompt = re.sub(".*?\## History", "## History", user_prompt, flags=re.DOTALL)  
  chat_params.append({"role": "user", "content": user_prompt})
  if len(chat_params) >= 5:
    del chat_params[1:3]
