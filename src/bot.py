import os
import discord
from discord.ext import commands
import datetime
import time

TOKEN = os.getenv("TOKEN")
LOG = 877473404117209191
prefix = "."

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(prefix),
    case_insensitive=True,
    owner_id=817359568945545226,
    intents=intents,
    strip_after_prefix=True
)

@bot.event
async def on_ready():
    x = []
    y = []
    r = []
    for filename in os.listdir(f"./src/cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                x.append(filename[:-3])
            except Exception as e:
                y.append(filename[:-3])
                r.append(str(e))
    print("up and running")
    timestamp = time.time()
    em = discord.Embed(title=f"running", color=discord.Color.green())
    em.add_field(name="time", value=f"<t:{timestamp}> - <t:{timestamp}:R>")
    em.description = f"success:{', '.join(x)}\nfails: {', '.join(y)}\nreasons:{'\n-'.join(r)}"
    await bot.get_channel(LOG).send(embed=em)


@bot.event
async def on_message(message):
    if message.author==bot.user:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(title="you broke me idiot", color=discord.Color.red(), timestamp=datetime.datetime())
    em.description = f"```{error}```"
    await ctx.send(embed=em)


@bot.command()
async def ping(ctx):
    """get latency"""
    await ctx.send(bot.latency)


@bot.command()
async def echo(ctx, *, content: str):
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(content)


bot.run(TOKEN)
