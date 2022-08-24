import discord
from discord.ext import commands
import git

class BotManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.has_any_role("Moderator", "Administrator", "第四話　雨、逃げ出した後")
    async def reload_cog(self, ctx, cog_name):
        self.bot.reload_extension("cogs." + cog_name)
        self.bot.dispatch("ready")
        # Manually dispatching an event is very bad in this case and could lead to breakage. When I have time I will
        # rewrite the cogs to address this issue and properly enable reloading.
        await ctx.send(f"Reloaded the cog: {cog_name}")

    @commands.command(hidden=True)
    @commands.has_any_role("Moderator", "Administrator", "第四話　雨、逃げ出した後")
    async def update(self, ctx):
        """Pull update to ubuntu server."""
        repo = git.Repo('/home/ubuntu/djt_bot_3')
        repo.remotes.origin.pull()
        await ctx.send("Pulled updated.")

async def setup(bot):
    await bot.add_cog(BotManager(bot))