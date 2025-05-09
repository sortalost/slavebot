from discord.ext import commands
import aiohttp
import json
import os

async def get(input_text: str, specific_user: str):
    api_url = os.getenv('chatapiurl')
    headers = {"Content-Type": "application/json",}
    prompt = f"{input_text}\n - from a user id \"{specific_user}\"; reply to them!"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                content = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No response content.")
                return content
            else:
                return f"error: {response.status}, {await response.text()}"


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
				await msg.reply("[-] user quits")
				run=False
				break
			reply = await get(str(msg.content), ctx.author.id)
			bmsg = await msg.reply(reply)
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