from discord.ext import commands
import discord
import Paginator


class Help(commands.HelpCommand):
    def __init__(self, no=[], bot):
        super().__init__()
        self.bot = bot
        self.no = no

    async def send_bot_help(self, mapping):
        ctx = self.context
        prefix = ctx.clean_prefix
        desc = ""
        i = 0
        for cog in self.bot.cogs:
            i+=1
            desc+=f"{str(i)}. `{cog}` - {self.bot.cogs[cog].description}\n"
        embed1 = discord.Embed(title="Categories", description = desc, color=discord.Color.random())
        embeds = [embed1]
        for cog, cmds in mapping.items():
            visible_cmds = [c for c in cmds if not c.hidden and c.name not in self.no]
            if not visible_cmds:
                continue
            embed = discord.Embed(title=cog.qualified_name if cog else "Uncategorized", color=discord.Color.blurple(), description="")
            for command in visible_cmds:
                if isinstance(command, commands.Group):
                    for sub in command.commands:
                        if not sub.hidden and sub.name not in self.no:
                            full_name = f"{command.qualified_name} {sub.name}"
                            embed.description += f"`{prefix}{full_name}` - {sub.help or 'No description'}\n"
                else:
                    embed.description += f"`{prefix}{command.qualified_name}` - {command.help or 'No description'}\n"
            embeds.append(embed)
        if not embeds:
            return await ctx.send("No commands available.")
        await Paginator.Simple().start(ctx, pages=embeds)
