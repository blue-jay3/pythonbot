import discord # from pip install py-cord
import os # default module
from dotenv import load_dotenv # from pip install python-dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=discord.Intents.all()) # create a new instance of discord.Bot()

@bot.event # overrides on_ready()
async def on_ready():
    print(f"{bot.user} is ready and online!")

# slash commands
@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

@bot.slash_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Latency is {round(bot.latency * 1000)}ms.")

@bot.slash_command(name="game", description="Play a number guessing game")
async def gtn(ctx: discord.ApplicationContext):
    embed = discord.Embed( # embed
        title="Number Guessing Game",
        description="Guess a number between 1 and 10.",
        color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
    )
    embed.set_footer(text="Type \'Cancel\' to end the game.")
    await ctx.respond(embed=embed)
    while True:
        guess = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if guess.content.lower() == 'cancel':
            await ctx.send('You cancelled the game.')
            break
        elif int(guess.content) == 5:
            await ctx.send('You guessed it!')
            break
        else:
            await ctx.send('Nope, try again or type \'Cancel\'.')

bot.run(os.getenv('TOKEN')) # run the bot with the token