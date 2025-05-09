from discord.ext import commands
import aiohttp
import json
import os
from utils import database


class ChatBot(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.msgs = {}
		self.remote = database.DB(main="aiconvos.json")

	@commands.Cog.listener()
	async def on_ready(self):
		self.bot.conversation_history = self.remote.get_remote_data()

	async def get(self, input_text: str, specific_user: str):
		api_url = os.getenv('chatapiurl')
		headers = {"Content-Type": "application/json"}
		if specific_user not in self.bot.conversation_history:
			self.bot.conversation_history[specific_user] = []
		self.bot.conversation_history[specific_user].append({"role": "user", "text": input_text})
		context = "\n".join([f"{message['role']}: {message['text']}" for message in self.bot.conversation_history[specific_user]]) + "\nassistant:"
		prompt = f"Conversation so far:\n{context}\nPlease reply naturally and keep verbosity to {self.bot.verbosity}%; reply as if youre talking to them. ONLY THE REPLY!"
		payload = {"contents": [{"parts": [{"text": prompt}]}]}
		async with aiohttp.ClientSession() as session:
			async with session.post(api_url, json=payload, headers=headers) as response:
				if response.status == 200:
					data = await response.json()
					content = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No response.")
					self.bot.conversation_history[specific_user].append({"role": "assistant", "text": content})
					return content
				else:
					return f"Error: {response.status}, {await response.text()}"
	
	@commands.command(name="chat", aliases=["c"])
	async def chatbot(self,ctx):
		"""chat with ai"""
		self.msgs.update({ctx.guild.id:[]})
		m1 = await ctx.reply("hey (send `QUIT` to end conversation)")
		self.msgs.get(ctx.guild.id).append(m1)
		run=True
		def check(m):return m.author==ctx.author and ctx.channel==m.channel
		while run:
			msg = await self.bot.wait_for("message",check=check)
			if msg.content.lower().strip()=="quit":
				await msg.reply("[-] user quits")
				run=False
				break
			reply = await self.get(str(msg.content), ctx.author.id)
			bmsg = await msg.reply(reply)
			self.msgs.get(ctx.guild.id).append(msg)
			self.msgs.get(ctx.guild.id).append(bmsg)
			self.remote.push_remote_data(self.conversation_history)
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