import io
import os
import sys
import time
import inspect
import discord
import platform
from discord.ext import commands
from src.bot.utils.tools import cleanup_code

GITHUBSRC = os.getenv("GITHUBSRC")

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
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        em = discord.Embed(description=f"🕒 **Uptime**: `{days}days {hours}h {minutes}m {seconds}s`\n📅 **Since**: <t:{int(self.start_time)}:{r}>")
        await ctx.send(embed=em)

    @commands.command(aliases=['src'])
    async def source(self,ctx,*,command):
        """get a command's source"""
        cmd = self.bot.get_command(command).callback
        src, line = inspect.getsourcelines(cmd)
        _file = inspect.getfile(cmd)[8:]
        desc = F"""\
[**`{_file}`**](<{GITHUBSRC}/blob/main/src/{_file}#L{line}>):
```py
{"".join(src)}
```

source on [GitHub](<{GITHUBSRC}/blob/main/src/{_file}#L{line}>)
        """
        em = discord.Embed(description=desc)
        em.timestamp=discord.utils.utcnow()
        return await ctx.send(embed=em)

    @commands.command()
    async def info(self,ctx):
        """tech stack of the bot"""
        dsc = discord.utils.get(self.bot.emojis, id=844923996738420757) # discord emoji
        pyt = discord.utils.get(self.bot.emojis, id=844917083757084713) # python emoji
        rwy = discord.utils.get(self.bot.emojis, id=1370670662359715912) # railway emoji (service)
        # rnd = discord.utils.get(self.bot.emojis, id=1378999200238403644) # render emoji (service)
        ubn = discord.utils.get(self.bot.emojis, id=1370682643469045910) # ubuntu emoji (os)
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    distro = line.strip().split("=")[1].strip('"')
        em = discord.Embed(color=discord.Colour.blurple())
        em.title = "Tech Stack"
        em.add_field(name="discord.py", value=f"{dsc} `v{discord.__version__}`", inline=False)
        em.add_field(name="python", value=f"{pyt} `{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`", inline=False)
        em.add_field(name=platform.system(), value=f"{ubn} `{distro}`", inline=False)
        em.add_field(name="Runs on", value=f"{rwy} [railway](<https://railway.com>)", inline=False) # change this
        # em.add_field(name="Runs on", value=f"{rnd} [render](<https://render.com>)", inline=False) # accordingly
        await ctx.send(embed=em)
    

    @commands.command()
    async def update(self,ctx):
        with open("src/bot/files/update.txt") as f:
            update = f.read()
        await ctx.send(f"```diff\n{update}\n```")

async def setup(bot):
    await bot.add_cog(Basic(bot))
