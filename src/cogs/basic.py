import io
import sys
import time
import inspect
import discord
import platform
from discord.ext import commands
from utils.tools import cleanup_code


class Basic(commands.Cog):
    """Basic commands"""
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
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

    @commands.command()
    async def uptime(self, ctx, r="R"):
        """how long the bot has been running for"""
        seconds = int(time.time() - self.start_time)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        em = discord.Embed(description=f"🕒 **Uptime**: `{hours}h {minutes}m {seconds}s`\n📅 **Since**: <t:{int(self.start_time)}:{r}>")
        await ctx.send(embed=em)

    @commands.command(aliases=['src'])
    async def source(self,ctx,command):
        """get a command's source"""
        cmd = self.bot.get_command(command).callback
        src = inspect.getsource(cmd)
        _file = inspect.getfiles(cmd)
        desc = f"""\
        From {_file}:
        ```py
        {src}
        ```
        
        -# source on [GitHub](<https://github.dev/sortalost/slavebot/>)
        """
        return await ctx.send(embed=discord.Embed(description=desc))

    @commands.command()
    async def info(self,ctx):
        """tech stack of the bot"""
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    distro = line.strip().split("=")[1].strip('"')
        em = discord.Embed(color=discord.Colour.blurple())
        em.title("Tech Stack")
        em.description=f"""\
        discord.py `{discord.__version__}`
        python `{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`
        {platform.system()} {distro}
        <:railway:1370670662359715912> runs on Railway
        `.source` for source code.
        """


async def setup(bot):
    await bot.add_cog(Basic(bot))
