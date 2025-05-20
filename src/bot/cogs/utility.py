import aiohttp
import discord
from discord.ext import commands
from discord.utils import get
import sys
from io import BytesIO
import Paginator
import re
import zlib
from src.bot.utils import rtfmutils


class RtfmBuildError(Exception):
    pass


class Utils(commands.Cog):
    """Utility commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logchannel = bot.get_channel(877473404117209191)
        self.lastmsg = {}
        self.targets = {"python": "https://docs.python.org/3", "discord": "https://discordpy.readthedocs.io/en/latest/"}
        self.rtfmaliases = {
            ("py", "p", "python"): "python",
            ("discord","d","dpy"): "discord",
        }
        self.cache = {}


    async def build(self, target) -> None:
        url = self.targets[target]
        async with aiohttp.ClientSession() as session:
            async with session.get(url+"/objects.inv") as response:
                if response.status != 200:
                    raise RtfmBuildError
                self.cache[target] = rtfmutils.SphinxObjectFileReader(await response.read()).parse_object_inv(url)

    def gen_snipe(self, ctx, guild):
        eb = []
        try:
            snipes = self.lastmsg[guild]
        except KeyError:
            self.lastmsg.update({guild: []})
            return []
        if snipes == []:
            return []
        i = 0
        for m in snipes:
            i += 1
            embed = discord.Embed(title=f"Snipe {i}/{len(snipes)}", color=discord.Color.random())
            embed.add_field(name="user", value=m.author.mention, inline=False)
            embed.add_field(name="content", value=f"{m.content}\n", inline=False)
            embed.add_field(name="channel", value=m.channel.mention, inline=False)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
            eb.append(embed)
        return eb[::-1]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        try:
            self.lastmsg[message.guild.id].append(message)
        except:
            self.lastmsg.update({message.guild.id: []})
            self.lastmsg[message.guild.id].append(message)

    @commands.command(name="snipe")
    async def snipe(self, ctx: commands.Context):
        """Get deleted messages"""
        snipes = self.gen_snipe(ctx, ctx.guild.id)
        if snipes == []:
            return await ctx.send("Nothing to snipe", delete_after=5)
        await Paginator.Simple().start(ctx, pages=snipes)

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='purge', aliases=['pg'], help='Purge(Delete) Messages')
    async def purge(self, ctx, number):
        try:
            num = int(number)
        except:
            return await ctx.send(f"Usage is `{ctx.prefix}purge 16` to delete last 16 messages")
        num = num + 1
        await ctx.channel.purge(limit=num)

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=['nr'])
    async def newrole(self, ctx, *args: str):
        """Create a new role with the specified name and color"""
        if len(args) >= 2:
            name = " ".join(args[:-1])
            color = args[-1].replace("#","")
        else:
            return await ctx.send(f"Usage: `{ctx.prefix}newrole rolename color`")
        try:
            color_int = int(color, 16)
        except ValueError:
            return await ctx.send("Invalid color format. Please provide a valid hex color code, eg: 0000ff for blue")
        
        role = await ctx.guild.create_role(name=name, color=color_int)
        await ctx.send(embed=discord.Embed(title=f"New Role: {name}", description=f"**{role.mention}** has been created.", color=color_int))

    @commands.has_permissions(manage_roles=True)
    @commands.command(aliases=['gr'])
    async def giverole(self, ctx, role: discord.Role, *users: discord.Member):
        """Assign a role to multiple users"""
        if not users:
            return await ctx.send("Please mention at least one user.")
        
        for user in users:
            try:
                await user.add_roles(role)
                await ctx.send(f"Role {role.mention} has been assigned to {user.mention}.")
            except discord.Forbidden:
                await ctx.send(f"I don't have permission to assign roles to {user.mention}.")
            except Exception as e:
                await ctx.send(f"An error occurred while assigning the role to {user.mention}: {e}")
    
    @commands.command(aliases=['dr'])
    async def deleterole(self, ctx, *roles: discord.Role):
        """Delete a role from the server"""
        if not roles:
            return await ctx.send("Specify at least one role to delete.")
        if ctx.author.guild_permissions.manage_roles:
            for role in roles:
                try:
                    await role.delete()
                    await ctx.send(f"Role `{role.name}` has been successfully deleted.")
                except discord.Forbidden:
                    await ctx.send("I don't have permission to delete that role.")
                except discord.HTTPException as e:
                    await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("You don't have permission to manage roles.")

    @commands.command(aliases=['ne'])
    async def newemoji(self, ctx, url: str, *, name):
        """Create a new emoji from a URL"""
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_emojis:
            async with aiohttp.ClientSession() as ses:
                try:
                    async with ses.get(url) as r:
                        try:
                            img_or_gif = BytesIO(await r.read())
                            b_value = img_or_gif.getvalue()
                            if r.status in range(200, 299):
                                emoji = await guild.create_custom_emoji(image=b_value, name=name)
                                ej = get(ctx.message.guild.emojis, name=name)
                                await ctx.send(f"EMOJI: \"{str(ej)}\"", embed=discord.Embed(title="Emoji "+str(name), description=f'New Emoji Created!!\nCheck the command for the emoji reaction', color=0X0EEE0F).set_thumbnail(url=url))
                                emj = get(ctx.guild.emojis, name=name)
                                await ctx.message.add_reaction(emj)
                                await ses.close()
                            else:
                                await ctx.send(embed=discord.Embed(title=f":o: ERROR :o:", description=f'Request status: {r.status}\nOnly `.png` And `.gif.` Extensions are allowed.', color=0xFF0000))
                                await ses.close()
                        except discord.HTTPException as e:
                            await ctx.send(embed=discord.Embed(title=f':o:File size is more than 256KB:o:', color=0xFF0000))
                except:
                    await ctx.send(embed=discord.Embed(title=":o:Unsupported Format!!:o:", description=f'Only PNG and GIF formats are supported\n**Or**\nThe url isn\'t a direct url ie, the url should end with [.png] or [.gif].', color=0xFF0000))
        else:
            await ctx.send(embed=discord.Embed(title=":x:PERMISSIONS:x:", description='You don\'t have "Manage Emojis" Permission!!!', color=0xFF0000))


    @commands.has_permissions(manage_emojis=True)
    @commands.command(aliases=["de"])
    async def delemoji(self, ctx, *emojis: discord.Emoji):
        """Delete an emoji"""
        if not emojis:
            return await ctx.send("specify at least one emoji to delete.")
        
        for emoji in emojis:
            try:
                await emoji.delete()
                await ctx.send(f"Emoji `{emoji.name}` deleted!")
            except Exception as e:
                await ctx.send(embed=discord.Embed(title=f":o: Unable to delete emoji :o:", description=f"Error: {e}", color=0xFF0000))

    @commands.command(aliases=['e'])
    async def emojis(self, ctx, *emoji_names):
        """List emojis the bot can access"""
        if emoji_names:
            found = []
            for name in emoji_names:
                emoji = discord.utils.get(self.bot.emojis, name=name)
                if emoji:
                    found.append((emoji, emoji.guild.name))
            if not found:
                return await ctx.send("No matching emojis found.")
            embed = discord.Embed(title="Matching Emojis", color=discord.Color.blurple())
            for emoji, guild in found:
                embed.add_field(name=guild, value=str(emoji), inline=True)
            await ctx.send(embed=embed)
        else:
            guilds = {}
            for emoji in self.bot.emojis:
                if emoji.guild.name not in guilds:
                    guilds[emoji.guild.name] = []
                guilds[emoji.guild.name].append(str(emoji))
            if not guilds:
                return await ctx.send("No emojis available.")
            embeds = []
            for guild, emojis in guilds.items():
                embed = discord.Embed(title=guild, description=" ".join(emojis), color=discord.Color.green())
                embeds.append(embed)
            await Paginator.Simple().start(ctx, pages=embeds)


    @commands.command(aliases=['docs'])
    async def rtfm(self, ctx, docs: str, *, term: str = None):
        """
        Documentiation refercence for discord.py and python
        """
        docs = docs.lower()
        target=None
        try:
            for aliases, target_name in self.rtfmaliases.items():
                if docs in aliases:
                    target = target_name
            if not term:
                return await ctx.reply(self.targets[target])
        except:
            lis = "\n".join(
                [f"{index}. {value.capitalize()}" for index, value in list(self.targets.keys())]
            )
            return await ctx.reply(
                embed=ctx.error(
                    title="Invalid",
                    description=f"**{docs}** isnt supprted, try\n{lis}",
                )
            )
        cache = self.cache.get(target)
        if not cache:
            await ctx.typing()
            try:
                await self.build(target)
            except RtfmBuildError:
                return await ctx.send("An error occurred.")
            cache = self.cache.get(target)
        results = rtfmutils.finder(term, list(cache.items()), key=lambda x: x[0], lazy=False)[:10]
        if not results:
            return await ctx.reply(f"No results found for **{term}** in **{docs}** Docs")
        await ctx.reply(
            embed=discord.Embed(
                title=f"Matches related to **{term}** in **{docs}** Docs",
                description="\n".join([f"[`{key}`]({url})" for key, url in results]),
                color=discord.Color.dark_theme(),
                timestamp=ctx.message.created_at).set_footer(text=ctx.author.name,icon_url=ctx.author.avatar)
            )
    

    @commands.command(aliases=["ui"])
    async def userinfo(self, ctx, user: discord.User):
        """Get a user's info"""
        member = ctx.guild.get_member(user.id) if ctx.guild else None
        is_member = isinstance(member, discord.Member)

        embed = discord.Embed(
            title=f"Info on {user}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=f"{user}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot?", value=user.bot, inline=True)
        embed.add_field(name="Badges", value=", ".join(badges) if badges else "None", inline=False)

        if is_member:
            badges = [str(flag).split('.')[-1] for flag in member.public_flags.all()]
            embed.description = "Here's what I know:"
            embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
            embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
            embed.add_field(name="Roles", value=", ".join(r.mention for r in member.roles[1:]) or "None", inline=False)
            embed.add_field(name="Badges", value=", ".join(badges) if badges else "None", inline=False)
            embed.add_field(name="Boosting Since", value=member.premium_since.strftime('%Y-%m-%d %H:%M:%S') if member.premium_since else "Not Boosting", inline=True)
            embed.add_field(name="Status", value=str(member.status).title(), inline=True)
            embed.add_field(name="Activity", value=member.activity.name if member.activity else "None", inline=True)
        else:
            embed.description = "idk this guy"
            embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
            flags = [str(flag).split('.')[-1] for flag in user.public_flags.all()]
            embed.add_field(name="Badges", value=", ".join(flags) if flags else "None", inline=False)

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
