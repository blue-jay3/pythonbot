import discord # from pip install py-cord
import os # default module
from dotenv import load_dotenv # from pip install python-dotenv

import schedule
import time
from discord.ext import tasks
import validators

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=discord.Intents.all()) # create a new instance of discord.Bot()

@bot.event # overrides on_ready()
async def on_ready():
    print(f"{bot.user} is ready and online!")

# notification functions
@tasks.loop(minutes=60)
async def notify_user():
    await bot.wait_until_ready()
    user = bot.get_user(396050286420164610)
    # requests.get("http://127.0.0.1").elapsed.total_seconds()
    await user.send(f"Latency is {round(bot.latency * 1000)}ms.")

notify_user.start()

# slash commands
@bot.slash_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Latency is {round(bot.latency * 1000)}ms.")

@bot.slash_command(name="add-website", description="Add a website to get notifications for it")
async def gtn(ctx: discord.ApplicationContext, url):
    if validators.url(url):
        await ctx.respond("You will now get notified for the site " + url)
    else:
        await ctx.respond("Invalid URL")

bot.run(os.getenv('TOKEN')) # run the bot with the token
