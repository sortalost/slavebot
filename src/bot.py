import os
import asyncio
import discord
from discord.ext import commands
import datetime
import time

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
    owner_id=817359568945545226,
    intents=intents,
    strip_after_prefix=True
)

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
    em = discord.Embed(title="you broke me idiot", color=discord.Color.red(), timestamp=datetime.datetime.now())
    em.description = f"```{error}```"
    await ctx.send(embed=em)


@bot.command()
async def ping(ctx):
    """get latency"""
    await ctx.send(bot.latency)


@bot.command()
async def echo(ctx, *, content: str):
    """i say what you say"""
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(content)


def cleanup_code(self, content):
    """Automatically removes code blocks from the code."""
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')
    

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically remove code blocks from the code."""
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.strip("`").split("\n")[1:])
        return content.strip("` \n")

    @commands.command(pass_context=True, aliases=['dds'])
    @commands.is_owner()
    async def dodis(self, ctx, *, body: str):
        """Evaluates a code."""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }
        env.update(globals())
        body = self.cleanup_code(body)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name="SayNo"))
            except:
                pass
            await ctx.send(embed=discord.Embed(
                title=":o: Traceback Encountered :o:",
                description=f"**Process Exited with Status Code `1`**\n```py\n{value}{traceback.format_exc()}\n```",
                colour=0xFF0000
            ).set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url))
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name="SayYes"))
            except:
                pass
            if ret is None:
                if value:
                    await ctx.send(embed=discord.Embed(
                        description=f"**Process Exited with Status Code `0`**\n```py\n{value}\n```"
                    ).set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url))
            else:
                self._last_result = ret
                await ctx.send(embed=discord.Embed(
                    description=f"**Process Exited with Status Code `0`**\n```py\n{value}{ret}\n```",
                    colour=0x00FF00
                ).set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url))


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
