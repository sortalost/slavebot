import os
import discord
from discord.ext import commands
import Paginator
from datetime import datetime 

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

lastmsg = {}


def gen_snipe(ctx, guild):
    eb = []
    try:
        snipes = lastmsg[guild]
    except KeyError:
        lastmsg.update({guild: []})
        return []
    if snipes == []:
        return []
    i = 0
    for m in snipes:
        i += 1
        embed = discord.Embed(title=f"snipe {i}/{len(snipes)}")
        embed.add_field(name="from", value=m.author.mention, inline=False)
        embed.add_field(name="content", value=f"{m.content}\n", inline=False)
        embed.add_field(name="in", value=m.channel.mention, inline=False)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
        eb.append(embed)
    return eb[::-1]


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return
    try:
        lastmsg[message.guild.id].append(message)
    except KeyError:
        lastmsg.update({message.guild.id: [message]})


@bot.event
async def on_ready():
    print("up and running")
    await bot.get_channel(LOG).send("running")


@bot.event
async def on_message(message):
    if 'nigga' in message.content.lower():
        await message.reply("no u nigga")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(title="you broke me idiot", color=discord.Color.red(), timestamp=datetime.utcnow())
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


@bot.command(name="snipe", aliases=['snp'])
async def snipe(ctx: commands.Context):
    """get deleted messages"""
    snipes = gen_snipe(ctx, ctx.guild.id) 
    if snipes == []:
        return await ctx.send("nothing to snipe")
    await Paginator.Simple().start(ctx, pages=snipes)


print("running???")
bot.run(TOKEN)
