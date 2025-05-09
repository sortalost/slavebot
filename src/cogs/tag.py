import asyncio
import discord
from discord.ext import commands
from utils import database
import json 
from discord.utils import get as g
import difflib as dfb

main_bank = "src/files/alltags.json"

def load_all_tags():
    with open(main_bank, 'r') as f:
        return json.load(f)

def init_guild(guild):
    tags = load_all_tags()
    if str(guild) not in tags:
        tags[str(guild)] = {}
        with open(main_bank, 'w') as f:
            json.dump(tags, f, indent=4)
    return tags[str(guild)]

def new_tag(guild, tag, value, author):
    tags = load_all_tags()
    tags[str(guild)][tag.lower()] = {'value': value, 'author': str(author)}
    with open(main_bank, 'w') as f:
        json.dump(tags, f, indent=4)
    return True

def rem_tag(guild, tag):
    tags = load_all_tags()
    tags[str(guild)].pop(tag.lower(), None)
    with open(main_bank, 'w') as f:
        json.dump(tags, f, indent=4)
    return True

def get_tag(guild, tag):
    return load_all_tags()[str(guild)][tag.lower()]

def get_guild_tags(guild):
    return dict(load_all_tags()[str(guild)])

def is_tag(guild, tag):
    return tag.lower() in load_all_tags().get(str(guild), {})


class Tagging(commands.Cog):
    """Tag stuff"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fp = main_bank
        self.remote = database.DB(main=self.fp)

    def disambiguate(self, tag, guild):
        taglist = list(load_all_tags().get(str(guild), {}))
        matches = dfb.get_close_matches(tag, taglist)
        if matches:
            return f"Did you mean: {', '.join(matches[:3])}"
        return ""

    @commands.Cog.listener()
    async def on_ready(self):
        start_tags = self.remote.get_remote_data()
        with open(self.fp, 'w') as f:
            json.dump(start_tags, f, indent=4)

    @commands.group(invoke_without_command=True, aliases=['t'], help="tag the stuff you want")
    async def tag(self, ctx, *, name=None):
        if name is None:
            return await ctx.invoke(self.bot.get_command("tag help"))
        c = init_guild(ctx.guild.id)
        if isinstance(c, bool):
            return await ctx.send("Tag manager initialized, try again.", delete_after=10)
        if not is_tag(ctx.guild.id, name):
            return await ctx.send(f"No such tag exists.\n{self.disambiguate(name, ctx.guild.id)}", delete_after=20)
        tag = get_tag(ctx.guild.id, name)
        user = g(ctx.guild.members, id=int(tag['author']))
        await ctx.send(tag['value'])

    @tag.command(name="help")
    async def helptag(self, ctx):
        """help regarding `tag`"""
        init_guild(ctx.guild.id)
        eb = discord.Embed(title=f"TAGS {g(self.bot.emojis, name='tag')}")
        eb.description = """
**Usage:**
```fix
.tag [TAG]
.tag all
.tag add [TAG]
.tag delete [TAG]
.tag edit [TAG]
.tag info [TAG]
```
**and**, `add`, `del`, `edit`, `all`, `info`, `help` are reserved.
"""
        eb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
        eb.timestamp = ctx.message.created_at
        await ctx.send(embed=eb)

    @tag.command(name="add")
    async def add_tag(self, ctx, *, name: str):
        """add a new tag"""
        init_guild(ctx.guild.id)
        if is_tag(ctx.guild.id, name):
            author_id = int(get_tag(ctx.guild.id, name)['author'])
            return await ctx.send(embed=discord.Embed(description=f"**Tag \"{name}\" by <@{author_id}> already exists**"), delete_after=15)
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send(f"1) What should the tag contain {ctx.author.mention}?")
        value = await self.bot.wait_for("message", check=check)
        new_tag(ctx.guild.id, name, value.content, ctx.author.id)
        self.remote.push_remote_data(load_all_tags())
        await ctx.send(embed=discord.Embed(description=f"**{g(self.bot.emojis, name='tag')} Tag \"{name.title()}\" by {ctx.author.mention} created!**"))

    @tag.command(name="delete")
    async def delete_tag(self, ctx, *, name: str):
        """delete a tag you own"""
        init_guild(ctx.guild.id)
        if not is_tag(ctx.guild.id, name):
            return await ctx.send("No such tag exists", delete_after=7)
        tag = get_tag(ctx.guild.id, name)
        if tag['author'] != str(ctx.author.id):
            return await ctx.send("You don't own this tag", delete_after=7)
        rem_tag(ctx.guild.id, name)
        self.remote.push_remote_data(load_all_tags())
        await ctx.send(f"Tag \"{name}\" deleted. Remaining tags: {len(get_guild_tags(ctx.guild.id))}")

    @tag.command(name="edit")
    async def edit_tag(self, ctx, *, name: str):
        """edit a tag you own"""
        init_guild(ctx.guild.id)
        if not is_tag(ctx.guild.id, name):
            return await ctx.send("No such tag exists", delete_after=7)
        tag = get_tag(ctx.guild.id, name)
        if tag['author'] != str(ctx.author.id):
            return await ctx.send("You don't own this tag", delete_after=7)
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send("1) New name for the tag?")
        new_name_msg = await self.bot.wait_for("message", check=check)
        await ctx.send("2) New content for the tag?")
        new_val_msg = await self.bot.wait_for("message", check=check)
        rem_tag(ctx.guild.id, name)
        new_tag(ctx.guild.id, new_name_msg.content, new_val_msg.content, ctx.author.id)
        self.remote.push_remote_data(load_all_tags())
        await ctx.send(embed=discord.Embed(title="Tag edited successfully."))

    @tag.command(name="info")
    async def info_tag(self, ctx, *, name: str):
        """find the owner of a tag"""
        init_guild(ctx.guild.id)
        if not is_tag(ctx.guild.id, name):
            return await ctx.send("No such tag", delete_after=7)
        tag = get_tag(ctx.guild.id, name)
        owner = await self.bot.fetch_user(tag['author'])
        em = discord.Embed(color=discord.Color.random())
        em.add_field(name="Tag", value=name)
        em.add_field(name="Owner", value=owner.mention)
        em.set_author(name=owner.name, icon_url=owner.avatar)
        await ctx.send(embed=em)

    @tag.command(name="all")
    async def all_tags(self, ctx):
        """show all the tags in this server"""
        init_guild(ctx.guild.id)
        tags = list(get_guild_tags(ctx.guild.id))
        if tags:
            await ctx.send(embed=discord.Embed(description="** , **".join(tags)))
        else:
            await ctx.send(embed=discord.Embed(description=f"No tags {g(self.bot.emojis, name='shhAngryUS')}"))


async def setup(bot):
    await bot.add_cog(Tagging(bot))