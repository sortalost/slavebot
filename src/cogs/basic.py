import io
import discord
from discord.ext import commands
from utils.tools import cleanup_code


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(pass_context=True, aliases=['dds'])
    @commands.is_owner()
    async def dodis(self, ctx, *, body: str):
        """Evaluates code."""
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
        body = cleanup_code(body)
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
    
    @commands.command()
    async def ping(self, ctx):
        """get latency"""
        await ctx.send(self.bot.latency)


    @commands.command()
    async def echo(self, ctx, *, content: str):
        """i say what you say"""
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(content)


async def setup(bot):
    await bot.add_cog(Basic(bot))