import discord
from discord.ext import commands
import git
import os


class BotManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, cog):
        try:
            if not cog == "all":
                self.bot.reload_extension(f'cogs.{cog}')
                print(f"Reloaded the following cog: {cog}")
            else:
                for filename in os.listdir("./cogs"):
                    if filename.endswith(".py"):
                        self.bot.reload_extension(f"cogs.{filename[:-3]}")
                        print(f"Reloaded the following cog: {filename}")
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await ctx.message.author.send(f"Could not reload {cog}")
            return

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        repo = git.Repo("bookmarkbot")
        repo.remotes.origin.pull()
        await ctx.send("Pulled updated.")

def setup(bot):
    bot.add_cog(BotManager(bot))