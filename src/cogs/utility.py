import Paginator
import discord
from discord.ext import commands



class Utils(commands.Cog):
	"""utility cog"""
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.logchannel = bot.get_channel(877473404117209191)
		self.lastmsg={}


	def gen_snipe(self, ctx, guild):
		eb = []
		try:
			snipes = self.lastmsg[guild]
		except KeyError:
			self.lastmsg.update({guild:[]})
			return []
		if snipes==[]:
			return []
		i=0
		for m in snipes:
			i+=1
			embed = discord.Embed(title=f"Snipe {i}/{len(snipes)}")
			embed.add_field(name="user", value=m.author.mention, inline=False, color=discord.Color.random())
			embed.add_field(name="content", value=f"{m.content}\n", inline=False)
			embed.add_field(name="channel", value=m.channel.mention, inline=False)
			embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
			eb.append(embed)
		return eb[::-1]


	@commands.Cog.listener()
	async def on_message_delete(self, message:discord.Message):
		if message.author.bot==True:
			return
		try:
			self.lastmsg[message.guild.id].append(message)
		except:
			self.lastmsg.update({message.guild.id:[]})
			self.lastmsg[message.guild.id].append(message)


	# @commands.command(name="snipe",aliases=['snp'])
	# async def snipe(self, ctx: commands.Context):
	# 	snipes = self.gen_snipe(ctx, ctx.guild.id)
	# 	if snipes==[]:
	# 		return await ctx.send("nothing to snipe", delete_after=5)
	# 	await Paginator.Simple().start(ctx, pages=snipes)

	@commands.command(name="snipe",aliases=['snp'])
	async def snipe(self, ctx: commands.Context):
		snipes = self.gen_snipe(ctx, ctx.guild.id)
        await ctx.send(embed=snipes[0])



def setup(bot: commands.Bot):
	bot.add_cog(Utils(bot))