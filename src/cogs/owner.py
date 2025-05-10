import io
import textwrap
import traceback
from contextlib import redirect_stdout
import discord
from discord.ext import commands
from utils.tools import cleanup_code


class Developer(commands.Cog):
    """only for the developer <:ver_devUS:869794681251332177>"""
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

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
                await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, name="shhAngryUS"))
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
    
    
    @commands.command(name="verbosity", aliases=['vb'])
    @commands.is_owner()
    async def verbosity(self,ctx,verbose=None):
        """set verbosity of `.chat` replies"""
        try:
            if verbose is None:
                return await ctx.send(f"{self.bot.verbosity}% verbosity.")
            old = self.bot.verbosity
            new = int(verbose)
        except ValueError:
            return await ctx.send("verbosity should be a number between 1 and 100, not"+str(type(verbose)))
        if new>100 or new<1:
            return await ctx.send("verbosity should be between 1 and 100")
        self.bot.verbosity=new
        return await ctx.send(f"Verbosity changed from {old}% to {self.bot.verbosity}%")


async def setup(bot):
    await bot.add_cog(Developer(bot))