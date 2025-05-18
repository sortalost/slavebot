import time
import aiohttp
import discord
from discord.ext import commands
from utils import database


class Server(commands.Cog):
    """Stuff related to the [Server](https://discord.gg/yVw38mjpFu)"""
    def __init__(self, bot):
        self.bot = bot
        self.rulesch = 1373384320751894535
        self.roles = {'human':1373325900040634531}
        self.remote = database.DB(main="wakewords.json")
    
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

    
    @commands.is_owner()
    @commands.command(aliases=['ru'])
    async def rulesupdate(self,ctx,*, rule:str):
        ch = self.bot.get_channel(self.rulesch)
        await ch.send(rule)
        await ctx.reply(f"Check {ch.mention}")


    @commands.Cog.listener()
    async def on_message(self,msg):
        guildwords = self.remote.get_remote_data()[msg.guild.id]
        if msg.content.lower() in list(guildwords):
            return await ctx.reply(guildwords[msg.content.lower()])
    

    @commands.command(aliases=['ww'])
    async def wakeword(self,ctx,word:str,*,reply:str):
        words = self.remote.get_remote_data()
        try:
            words[ctx.guild.id][word] = reply
        except KeyError:
            words.update({ctx.guild.id:{word:reply}})
        self.remote.push_remote_data(words)
        await ctx.send(f"Added `{word}`. Total `{len(list(words[ctx.guild.id]))}`.")


    @commands.command(aliases=['lw'])
    async def listwakewords(self,ctx):
        words = self.remote.get_remote_data()
        try:
            guildwords = words[ctx.guild.id]
        except KeyError:
            words.update({ctx.guild.id:{}})
            return await ctx.send("initialized")
        if list(guildwords)==[]:
            return await ctx.send("None. Setup using `.wakeword [word] [reply to it]`")
        await ctx.send(", ".join(guildwords))


async def setup(bot):
    await bot.add_cog(Server(bot))
