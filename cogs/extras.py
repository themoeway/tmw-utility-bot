import discord
import re
import asyncio
import json
from discord.ext import commands
from discord.ext import tasks
from datetime import timedelta

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = data_dict["guild_id"]

#############################################################

class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @commands.command()
    async def github(self, ctx):
        """Get a link to the github repository hosting the code for this bot."""
        link = "https://github.com/Timm04/timmbookmarkbot"
        await ctx.send(link)
                
def setup(bot):
    bot.add_cog(Extras(bot))