import discord
from discord.ext import commands
import git
import os


class BotManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def reload_cog(self, ctx, cog: str):
        try:
            await self.bot.reload_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await ctx.message.author.send(f"Could not unload {cog}")
            return
        if cog == "all":
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    await self.bot.reload_extension(f"cogs.{filename[:-3]}")
                    print(f"Reloaded the following cog: {filename}")
        else:
            print(f"Reloaded the following cog: {cog}")

    @commands.command(hidden=True)
    async def update(self, ctx):
        repo = git.Repo("bookmarkbot")
        repo.remotes.origin.pull()
        await ctx.send("Pulled updated.")


async def setup(bot):
    await bot.add_cog(BotManager(bot))
