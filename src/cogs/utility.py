import discord
import aiohttp
from discord.ext import commands
from discord.utils import get
from io import BytesIO
import sys
import os



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
            embed.add_field(name="channel", value=f"{m.channel.mention}", inline=False)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
            eb.append(embed)
        return eb[::-1]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot == True:
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
            return await ctx.send("Usage is `.purge 16` to delete last 16 messages")
        num = num + 1
        await ctx.channel.purge(limit=num)

    @commands.command(aliases=['nr'])
    async def newrole(self, ctx, *, name):
        """Create a new role in the server"""
        if ctx.author.guild_permissions.manage_roles:
            await ctx.guild.create_role(name=name, color=0x00FF00)
            try:
                await ctx.send(embed=discord.Embed(title=f"New Role: {name}",
                                                   description=f"**{name} has been created\nAdd Members to this role via ```{prefix}GiveRole [USER] [ROLE]```**",
                                                   color=0xFF0000))
            except:
                await ctx.send(embed=discord.Embed(title=f"New Role: {name}",
                                                   description=f"**{name} has been created\nAdd Members to this role via ```{prefix}GiveRole [USER] [ROLE]```**",
                                                   color=0xFF0000).set_footer(
                    text=f"You got this message as I wasn't able to send messages in {ctx.channel.name}"))
        else:
            await ctx.send(embed=discord.Embed(title=":x:PERMISSIONS:x:",
                                               description='You don\'t have "Manage Roles" Permission',
                                               color=0xFF0000))

    # @NewRole.error
    # async def errorrole(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(embed=discord.Embed(title=":x:PARAMETER MISSING:x:", description=f'```{prefix}newrole [NAME]```',
    #                                            color=0xFF0000))
    #     else:
    #         try:
    #             await ctx.send(embed=discord.Embed(description=f"**Encountered Unknown Error(s)**```{sys.exc_info()}```\n"))
    #         except:
    #             await ctx.author.send(f"Couldn't send this message in {ctx.message.channel.mention}, so...",
    #                                   embed=discord.Embed(description=f"**Encountered Unknown Error**```{sys.exc_info()}```"))


    @commands.command(aliases=['ne'])
    async def newemoji(self, ctx, url: str, *, name):
        """Create a new emoji in the server"""
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
                                await ctx.send(f"EMOJI: \"{str(ej)}\"",
                                               embed=discord.Embed(title="Emoji " + str(name),
                                                                   description=f'New Emoji Created!!\nCheck the command for the emoji reaction',
                                                                   color=0X0EEE0F).set_thumbnail(url=url))
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

    # @newemoji.error
    # async def newmeoji_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(embed=discord.Embed(title=":x:PARAMETER MISSING:x:", description=f'```{prefix}newemoji [URL] [NAME]```', color=0xFF0000))
    #     elif isinstance(error, discord.Forbidden):
    #         try:
    #             await ctx.send(embed=discord.Embed(title=":x:MISSING PERMISSIONS:x:", description=f'```{prefix}newemoji [URL] [NAME]```\nLooks like I\'m Missing Some permissions:\n```{error}```', color=0xFF0000))
    #         except:
    #             await ctx.author.send(embed=discord.Embed(title=":x:MISSING PERMISSIONS:x:", description=f'```{prefix}newemoji [URL] [NAME]```\nLooks like I\'m Missing Some permissions:\n```{error}```', color=0xFF0000))

    @commands.command(aliases=['de'])
    async def delemoji(self, ctx, *, emoji: discord.Emoji):
        """Delete an emoji in the server."""
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_emojis:
            try:
                await emoji.delete()
                await ctx.send("Emoji Successfully Deleted!!")
            except Exception as e:
                await ctx.send(embed=discord.Embed(title=f':o:Unable to delete the Emoji:o:', description=f'Error: {e}', color=0xFF0000))
        else:
            perm = 'Manage Emojis'
            await ctx.send(f"{ctx.author.mention},", embed=discord.Embed(title="Missing Permissions", description=f'You don\'t have `{perm}` Permission!!\nAsk the Server Owner to give you the permission', color=0xFF0000))


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
