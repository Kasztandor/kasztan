# -*- coding: utf-8 -*-
import discord
import asyncio
import mysql.connector as sql
import os
import shutil
#import pytubefix as pytube
import math
import sqlite3
import yt_dlp
from discord.ext import commands
from discord import FFmpegPCMAudio
from mcstatus import JavaServer

def checkType(value):
    try:
        int(value)
        return "int"
    except:
        pass

    try:
        float(value)
        return "float"
    except:
        pass

    return "str"

##################
# Database stuff #
##################

import sqlite3

def checkType(value):
    # None
    if value == None:
        return "None"
    # Int
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    # Float
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    # String
    return "str"

def returnType(value):
    # None
    if value == None:
        return "None"
    # Int
    try:
        return int(value)
    except ValueError:
        pass
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    # String
    return value

envContent = {
    "TOKEN": "str",
    "COUNTING_CHANNEL": "int",
    "MEMES_CHANNEL": "int",
    "MINECRAFT_STATUS_CHANNEL":"int",
    "GUILD_ID": "int",
    "OWNER_ID": "int",
    "MINECRAFT_SERVER_IP": "str",
    "MINECRAFT_SERVER_PORT": "int"
}

con = sqlite3.connect("db.db")
cur = con.cursor()

# Sprawdzenie, czy tabela `variables` istnieje
res = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='variables';")
if res.fetchone()[0] == 0:  # Jeśli tabela nie istnieje, tworzona jest nowa
    cur.execute("CREATE TABLE variables (name text, value text)")
    con.commit()

# Sprawdzenie, czy tabela ma wymagane kolumny
res = cur.execute("SELECT COUNT(*) FROM pragma_table_info('variables') WHERE name IN ('name', 'value');")
if res.fetchone()[0] != 2:  # Jeśli tabela ma błędną strukturę, usuń i stwórz poprawną
    cur.execute("DROP TABLE IF EXISTS variables;")
    cur.execute("CREATE TABLE variables (name text, value text)")
    con.commit()

# Pobranie istniejących wpisów
existing_entries = {row[0] for row in cur.execute("SELECT name FROM variables")}

# Dodawanie brakujących wartości
for key, value in envContent.items():
    if key not in existing_entries:
        x = None
        while checkType(x) != value:
            if x != None:
                print("Use correct type for", key)
            x = input(f"Add missing entry: {key} ({value}): ")
        cur.execute("INSERT INTO variables (name, value) VALUES (?, ?)", (key, x))

con.commit()

env = {name: returnType(value) for name, value in cur.execute("SELECT name, value FROM variables")}

#####################################################
# Creating bot class and setting up the environment #
#####################################################

guild = discord.Object(id=env["GUILD_ID"])
queue = []
nowPlaying = ""

class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.sycned = False
    async def on_ready(self):
        await self.wait_until_ready()
        #if not self.sycned:
            #await tree.sync(guild=guild)
            #self.synced = True
        mcServer = asyncio.create_task(minecraftServer())
        print("Bot is online")

bot = abot()
tree = discord.app_commands.CommandTree(bot)

async def minecraftServer():
    while True:
        channel = bot.get_channel(env["MINECRAFT_STATUS_CHANNEL"])
        try:
            server = JavaServer(env["MINECRAFT_SERVER_IP"], env["MINECRAFT_SERVER_PORT"])
            messageContent = "**Status serwera:** *online*\n**Ilość graczy:** *"+str(server.status().players.online)+"*"
            await channel.edit(name="『💎』info〘"+str(server.status().players.online)+"〙")
            if len(server.query().players.names):
                messageContent += "\n**Gracze online:** *"+", ".join(server.query().players.names)+"*"
        except:
            await channel.edit(name="『💎』info")
            messageContent = "**Status serwera:** *offline*"
        messages = [message async for message in channel.history(limit=1)]
        if len(messages) == 0 or messages[0].author.id != bot.user.id:
            await channel.send(messageContent)
        else:
            await messages[0].edit(content=messageContent)
        await asyncio.sleep(30)

'''
async def initMoney(id):
    mydb = sql.connect(host="localhost", user="root", password="", database='kasztan')
    cursor = mydb.cursor()
    cursor.execute((f"SELECT * FROM `users` WHERE `user_id` = {id}"))
    for x in cursor:
        mydb.close()
        return x[1]
    cursor.close()
    cursor = mydb.cursor()
    cursor.execute((f"INSERT INTO `users` (`user_id`, `money`) VALUES ({id}, 1000)"))
    mydb.commit()
    cursor.close()
    mydb.close()
    return 1000
'''

@tree.command(name="ping", description="Bot odpowie ci pong", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="author", description="Bot poda ci najważniejsze informacje o autorze", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Autorem bocika jest <@386237687008591895>.\n\nGithub: <https://github.com/kasztandor>\nFacebook: <https://www.facebook.com/kasztandor>\nReddit: <https://www.reddit.com/user/Kasztandor>\nInstagram: <https://www.instagram.com/kasztandor_art>\nInstagram: <https://www.instagram.com/kasztandor_photos>", suppress_embeds=True)

'''
@tree.command(name="money", description="Sprawdź stan konta", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(await initMoney(interaction.user.id))

@tree.command(name="top", description="Zobacz kto jest najbogatszy", guild=guild)
async def self(interaction: discord.Interaction):
    mydb = sql.connect(host="localhost", user="root", password="", database='kasztan')
    cursor = mydb.cursor()
    cursor.execute((f"SELECT * FROM `users` ORDER BY `money` DESC"))
    string = ""
    embed = discord.Embed(color=0x00ff00)
    for x in cursor:
        string += f"<@{x[0]}>: {x[1]:,}\n"
    mydb.close()
    embed.add_field(name="Najbogatsi ludzie:", value=string, inline=False)
    await interaction.response.send_message(embed=embed)
'''

async def afterPlayAsync():
    global queue
    #global nowPlaying
    if (len(queue)):
        #if ((nowPlaying not in queue) and os.path.isfile("yt/"+nowPlaying+".mp3")):
        #    os.remove("yt/"+nowPlaying)
        playSong(queue.pop(0))
    else:
        nowPlaying = ""
        queue = []
        if (len(bot.voice_clients)):
            await bot.voice_clients[0].disconnect()

def afterPlay(err):
    asyncio.run_coroutine_threadsafe(afterPlayAsync(), bot.loop)

def playSong(path):
    #global nowPlaying
    #nowPlaying = path
    source = FFmpegPCMAudio(path)
    bot.voice_clients[0].play(source, after=afterPlay)


def ytDownload(phrase="", dirr="yt", downType="mp3"):
    search_url = f"ytsearch:{phrase}"

    if downType == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{dirr}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '44100',
                '-ac', '2',
            ],
        }
    elif downType == 'mp4':
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{dirr}/%(id)s.%(ext)s',
            'merge_output_format': 'mp4',  # Ensures final output is MP4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Fallback conversion if needed
            }],
        }
    else:
        print("Nieobsługiwany format")
        return

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
        video_info = info['entries'][0]
        video_id = video_info['id']
        ydl.download([search_url])
    
    return {"success": True, "reason": "already exists", "link": "https://youtu.be/", "title": "", "vid": video_id}

# Przykład użycia
#download_video(phrase="Rick Astley Never Gonna Give You Up", dirr="yt", downType="mp3")

#def ytDownload(phrase="", dirr="yt", downType="mp3"):
#    try:
#        yt = pytube.YouTube(phrase)
#    except:
#        srch = pytube.Search(phrase)
#        if len(srch.results) == 0:
#            return {success: False, "reason": "search error"}
#        yt = srch.results[0]
#    video = yt.streams.filter(only_audio=(downType=="mp3")).first()
#    if not os.path.isfile(dirr+"/"+yt.video_id+"."+downType):
#        try:
#            video.download(filename=yt.video_id+"."+downType,output_path=dirr)
#            return {"success": True, "link": "https://youtu.be/"+yt.video_id, "title": yt.title, "vid": yt.video_id, "path": dirr+"/"+yt.video_id+"."+downType}
#        except:
#            return {"success": False, "reason": "download error"}
#    else:
#        return {"success": True, "reason": "already exists", "link": "https://youtu.be/"+yt.video_id, "title": yt.title, "vid": yt.video_id, "path": dirr+"/"+yt.video_id+"."+downType}

@tree.command(name="play", description="Dodaj utwór z biblioteki do kolejki odtwarzania", guild=guild)
async def self(interaction: discord.Interaction, fraza:str):
    global queue
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        await interaction.response.send_message("Trwa pobieranie wybranego utworu...")
        ytb = ytDownload(fraza)
        if ytb["success"] == False:
            if ytb["reason"] == "search error":
                await interaction.edit_original_response("Nie znaleziono takiego utworu!")
            else:
                await interaction.edit_original_response("Nie udało się pobrać filmu!")
        else:
            if (len(bot.voice_clients) == 0):
                await channel.channel.connect()
                playSong(ytb["path"])
            elif (bot.voice_clients[0].is_playing()):
                queue.append(ytb["path"])
            else:
                playSong(ytb["path"])
            await interaction.edit_original_response(content="Wyszukano: **"+fraza+"**.\nDodano do kolejki: **"+ytb["title"]+"**!")

@tree.command(name="playfromlib", description="Dodaj utwór do kolejki odtwarzania", guild=guild)
async def self(interaction: discord.Interaction, fraza:str):
    global queue
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        #if file exist
        path = os.path.dirname(os.path.abspath(__file__))+"/library/"+fraza+".mp3"
        print(path)
        if os.path.isfile(path):
            if (len(bot.voice_clients) == 0):
                await channel.channel.connect()
                playSong(path)
            elif (bot.voice_clients[0].is_playing()):
                queue.append(path)
            else:
                playSong(path)
            await interaction.response.send_message(content="Dodano do kolejki: **"+fraza+"** z biblioteki!")
        else:
            await interaction.response.send_message("Nie znaleziono takiego utworu w bibliotece!")


#@tree.command(name="pause", description="Pauzuje i wznawia odtwarzanie muzyki", guild=guild)
#async def self(interaction: discord.Interaction):
#    if (len(bot.voice_clients) and bot.voice_clients[0].is_playing()):
#        if (bot.voice_clients[0].is_paused()):
#            bot.voice_clients[0].resume()
#            await interaction.response.send_message("Wznowiono odtwarzanie muzyki.")
#        else:
#            bot.voice_clients[0].pause()
#            await interaction.response.send_message("Spauzowano odtwarzanie muzyki.")
#    else:
#        await interaction.response.send_message("Bot nic nie gra przystojniaczku. Nie jestem w stanie zarzucić pauzy JOŁ.")

#@tree.command(name="queue", description="Sprawdź kolejkę odtwarzania", guild=guild)
#async def self(interaction: discord.Interaction, page:int=1):
#    global queue
#    if (len(queue) == 0):
#        await interaction.response.send_message("Aktualnie nic nie czeka na odtworzenie.")
#    else:
#        prefix = ""
#        if (page < 1):
#            prefix = "Podana strona nie istnieje. Wyświetlam pierwszą dostępną stronę.\n\n"
#            page = 1
#        elif (page > math.ceil(len(queue)/10)):
#            prefix = "Podana strona nie istnieje. Wyświetlam ostatnią dostępną stronę.\n\n"
#            page = math.ceil(len(queue)/10)
#        pg = page-1
#        middle = ""
#        for i in range(10):
#            if (len(queue) == pg*10+i):
#                break
#            srch = pytube.Search(queue[pg*10+i])
#            middle += str(pg*10+i+1)+". **"+srch.results[0].title+"**\n"
#        sufix = "\nWyświetlono stronę: "+str(page)+"/"+str(math.ceil(len(queue)/10))
#        await interaction.response.send_message(prefix+middle+sufix)

@tree.command(name="skip", description="Pomija aktualnie odtwarzany utwór", guild=guild)
async def self(interaction: discord.Interaction, count:int=1):
    global queue
    counter = 1
    while (count > 1):
        count -= 1
        counter += 1
        if (not len(queue)):
            break
        queue.pop(0)
    bot.voice_clients[0].stop()
    await afterPlayAsync()
    await interaction.response.send_message("Pominięto "+str(counter)+" utworów.")

@tree.command(name="stop", description="Zatrzymuje odtwarzacz", guild=guild)
async def self(interaction: discord.Interaction):
    global queue
    queue = []
    #shutil.rmtree("yt")
    #os.mkdir("yt")
    if (len(bot.voice_clients)):
        await bot.voice_clients[0].disconnect()
    await interaction.response.send_message("Zatrzymano odtwarzacz.")
'''
@tree.command(name="leave", description="Spraw, aby bot uciekł z kanału głosowego", guild=guild)
async def self(interaction: discord.Interaction):
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        await bot.voice_clients[0].disconnect()
        await interaction.response.send_message("Opuściłem kanał głosowy!")
'''

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild is None:
        msg = message.content.lower()
        afterTrim = message.content[5:]
        if msg.startswith("mp4: ") or msg.startswith("mp3: "):
            #try:
                yt = ytDownload(afterTrim, "yt/"+str(message.author.id), msg[:3])
                if yt["success"]:
                    await message.channel.send("", file=discord.File("yt/"+str(message.author.id)+"/"+yt["vid"]+"."+msg[:3]), reference=message)
                    os.remove("yt/"+str(message.author.id)+"/"+yt["vid"]+"."+msg[:3])
                else:
                    await message.channel.send("Nie udało się pobrać filmu!", reference=message)
            #except:
            #    await message.channel.send("No i w dupę strzelił! Znów coś się zepsuło :(   ", reference=message)
        else:
            await message.channel.send("Funkcje bota poprzez DM zawierają:```► mp3: [link/fraza] ◄ pobiera i wysyła plik mp3 z youtube\n► mp4: [link/fraza] ◄ pobiera i wysyła plik mp4 z youtube```\nNa przykład:```mp3: https://www.youtube.com/watch?v=dQw4w9WgXcQ```\nWszystkie inne komendy działają tylko na serwerze!")
        return
    requiredEquationCharacters = "+-*/"
    allowedEquationCharacters = "0123456789 (),."

    processEquation = True
    containsRequiredCharacters = False

    for index, char in enumerate(message.content.replace(" ", "").replace(",", ".")):
        if char in requiredEquationCharacters:
            if index != 0:
                containsRequiredCharacters = True
        elif char not in allowedEquationCharacters:
            processEquation = False
            break
    
    if processEquation and containsRequiredCharacters:
        await message.channel.send("```\n"+message.content.replace(" ","")+" = "+str(eval(message.content))+"```", reference=message)
        return

    msgLowercase = message.content.lower()
    msgLowercaseNoPolish = msgLowercase.replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l").replace("ń","n").replace("ó","o").replace("ś","s").replace("ż","z").replace("ź","z")
    guild = message.guild
    msg = message.content
    sender = message.author
    if msg == "!sync" and message.author.id == env["OWNER_ID"]:
        await tree.sync(guild=guild)
        await message.channel.send("Zsynchronizowano drzewo!")
    if msg == "!reset":
        if message.author.guild_permissions.administrator:
            await message.channel.send("Bot został zresetowany!")
            os.system("systemctl --user restart SELF-kasztan.service")
        else:
            await message.channel.send("Nie jesteś wystarczająco zasłużony aby używać tej komendy!")
    if message.channel.id == env["MEMES_CHANNEL"]:
        if len(message.attachments) or message.content.startswith("j:") or "https://" in msg or "http://" in msg:
            await message.add_reaction("\U0001F44D")
            await message.add_reaction("\U0001F44E")
    if bot.user in message.mentions and "przedstaw sie" in msgLowercaseNoPolish:
        await message.channel.send("Siema! Jestem sobie botem napisanym przez Kasztandora i tak sobie tutaj działam i robię co do mnie należy. Pozdrawiam wszystkich i życzę udanego dnia!")

bot.run(env["TOKEN"])
