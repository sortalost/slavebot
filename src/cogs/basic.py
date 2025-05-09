import io
import discord
from discord.ext import commands
from utils.tools import cleanup_code


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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