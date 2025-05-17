import aiohttp
from discord.ext import commands


class Random(commands.Cog):
    """Random commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['cs'])
    async def csgo(self, ctx, num:int = 1):
        """get `n` videos from CSGOANI.ME"""
        allurls = []
        if int(num)>5:
            return await ctx.send("`num` cannot be > 5")
        for i in range(num):
            async with aiohttp.ClientSession() as session:
                async with session.post("https://csgoanime.vercel.app/new") as response:
                    if response.status != 200:
                        return await ctx.send("something went wrong...", delete_after=10)
                    url = await response.json()
                    allurls.append(url)
        await ctx.send("\n".join(allurls))
  

async def setup(bot):
    await bot.add_cog(Random(bot))
