import time
import aiohttp
import discord
from discord.ext import commands


class Server(commands.Cog):
    """Stuff related to the [Server](https://discord.gg/yVw38mjpFu)"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.is_owner()
    @commands.command(aliases=['su'])
    async def serverupdate(self,ctx):
        em = discord.Embed(title=f"Last update: <t:{int(time.time())}:R>",color=ctx.author.color)
        members = ctx.guild.member_count
        bots = len([member for member in ctx.guild.members if member.bot])
        roles = []
        for r in ctx.guild.roles:
            if not r.is_bot_managed() and (not r.is_default()):
                roles.append(r.mention)
        em.description = f"""\
        `{members}` members.
        `{bots}` bots.
        {len(roles)} roles:
        {' '.join(roles)}
        """
        await ctx.message.delete()
        mid = ctx.message.reference.message_id
        msg = await ctx.fetch_message(mid)
        await msg.edit(embed=em)
        await msg.reply("updated",delete_after=10)


async def setup(bot):
    await bot.add_cog(Server(bot))
