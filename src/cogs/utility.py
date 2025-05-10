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
    @commands.command(help="Create a new role with a color")
    async def newrole(self, ctx, name: str, color: str):
        """Create a new role with the specified name and color"""
        try:
            color_int = int(color, 16)
        except ValueError:
            return await ctx.send("Invalid color format. Please provide a valid hex color code.")
        
        role = await ctx.guild.create_role(name=name, color=color_int)
        await ctx.send(embed=discord.Embed(title=f"New Role: {name}", description=f"**{role.mention}** has been created.", color=color_int))

    @commands.has_permissions(manage_roles=True)
    @commands.command(alia=['gr'])
    async def giverole(self, ctx, role: discord.Role, *users: discord.User):
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
    async def delemoji(self, ctx, *, emoji: discord.Emoji):
        """Delete an emoji"""
        try:
            await emoji.delete()
            await ctx.send("Emoji successfully deleted!")
        except Exception as e:
            await ctx.send(embed=discord.Embed(title=f":o: Unable to delete emoji :o:", description=f"Error: {e}", color=0xFF0000))

async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
