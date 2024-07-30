import openai
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config['DEFAULT']['OPENAI_API_KEY']


def translate_to_english(text):
  chat_params = [
    {"role": "system", "content":"You are an excellent translator. Please translate the Japanese portion of the text into English."},
    {"role": "user", "content": text}]
  
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_params)
  res = response['choices'][0]['message']['content']
  return res
  
  
def translate_to_japanese(text):
  chat_params = [
    {"role": "system", "content":"You are an excellent translator. Please translate the English portion of the text into Japanese."},
    {"role": "user", "content": text}]
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_params)
  res = response['choices'][0]['message']['content']
  return res

def createWorld(input, lang):
  if(lang == "en"):
    with open("prompt/createWorld.txt", "r") as f:
      content = f.read()
  else:
    with open("prompt/createWorld_JP.txt", "r") as f:
      content = f.read()

  chat_params = [
    {"role": "system", "content":content},
    {"role": "user", "content": input}]
  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=chat_params)
  res = response['choices'][0]['message']['content']
  return res

def createScenario(input , lang):
  if(lang == "en"):
    with open("prompt/createScenario.txt", "r") as f:
      content = f.read()
  else:
    with open("prompt/createScenario_JP.txt", "r") as f:
      content = f.read()

  chat_params = [
    {"role": "system", "content":content},
    {"role": "user", "content": input}]
  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=chat_params)
  res = response['choices'][0]['message']['content']
  return res
