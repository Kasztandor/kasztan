# -*- coding: utf-8 -*-
import env
import discord
import asyncio
import mysql.connector as sql
import os
import pytube
from discord.ext import commands
from discord import FFmpegPCMAudio

guild = discord.Object(id=env.GUILD_ID)
voice = None

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

@tree.command(name="sync", description="Synchronizacja drzewa", guild=guild)
async def self(interaction: discord.Interaction):
    await tree.sync()
    await interaction.response.send_message("Zsynchronizowano drzewo!")

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
    if message.channel.id == env.MEMES_CHANEL:
        await message.add_reaction("\U0001F44D")
        await message.add_reaction("\U0001F44E")
    if bot.user in message.mentions and "przedstaw sie" in msgLowercaseNoPolish:
        await message.channel.send("Siema! Jestem sobie botem napisanym przez Kasztandora i tak sobie tutaj działam i robię co do mnie należy. Pozdrawiam wszystkich i życzę udanego dnia!")

@tree.command(name="play", description="Dodaj utwór do kolejki odtwarzania", guild=guild)
async def self(interaction: discord.Interaction, argument:str):
    """ resp = ""
    for i, j in enumerate(pytube.Search(argument).results):
        resp += f"{i+1}. {j.title}\n"
        if i == 4:
            break
    await interaction.response.send_message(resp) """
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        srch = pytube.Search(argument)
        if len(srch.results) == 0:
            await interaction.response.send_message("Nie znaleziono takiego utworu!")
        else:
            await interaction.response.send_message("Wyszukano: **"+argument+"**.\nOdtwarzam **"+srch.results[0].title+"**!")
            yt = pytube.YouTube("https://www.youtube.com/watch?v="+srch.results[0].video_id)
            video = yt.streams.filter(only_audio=True).first()
            video.download(filename="song.mp3",output_path="yt")
            voice = await channel.channel.connect()
            source = FFmpegPCMAudio("yt/song.mp3")
            voice.play(source)

@tree.command(name="leave", description="Spraw, aby bot uciekł z kanału głosowego", guild=guild)
async def self(interaction: discord.Interaction):
    channel = interaction.user.voice
    if channel is None:
        await interaction.response.send_message("Musisz być na kanale głosowym!")
    else:
        await bot.voice_clients[0].disconnect()
        await interaction.response.send_message("Opuściłem kanał głosowy!")

bot.run(env.TOKEN)