import discord # Discordのライブラリをインポート
import os
import re
import openai # OpenAIのライブラリをインポート
import deepl # DeepLのライブラリをインポート
import datetime, time, random
from discord.ext import commands

# Discord Botのアクセストークン
TOKEN = ''

# OpenAI APIキー
openai.api_key = ''

# 使用するエンジン
model_engine = "gpt-3.5-turbo"

# chennel ID(chatbot-test)の定義
CHANNEL_ID = 
ROLE_CHANNEL_ID = 
TRANSLATE_CHANNEL_ID = 
VC_CHANNEL_ID = 

# 付与する役職のIDの定義
ROLE_ID = 1183652364226404392

# 時間計測用の変数定義
start = -1
end = -1

# 初期設定
intents = discord.Intents.all()
client = discord.Client(intents=discord.Intents.all())

async def greet(): # 起動時にこのBotで利用できるコマンドを表示
    channel = client.get_channel(CHANNEL_ID) #チャンネル情報を取得
    await channel.send('このChatBotで利用できる機能は以下の通りです。\n\n＜コマンド＞\n- /neko: ねこが泣きます\n- /dice: サイコロのように1~6の乱数を生成します\n- /date: 現在の日本時間を表示できます\n- /banana: 強調文字でメッセージが送られます\n- /status: Botのステータスを編集します\n- /gpt: チャットボットが起動します\n\n＜その他の機能＞\n- リアクション付与機能\n- メッセージ編集時通知機能\n- メッセージ削除時通知機能\n- 翻訳機能\n- 新規メンバー参加時通知機能')

def is_japanese(str): # メッセージが日本語か否かを判定
    return True if re.search(r'[ぁ-んァ-ン]', str) else False

# 起動時に動作する処理
@client.event
async def on_ready(): 
    print('ログインしました') # Botが起動したらターミナルに起動通知を表示させる
    await greet()
    await client.change_presence(activity=discord.Game(name="SA演習"))

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.bot: # メッセージ送信者がBotだった場合は無視する
        return
    if message.content.startswith('こんにちは'): # メッセージが"こんにちは"で始まっていたら"こんにちは!"と応答
        await message.channel.send('こんにちは!')
    if message.content.startswith('おはよう'):
        await message.channel.send('うるせえ')
    if message.content.startswith('さようなら'):
        await message.channel.send('さようなら!')
    if message.content.startswith('元気?'):
        await message.channel.send('私はロボットなので体調は関係ありません。')
    if message.content.startswith('こんばんは'):
        await message.channel.send('こんばんは!')
    if message.content.startswith('マクド'):
        await message.channel.send('「マック」な')
    
    # ねこのお遊び
    if message.content == ('/neko'):
        await message.channel.send('にゃーん')
        
    # サイコロを振る
    if message.content == ('/dice'):
        await message.channel.send(random.randint(1,6))

    # 今日の日付を出す
    if message.content == ('/date'):
        dt = datetime.datetime.today()
        await message.channel.send(dt.date())

    # バナナメッセージ
    if message.content == '/banana':
        await message.channel.send('# バナナのナス、バナナス')

    # Botのステータスを変更
    if message.content.startswith("/status"):
       if client.user!=message.author:
           stmsg=message.content[4:]
           await client.change_presence(activity = discord.Activity(name=str(stmsg), type=discord.ActivityType.playing))

    #時間の計測
    if message.content == '/start': #時間の計測を開始
        start = time.time()
        await message.channel.send('計測開始しました')
    if message.content == '/finish': #時間の計測を終了
        if start == -1:
            await message.channel.send('計測が開始されていません')
        else:
            end = time.time()
            diff_time = end - start
            await message.channel.send(f'経過時間は{diff_time}です')
            start = -1
            end = -1
        
    #ChatGPTで会話
    global model_engine
    if message.author.bot: # Botが相手なら反応しない
        return
    if message.author == client.user: # Bot自身が送信したメッセージには反応しない
        return
    if message.content.startswith('/gpt'): 
        msg = await message.reply("生成中...", mention_author=False)
        try:
            prompt = message.content[4::] # ユーザーからの質問を受け取る
            if not prompt: # プロンプト無しなら「生成中」のメッセージを削除する
                await msg.delete()
                await message.channel.send("質問内容がありません")
                return
            completion = openai.ChatCompletion.create(
            model = model_engine,
            messages = [
                {
                    "role": "system",
                    "content": "日本語で返答してください。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            )

            response = completion["choices"][0]["message"]["content"]
            await msg.delete()
            await message.reply(response, mention_author=False)
        except:
            import traceback
            traceback.print_exc()
            await message.reply("エラーが発生しました", mention_author=False)

    # DeepLを用いた英語翻訳機能
    if message.channel.id != TRANSLATE_CHANNEL_ID:
        return
    msg = message.content
    if is_japanese(msg) == True:
        lang = "EN-US"
    else:
        lang = "JA"

    translator = deepl.Translator("")
    result = translator.translate_text(msg, target_lang=lang)
    result_txt = result.text

    embed = discord.Embed(description=result, color = discord.Colour.from_rgb(130, 219, 216))
    await message.channel.send(embed=embed)

# 新規メンバー参加時に動作する処理
@client.event
async def on_member_join(member):
    channel = client.get_channel(CHANNEL_ID) #チャンネル情報を取得
    await channel.send(f"{member}が参加しました！ よろしく！")

# メッセージが編集された時に実行される処理
@client.event
async def on_message_edit(before, after):
    await before.channel.send(f"「{before.content}」から「{after.content}」にメッセージが編集されました")

# メッセージが削除された時に実行される処理
@client.event
async def on_message_delete(message):
    if message.author.bot: # Botが相手なら反応しない
        return
    await message.channel.send(f"{message.author.name}さんのメッセージが削除されました:\n```\n削除されたメッセージ: {message.content}\n```")

# リアクションに応じてロールを付与
@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(CHANNEL_ID) 
    if channel.id != CHANNEL_ID: # もし該当のチャンネル(chatbot-test)でない場合は実行しない
        return
    guild = client.get_guild(payload.guild_id) # Discordのサーバー(ギルド)情報を取得
    member = guild.get_member(payload.user_id) # User IDを取得
    role = guild.get_role(ROLE_ID) # 'role'にロールIDを代入
    await member.add_roles(role) # ロールを付与！
    await channel.send(f"ハイラッシャイ！！！ {member}に「Superman!!!」のロールを付与しました！")

# リアクションが付いたら通知
@client.event
async def reaction_add(reaction, user):
    channel = client.get_channel(CHANNEL_ID)
    message = reaction.message #リアクションがついたメッセージを記録
    msg = f"{message.author.mention} {reaction}\nFrom:{user.display_name} \
        \nMessage:{message.content}\n{message.jump_url}" # 通知する内容
    await channel.send(msg)

client.run(TOKEN)
