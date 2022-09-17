import discord
from discord.ext import commands
from PIL import Image
import os
from random import randrange

TOKEN = "MTAxNjQxNDc0NjQ2MDgyMzU2Mg.GiJyQJ.FKMwOLjSNJGfDKTwdj-zWgotmjRJnmO_FoAhok"
roles = [698047161245630545,698047575013457931,703327203068346388,723329755465777193,732345037798506497,736570299537031280,736570295954964542,736570323234848930,736570319921348619,736571825043013672,736571823600435280]
guild = discord.Object(id=670330167339778048)

def ball8():
    x=["Mój wywiad donosi: NIE","Wygląda dobrze","Kto wie?","Zapomnij o tym","Tak - w swoim czasie","Prawie jak tak","Nie teraz","YES, YES, YES","To musi poczekać","Mam pewne wątpliwości","Możesz na to liczyć","Zbyt wcześnie aby powiedzieć","Daj spokój","Absolutnie","Chyba żatrujesz?","Na pewno nie","Zrób to","Prawdopodobnie","Dla mnie rewelacja","Na pewno tak"]
    return "Magiczna kula mówi: "+x[randrange(0,len(x))]

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

@tree.command(name="ping", description="Bot odpowie ci pong", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="ball8", description="Bot wylosuje hasło z magicznej kuli nr 8", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(ball8())

@tree.command(name="generate", description="Bot wygeneruje wybrany przez ciebie napis", guild=guild)
async def self(interaction: discord.Interaction, argument:str):
    process = argument.lower().replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l").replace("ń","n").replace("ó","o").replace("ś","s").replace("ż","z").replace("ź","z")
    images = []
    width = 0
    for i in process:
        if i == " ":
            images.append(Image.open("letters/space.png"))
            width += images[-1].width
        elif os.path.exists("letters/"+i+".png"):
            images.append(Image.open("letters/"+i+".png"))
            width += images[-1].width
    newImage = Image.new('RGB', (width, images[0].height))
    width = 0
    for i in images:
        newImage.paste(i, (width, 0))
        width += i.width
    if os.path.exists("napis.png"):
        os.remove("napis.png")
    newImage.save("napis.png")
    await interaction.response.send_message(file=discord.File('napis.png'))

@bot.event
async def on_message(message):
    guild = message.guild
    msg = message.content
    msgLowercase = msg.lower()
    msgLowercaseNoPolish = msgLowercase.replace("ą","a").replace("ć","c").replace("ę","e").replace("ł","l").replace("ń","n").replace("ó","o").replace("ś","s").replace("ż","z").replace("ź","z")
    sender = message.author

    if len(message.mentions) > 0 and message.mentions[0] == bot.user and (msgLowercaseNoPolish.content.find("przedstaw sie") != -1):
        await message.channel.send("Siema! Jestem sobie botem napisanym przez Kasztandora i tak sobie tutaj działam i robię co do mnie należy. Pozdrawiam wszystkich i życzę udanego dnia!")

bot.run(TOKEN)