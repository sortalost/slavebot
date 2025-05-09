import os
import asyncio
import discord
from discord.ext import commands
import datetime
import time
from utils.help import Help


TOKEN = os.getenv("TOKEN")
LOG = 877473404117209191
prefix = "."
_vars = {
    'x':[],
    'y':[],
    'r':[]
}
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(prefix),
    case_insensitive=True,
    help_command=Help(no=["dodis"]),
    owner_id=817359568945545226,
    intents=intents,
    strip_after_prefix=True
)

bot.verbosity = 30

@bot.event
async def on_ready():
    print("up and running")
    timestamp = int(time.time())
    em = discord.Embed(title=f"running", color=discord.Color.green())
    em.add_field(name="time", value=f"<t:{timestamp}> - <t:{timestamp}:R>")
    em.description = f"""\
    success:{', '.join(_vars['x'])}
    fails: {', '.join(_vars['y'])}
    reasons:{' | '.join(_vars['r'])}
    """
    await bot.get_channel(LOG).send(embed=em)


@bot.event
async def on_message(message):
    if message.author==bot.user:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(title="nuh uh", color=discord.Color.red(), timestamp=datetime.datetime.now())
    em.description = f"```{error}```"
    await ctx.send(embed=em)



async def main():
    async with bot:
        for filename in os.listdir(f"./src/cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    _vars['x'].append(filename[:-3])
                except Exception as e:
                    _vars['y'].append(filename[:-3])
                    _vars['r'].append(str(e))
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
