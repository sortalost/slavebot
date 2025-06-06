from discord.ext import commands
import aiohttp
import asyncio
import json
import os
from src.bot.utils import database


class ChatBot(commands.Cog):
    """chat with gemini (not shapes inc.)"""
    def __init__(self,bot):
        self.bot=bot
        self.msgs = {}
        self.remote = database.DB(main="aiconvos.json")
        with open("src/bot/files/prompt.txt","r") as f:
            self.base_prompt = f.read()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.conversation_history = self.remote.get_remote_data()

    async def get(self, input_text: str, specific_user: str):
        api_url = os.getenv('CHATAPI')
        headers = {"Content-Type": "application/json"}
        if specific_user not in self.bot.conversation_history:
            self.bot.conversation_history[specific_user] = []
        self.bot.conversation_history[specific_user].append({"role": "user", "text": input_text})
        context = "\n".join([f"{message['role']}: {message['text']}" for message in self.bot.conversation_history[specific_user]]) + "\nassistant:"
        prompt = f"Conversation so far:\n{context} \n{self.base_prompt}"
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
            try:
                msg = await self.bot.wait_for("message",check=check, timeout=60)
            except asyncio.exceptions.TimeoutError:
                await m1.reply(f"{ctx.author.mention}, chat timed out. (60s)")
                return
            if msg.content.lower().strip()=="quit":
                await msg.reply("[-] user quits")
                run=False
                break
            await ctx.typing()
            reply = await self.get(str(msg.content), ctx.author.id)
            bmsg = await msg.reply(reply)
            self.msgs.get(ctx.guild.id).append(msg)
            self.msgs.get(ctx.guild.id).append(bmsg)
            self.remote.push_remote_data(self.bot.conversation_history)
        convolength = len(self.msgs.get(ctx.guild.id))
        self.msgs = {}
        await ctx.send(f"Conversation Length, {convolength}. See it [here](<{self.bot.website}/ai/{ctx.author.id}>).")
        # try:
        #     for m in self.msgs.get(ctx.guild.id):
        #         await m.delete()
        # except:
        #     pass

    
    @commands.command(aliases=['hc'])
    async def historyclear(self,ctx):
        """deletes your data with gemini; your chat history and saved character traits will be deleted"""
        await ctx.send("are you sure? send `yes` or `no`")
        def check(m):return m.author==ctx.author and ctx.channel==m.channel
        try:
            msg = await self.bot.wait_for("message",check=check, timeout=60)
            if str(msg.content).lower()=="yes":
                await ctx.typing()
                self.bot.conversation_history[ctx.author.id] = []
                self.remote.push_remote_data(self.bot.conversation_history)
                await ctx.send("cleared chat history")
                return
            else:
                await ctx.send("cancelled",delete_after=5)
                return
        except asyncio.exceptions.TimeoutError:
            await m1.reply(f"{ctx.author.mention}, timed out. (60s)")
            return

async def setup(bot):
    await bot.add_cog(ChatBot(bot))
