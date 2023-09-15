# -*- coding: utf-8 -*-
import env
import discord
import asyncio
import mysql.connector as sql
import os
import shutil
import pytube
import math
from discord.ext import commands
from discord import FFmpegPCMAudio

guild = discord.Object(id=env.GUILD_ID)
queue = []
nowPlaying = ""

class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.sycned = False
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.sycned:
            await tree.sync(guild=guild)
            self.synced = True
        print("Bot is online")

bot = abot()
tree = discord.app_commands.CommandTree(bot)

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

@tree.command(name="ping", description="Bot odpowie ci pong", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="author", description="Bot poda ci najważniejsze informacje o autorze", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Autorem bocika jest <@386237687008591895>.\n\nGithub: https://github.com/kasztandor\nFacebook: https://www.facebook.com/kasztandor\nReddit: https://www.reddit.com/user/Kasztandor\nInstagram: https://www.instagram.com/kasztandor_art\nInstagram: https://www.instagram.com/kasztandor_photos", suppress_embeds=True)

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

@bot.event
async def on_message(message):
    msgLowercase = message.content.lower()
    msgLowercaseNoPolish = msgLowercase.replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l").replace("ń","n").replace("ó","o").replace("ś","s").replace("ż","z").replace("ź","z")
    guild = message.guild
    msg = message.content
    sender = message.author
    if (msg == "!sync" and message.author.id == 386237687008591895):
        await tree.sync()
        await message.channel.send("Zsynchronizowano drzewo!")
    if (msg == "!queue" and message.author.id == 386237687008591895):
        await message.channel.send(queue)
    if message.channel.id == env.MEMES_CHANNEL:
        if len(message.attachments) or message.content.startswith("j:") or "https://" in msg or "http://" in msg:
            await message.add_reaction("\U0001F44D")
            await message.add_reaction("\U0001F44E")
    if bot.user in message.mentions and "przedstaw sie" in msgLowercaseNoPolish:
        await message.channel.send("Siema! Jestem sobie botem napisanym przez Kasztandora i tak sobie tutaj działam i robię co do mnie należy. Pozdrawiam wszystkich i życzę udanego dnia!")


async def afterPlayAsync():
    global queue
    global nowPlaying
    if (len(queue)):
        print("Następny song")
        if ((nowPlaying not in queue) and os.path.isfile("yt/"+nowPlaying+".mp3")):
            os.remove("yt/"+nowPlaying)
        playSong(queue.pop(0))
    else:
        print("Uciekam")
        nowPlaying = ""
        queue = []
        if (len(bot.voice_clients)):
            await bot.voice_clients[0].disconnect()

def afterPlay(err):
    asyncio.run_coroutine_threadsafe(afterPlayAsync(), bot.loop)

def playSong(vid_id):
    global nowPlaying
    print("playSong()")
    nowPlaying = vid_id
    source = FFmpegPCMAudio("yt/"+vid_id+".mp3")
    bot.voice_clients[0].play(source, after=afterPlay)

@tree.command(name="play", description="Dodaj utwór do kolejki odtwarzania", guild=guild)
async def self(interaction: discord.Interaction, fraza:str):
    global queue
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        srch = pytube.Search(fraza)
        if len(srch.results) == 0:
            await interaction.response.send_message("Nie znaleziono takiego utworu!")
        else:
            await interaction.response.send_message("Trwa pobieranie wybranego utworu...")
            try:
                if (not os.path.isfile("yt/"+srch.results[0].video_id+".mp3")):
                    yt = pytube.YouTube("https://www.youtube.com/watch?v="+srch.results[0].video_id)
                    video = yt.streams.filter(only_audio=True).first()
                    video.download(filename=srch.results[0].video_id+".mp3",output_path="yt")
                if (len(bot.voice_clients) == 0):
                    await channel.channel.connect()
                    playSong(srch.results[0].video_id)
                elif (bot.voice_clients[0].is_playing()):
                    queue.append(srch.results[0].video_id)
                else:
                    playSong(srch.results[0].video_id)
                await interaction.edit_original_response(content="Wyszukano: **"+fraza+"**.\nDodano do kolejki: **"+srch.results[0].title+"**!")
            except:
                await interaction.edit_original_response(content="Głupi youtube nie pozwala mi pobrać tego utworu.")

@tree.command(name="pause", description="Pauzuje i wznawia odtwarzanie muzyki", guild=guild)
async def self(interaction: discord.Interaction):
    if (len(bot.voice_clients) and bot.voice_clients[0].is_playing()):
        if (bot.voice_clients[0].is_paused()):
            bot.voice_clients[0].resume()
            await interaction.response.send_message("Wznowiono odtwarzanie muzyki.")
        else:
            bot.voice_clients[0].pause()
            await interaction.response.send_message("Spauzowano odtwarzanie muzyki.")
    else:
        await interaction.response.send_message("Bot nic nie gra przystojniaczku. Nie jestem w stanie zarzucić pauzy JOŁ.")

@tree.command(name="queue", description="Sprawdź kolejkę odtwarzania", guild=guild)
async def self(interaction: discord.Interaction, page:int=1):
    global queue
    if (len(queue) == 0):
        await interaction.response.send_message("Aktualnie nic nie czeka na odtworzenie.")
    else:
        prefix = ""
        if (page < 1):
            prefix = "Podana strona nie istnieje. Wyświetlam pierwszą dostępną stronę.\n\n"
            page = 1
        elif (page > math.ceil(len(queue)/10)):
            prefix = "Podana strona nie istnieje. Wyświetlam ostatnią dostępną stronę.\n\n"
            page = math.ceil(len(queue)/10)
        pg = page-1
        middle = ""
        for i in range(10):
            if (len(queue) == pg*10+i):
                break
            srch = pytube.Search(queue[pg*10+i])
            middle += str(pg*10+i+1)+". **"+srch.results[0].title+"**\n"
        sufix = "\nWyświetlono stronę: "+str(page)+"/"+str(math.ceil(len(queue)/10))
        await interaction.response.send_message(prefix+middle+sufix)

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
    shutil.rmtree("yt")
    os.mkdir("yt")
    if (len(bot.voice_clients)):
        bot.voice_clients[0].disconnect()
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

bot.run(env.TOKEN)