import datetime
import json
import discord # from pip install py-cord
import os # default module
from dotenv import load_dotenv # from pip install python-dotenv

import requests
from discord.ext import tasks, commands
import validators

import pythonping
import sqlite3

import pandas as pd

from captcha.image import ImageCaptcha
from datetime import datetime

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=discord.Intents.all()) # create a new instance of discord.Bot()

# sqlite database information
connection = sqlite3.connect("linksToNotify.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS usersLinks (userId, userName, url)")
connection.commit()
cursor.execute("CREATE TABLE IF NOT EXISTS metricsAccessed (userId, userName, url, lastAccessed)")
connection.commit()

@bot.event # overrides on_ready()
async def on_ready():
    print(f"{bot.user} is ready and online!")

# notification functions
@tasks.loop(minutes=15)
async def call_python_ping():
    await bot.wait_until_ready()

    result = cursor.execute(f"SELECT * FROM usersLinks")

    for (id, _, url) in result.fetchall():
        user = bot.get_user(id)
        resp = requests.get(url)
        respMs = resp.elapsed.total_seconds()*1000
        if resp.status_code == 404:
            await user.send("! : Can't reach <" + str(url) + ">")
        elif respMs > 400:
            await user.send(f"! : Latency for <{url}> ({respMs}ms) is over 400ms")
        else:
            print(f"Ping {url} : {respMs}ms")

call_python_ping.start()

# slash commands
@bot.slash_command(name="ping", description="Get the bot's latency")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Latency is {round(bot.latency * 1000)}ms.")

@bot.slash_command(name="help", description="Get started with Status Scout here!")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Status Scout's Commands",
        description="**Disclaimer :** Users should only use the bot for accessing metrics from websites they own or manage.",
        color=discord.Colour.darker_grey(),
    )
    embed.add_field(name="/ping", value="Get Status Scout's latency", inline=True)
    embed.add_field(name="/add-website [url]", value="Add a website to get notifications for it", inline=True)
    embed.add_field(name="/metrics [url]", value="Get the website metrics for the specified url", inline=True)
 
    embed.set_footer(text="Join our support server discord.gg/MSR83fkWxf !") # footers can have icons too

    await ctx.respond(embed=embed)

@commands.cooldown(2, 5, commands.BucketType.user)
@bot.slash_command(name="add-website", description="Add a website to get notifications for it")
async def gtn(ctx: discord.ApplicationContext, url):
    if validators.url(url):
        result = cursor.execute(f"SELECT * FROM usersLinks WHERE url='{url}' AND userId={ctx.author.id}")
        if result.fetchone() is None:
            cursor.execute("INSERT INTO usersLinks (userId, userName, url) VALUES (?, ?, ?)", (ctx.author.id, str(ctx.author.name), str(url)))
            connection.commit()
            await ctx.respond("You will now get notified for the site <" + url + ">")
        else:
            await ctx.respond("You already have notifications set up for the site <" + url + ">")
    else:
        await ctx.respond("Invalid URL")

@commands.cooldown(1, 120, commands.BucketType.user)
@bot.slash_command(name="metrics", description="Get the website metrics for the specified url")
async def get_metrics(ctx: discord.ApplicationContext, url):
    now = datetime.now()
    
    if not validators.url(url):
        return await ctx.respond("Invalid URL")

    # API request url
    await ctx.respond("Contacting API...")
    results = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={os.getenv('PS_API_KEY')}")

    await ctx.edit(content="Fetching metrics...")
    results_json = results.json()

    await ctx.edit(content="Loading results...")
    df1 = pd.DataFrame(results_json)

    result = cursor.execute(f"SELECT * FROM metricsAccessed WHERE url='{url}' AND userId={ctx.author.id}")
    if result.fetchone() is None:
        cursor.execute("INSERT INTO metricsAccessed (userId, userName, url, lastAccessed) VALUES (?, ?, ?, ?)", (ctx.author.id, str(ctx.author.name), str(url), now))
    else:
        cursor.execute(f"UPDATE metricsAccessed SET lastAccessed='{now}' WHERE userId={ctx.author.id} AND url='{url}'")
    connection.commit()

    try:
        await ctx.edit(content="Metrics fetched : " + str(df1['lighthouseResult']['audits']['speed-index']))
    except discord.ApplicationCommandInvokeError as e:
        await ctx.edit(content=e)

# catch error if command is on cooldown, and notify user
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

bot.run(os.getenv('TOKEN')) # run the bot with the token
