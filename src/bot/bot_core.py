import os
import asyncio
import discord
from discord.ext import commands
import datetime
import time
import traceback
from src.bot.utils.help import Help


TOKEN = os.getenv("TOKEN")
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
    help_command=Help(),
    owner_id=os.getenv("OWNER_ID"),
    intents=intents,
    strip_after_prefix=True
)

bot.conversation_history = {}
bot.website = os.getenv("WEBSITE")
bot.LOG = os.getenv("LOG_CHANNEL")

@bot.event
async def on_ready():
    print("up and running")
    timestamp = int(time.time())
    with open("src/bot/files/update.txt","r") as f:
        update = f.read()
    em = discord.Embed(title=f"Running", color=discord.Color.green())
    em.add_field(name="TIME", value=f"<t:{timestamp}> - <t:{timestamp}:R>")
    em.description = f"""\
    ```diff\n{update}\n```
    **Cogs:**
    **- Loaded:** {', '.join(_vars['x'])}
    **- Errors:** {', '.join(_vars['y'])}
    **- Reasons:** {' | '.join(_vars['r'])}
    """
    await bot.get_channel(bot.LOG).send(embed=em)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.bot:  # oopsies
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(title="nuh uh", color=discord.Color.red(), timestamp=datetime.datetime.now())
    em.description = f"```{error}```"
    await ctx.send(embed=em)


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(bot.LOG)
    if channel:
        error = traceback.format_exc()
        await channel.send(embed=discord.Embed(title=f"error in `{event}`",color=discord.Color.red(),description=f"```\n{error}\n```"))


async def run_async():
    async with bot:
        for filename in os.listdir(f"src/bot/cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"src.bot.cogs.{filename[:-3]}")
                    _vars['x'].append(filename[:-3])
                except Exception as e:
                    _vars['y'].append(filename[:-3])
                    _vars['r'].append(str(e))
        await bot.start(TOKEN)

# service: comment out for railway
# if __name__ == "__main__":
#     asyncio.run(run_async())
