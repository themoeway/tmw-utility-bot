import discord
import re
import asyncio
import json
from discord.ext import commands
from discord.ext import tasks
from datetime import timedelta

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
with open("cogs/jsons/info.json") as file:
    data_dict = json.load(file)

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
    
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        """Displays the settings."""
        await ctx.send(f'```json\n{json.dumps(data, indent=4, sort_keys=True)}\n```')
                
def setup(bot):
    bot.add_cog(Extras(bot))