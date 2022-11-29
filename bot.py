# -*- coding: utf-8 -*-
import env
import discord
from discord.ext import commands
import mysql.connector as sql
import os

guild = discord.Object(id=GUILD_ID)

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
    guild = message.guild
    msg = message.content
    sender = message.author

    if bot.user in message.mentions:
        await message.channel.send("Siema! Jestem sobie botem napisanym przez Kasztandora i tak sobie tutaj działam i robię co do mnie należy. Pozdrawiam wszystkich i życzę udanego dnia!")

bot.run(TOKEN)
