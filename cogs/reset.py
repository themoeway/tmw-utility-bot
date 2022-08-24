import discord
from discord.ext import commands

class Reset(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Moderator", "Administrator", "第四話　雨、逃げ出した後")
    async def stop(self, ctx):
        await self.bot.reload_extension(f'cogs.posting.py')
        print("Reloaded posting list cog.")

async def setup(bot):
    await bot.add_cog(Reset(bot))