from discord.ext import commands
import discord
from paginator import Paginator  # replace with your actual paginator import

class Help(commands.HelpCommand):
    def __init__(self, no=[]):
        super().__init__()
        self.no = no

    async def send_bot_help(self, mapping):
        ctx = self.context
        prefix = self.clean_prefix
        embeds = []
        for cog, cmds in mapping.items():
            cmds = [c for c in cmds if not c.hidden and c.name not in self.no]
            if not cmds:
                continue
            embed = discord.Embed(title=cog.qualified_name if cog else "uncategorized", color=discord.Color.blurple(), description="")
            for command in cmds:
                embed.description += f"`{prefix}{command.name}` - {command.help or '**no description**'}\n"
            embeds.append(embed)
        if not embeds:
            await ctx.send("No commands available.")
            return
        await Paginator.Simple().start(ctx, pages=embeds)
