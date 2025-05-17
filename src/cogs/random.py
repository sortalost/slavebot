import aiohttp
from discord.ext import commands


class Random(commands.Cog):
    """Random commands"""
    def __init__(self, bot):
        self.bot = bot
        self.max_vid=5
    
    @commands.command(aliases=['cs'])
    async def csgo(self, ctx, num:int = 1):
        """get `n` videos from CSGOANI.ME"""
        try:
            if int(num)==0:
                return await ctx.send("atleast one")
        except:
            return await ctx.send(f"must be a number. Eg: `.cs 4` sends four videos. Maximum limit is {self.max_vid}. Change using `.maxcsgo number`")
        allurls = []
        if int(num)>self.max_vid:
            return await ctx.send("`num` cannot be > 5")
        await ctx.typing()
        for i in range(num):
            i+=1
            async with aiohttp.ClientSession() as session:
                async with session.get("https://csgoanime.vercel.app/new") as response:
                    if response.status != 200:
                        return await ctx.send(response.status, delete_after=10)
                    resp = await response.json()
                    url = resp['video']
                    name = url.split("/")[-1]
                    allurls.append(f"`{i}`.[`{name}`]({url})")
        await ctx.send("\n".join(allurls))


    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def maxcsgo(self,ctx,num:int=0):
        if num==0:
            return await ctx.send(f"Current CSGO videos threshold: `{self.max_vid}`")
        self.max_vid=num
        await ctx.send(f"Current CSGO videos threshold: `{self.max_vid}`")

  

async def setup(bot):
    await bot.add_cog(Random(bot))
