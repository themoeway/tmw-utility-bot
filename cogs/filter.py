import discord
from discord.ext import commands
import json

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = data_dict["guild_id"]
    
with open("cogs/jsons/roles.json", encoding="utf-8") as file:
    data = json.load(file)
    roles = data["roles"]

#############################################################

class Filter(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
    
    async def json_change(self, id):
        with open("cogs/jsons/filter.json", "r+") as file:
            data = json.load(file)
            data["filter"].append(id)
            file.seek(0)
            json.dump(data, file)
            
    @commands.command(hidden=True)
    @commands.has_any_role("Moderator", "Administrator")
    async def filter(self, ctx, id):
        """
        Excludes messages.
        """
        if id.isnumeric():
            id = int(id)
            await self.json_change(id)
        else:
            await ctx.send("Please choose a valid message id.")
        
def setup(bot):
    bot.add_cog(Filter(bot))
