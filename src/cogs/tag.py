
import asyncio
import discord
from discord.ext import commands
from utils import database
from discord.utils import get as g
import difflib as dfb


main_bank = "alltags.json"


def load_all_tags():
    with open(main_bank,'r') as f:
        tags = json.load(f)
    return tags

def init_guild(guild):
    tags=load_all_tags()
    try:
        return tags[str(guild)]
    except KeyError:
        tags.update(dict({str(guild):{}}))
        with open(main_bank,'w') as f:
            json.dump(tags,f,indent=4)
        return True

def new_tag(guild,tag,value,author):
    tags = load_all_tags()
    tag=dict({tag.lower():{'value':value,'author':str(author)}})
    tags[str(guild)].update(tag)
    with open(main_bank,'w') as f:
        json.dump(tags,f,indent=4)
    return True

def rem_tag(guild,tag):
    tags = load_all_tags()
    tags[str(guild)].pop(tag.lower())
    with open(main_bank,'w') as f:
        json.dump(tags,f,indent=4)
    return True

def get_tag(guild,tag):
    users = load_all_tags()
    bal = users[str(guild)][tag.lower()]
    return bal

def get_guild_tags(guild):
    tags=load_all_tags()
    return dict(tags[str(guild)])

def is_tag(guild,tag):
    try:
        all_tags = load_all_tags()
        all_tags[str(guild)][tag.lower()]
        return True
    except KeyError:
        return False


class Tagging(commands.Cog):
	"""Tag stuff"""
	def __init__(self, bot:commands.Bot):
		self.bot=bot
		self.fp=main_bank
		self.remote=database.DB(main=self.fp)


	def disambiguate(self,tag,guild):
		taglist = list(load_all_tags().get(str(guild)))
		mt = dfb.get_close_matches(tag,taglist)
		if mt==[]:
			return ""
		if len(mt)>3:
			mt = mt[:3]
		return f"Did you mean: {', '.join(mt)}"
	
	
	@commands.Cog.listener()
	async def on_ready(self):
		self.remote.sync(self.fp, prefer="cloud")



	@commands.command(aliases=['t'], help="tag the stuff you want")
	async def tag(self,ctx,*,name=None):
		if name is None:
			return await ctx.invoke(self.bot.get_command("helptag"))
		if name.lower().startswith("add"):
			return await ctx.invoke(self.bot.get_command("addtag"),name=name[4:])
		elif name.lower().startswith("del"):
			return await ctx.invoke(self.bot.get_command("deltag"),name=name[4:])
		elif name.lower().startswith("edit"):
			return await ctx.invoke(self.bot.get_command("editag"),name=name[5:])
		elif name.lower().startswith("help"):
			return await ctx.invoke(self.bot.get_command("helptag"))
		elif name.lower().startswith("all"):
			return await ctx.invoke(self.bot.get_command("all_tags"))
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):
			return await ctx.send(f"tag manager initialized, try again.",delete_after=10)
		try:
			tag = get_tag(ctx.guild.id,name)
			con = tag['value']
		except KeyError:
			return await ctx.send(f"no such tag exists\n{self.disambiguate(name,ctx.guild.id)}",delete_after=20)
		u = g(ctx.guild.members,id=int(tag['author']))
		eb=discord.Embed(description=f"{con}",colour=u.colour,timestamp=ctx.message.created_at)
		eb.title=name.upper()
		eb.colour=u.colour
		await ctx.send(embed=eb)
				
	@commands.command(name="helptag")
	async def helptag(self,ctx):
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):
			return await ctx.send(f"tag manager initialiazed, try again.",delete_after=17)
		eb=discord.Embed(title=f"TAGS {g(self.bot.emojis,name='tag')}")
		eb.description=f"""\
**Usage:**
```fix
.tag [TAG]
.tag all
.tag add [TAG NAME]
.tag delete [TAG NAME]
.tag edit [EXISTING TAG NAME]
```
**and**,
`add`, `del`, `edit`, `all` and `help` are reserved.
"""
		eb.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar_url)
		eb.timestamp=ctx.message.created_at
		await ctx.send(embed=eb)

	@commands.command(name="addtag")
	async def _add(self,ctx,*,name:str):
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):
			return await ctx.send(f"tag manager initialized, try again.",delete_after=17)
		try:
			tag=get_tag(ctx.guild.id,name)
			a=int(tag['author'])
			await ctx.send(embed=discord.Embed(description=f"**tag \"{name}\", by <@{a}> already exists**"),delete_after=15)
			return
		except KeyError:
			pass
		def chk(m):return m.author==ctx.author and m.channel==ctx.channel
		msg0=await ctx.send(f"1) What should the tag contain {ctx.author.mention}?? Send it")
		value=await self.bot.wait_for("message",check=chk)
		msg = await ctx.send(f"Creating tag...{g(self.bot.emojis,name='funUS')}")
		new_tag(ctx.guild.id,name,value.content,ctx.author.id)
		try:
			await ctx.message.delete()
			await value.delete()
			await msg.delete()
			await msg0.delete()
		except:pass
		self.remote.push_remote_data(db.load_file(self.fp))
		await ctx.send(embed=discord.Embed(description=f"**{g(self.bot.emojis,name='tag')}tag\"{name.title()}\" by {ctx.author.mention} created{g(self.bot.emojis,name='tag')}**"))
	
	@commands.command(name="deltag")
	async def _delete(self,ctx,*,name:str):
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):
			return await ctx.send(f"tag manager initialized, try again",delete_after=17)
		chk = is_tag(ctx.guild.id,name)
		if chk is False:
			await ctx.send("no such tag exists",delete_after=7)
			return
		tag = get_tag(ctx.guild.id,name)
		if tag['author']!=str(ctx.author.id):
			return await ctx.send("you dont own this tag",delete_after=7)
		rem_tag(ctx.guild.id,name)
		tag_num = len(get_guild_tags(ctx.guild.id))
		self.remote.push_remote_data(db.load_file(self.fp))
		await ctx.send(f"tag \"{name}\" has been successfully deleted\ntotal tags for this server: {tag_num}",delete_after=10)
	
	
	@commands.command(name="editag")
	async def _edit(self,ctx,*,name:str):
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):
			return await ctx.send(f"tag manager initialized, try again.",delete_after=17)
		chk = is_tag(ctx.guild.id,name)
		if chk is False:
			await ctx.send("No Such Tag Exists!!!",delete_after=7)
			return
		tag = get_tag(ctx.guild.id,name)
		if tag['author']!=str(ctx.author.id):
			return await ctx.send("not yours...tsk...tsk",delete_after=7)
		m1=await ctx.send(f"1) Any new name for the tag?? (send the same name if you want the same name, cuz same name's name is same xD)")
		def chk(m):return m.author==ctx.author and m.channel==ctx.channel
		nm=await self.bot.wait_for("message",check=chk)
		if is_tag(ctx.guild.id,m1.content):
			if get_tag(ctx.guild.id,m1.content)['author']!=str(ctx.author.id):
				return await ctx.send("this tag already exists, sad for you. Send `.tag edit [TAG]` again",delete_after=15)
		m2=await ctx.send(f"2) Any new content for the tag?? (send the same content if u want the same content, cuz same content's content is same xD)")
		val=await self.bot.wait_for("message",check=chk)
		rem_tag(ctx.guild.id,name)
		new_tag(ctx.guild.id,nm.content,val.content,ctx.author.id)
		try:
			await ctx.message.delete()
			await m1.delete()
			await nm.delete()
			await m2.delete()
			await val.delete()
		except:
			pass
		self.remote.push_remote_data(db.load_file(self.fp))
		await ctx.send(embed=discord.Embed(title=f"tag edited.{g(self.bot.emojis,name='BlobBroke')}"))
	
	@commands.command()
	async def all_tags(self,ctx):
		c = init_guild(ctx.guild.id)
		if isinstance(c, bool):return await ctx.send(f"tag manager initialized, try again.",delete_after=17)
		tags=list(get_guild_tags(ctx.guild.id))
		try:
			await ctx.send(embed=discord.Embed(description=", ".join(tags)))
		except:
			await ctx.send(embed=discord.Embed(description=g(self.bot.emojis,name="shhAngryUS")))


async def setup(bot):
	await bot.add_cog(Tagging(bot))