import io
import time
import discord
from discord.ext import commands
from utils.tools import cleanup_code


class Basic(commands.Cog):
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
        seconds = int(time.time() - self.start_time)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        em = discord.Embed(description=f"🕒 **Uptime**: `{hours}h {minutes}m {seconds}s`\n📅 **Since**: <t:{int(self.start_time)}:{r}>")
        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Basic(bot))
