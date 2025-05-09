import requests
import discord
from discord.ext import commands

def get(i,u):
	return requests.get(f"{os.getenv('api')}?uid={str(u)}&msg={i}").json()["cnt"]

class ChatBot(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.msgs = {}
	
	@commands.command(name="chat", aliases=["c"])
	async def chatbot(self,ctx):
		self.msgs.update({ctx.guild.id:[]})
		m1 = await ctx.reply("hey (send `QUIT` to end conversation)")
		self.msgs.get(ctx.guild.id).append(m1)
		run=True
		def check(m):return m.author==ctx.author and ctx.channel==m.channel
		while run:
			msg = await self.bot.wait_for("message",check=check)
			if msg.content.lower().strip()=="quit":
				await msg.reply(get("quit",ctx.author.id))
				run=False
				break
			bmsg = await msg.reply(get(str(msg.content),ctx.author.id))
			self.msgs.get(ctx.guild.id).append(msg)
			self.msgs.get(ctx.guild.id).append(bmsg)
		convolength = len(self.msgs.get(ctx.guild.id))
		self.msgs = {}
		await ctx.send(f"Conversation Length, {convolength}")
		# try:
		# 	for m in self.msgs.get(ctx.guild.id):
		# 		await m.delete()
		# except:
		# 	pass


async def setup(bot):
	await bot.add_cog(ChatBot(bot))