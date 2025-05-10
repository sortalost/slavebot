import aiohttp
import discord
from discord.ext import commands
from discord.utils import get
import sys
from io import BytesIO

class Utils(commands.Cog):
    """Utility commands <:ver_devUS:869794681251332177>"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logchannel = bot.get_channel(877473404117209191)
        self.lastmsg = {}

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

    @commands.command(name="emojis", help="List emojis the bot can access")
    async def emojis(self, ctx, *emoji_names):
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
