import discord
from discord.ext import commands
import json
from discord import app_commands

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = data_dict["guild_id"]
    
with open("cogs/jsons/roles.json", encoding="utf-8") as file:
    data = json.load(file)
    roles = data["roles"]

#############################################################

class Filter(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
    
    async def json_change(self, message_id):
        with open("cogs/jsons/filter.json", "r+") as file:
            data = json.load(file)
            data["filter"].append(message_id)
            file.seek(0)
            json.dump(data, file)
            
    @app_commands.command(name="filter", description="Filters out messages to be posted.")
    @app_commands.checks.has_role("Moderator")
    async def filter(self, interaction: discord.Interaction, message_id: int):
        await interaction.response.send_message(f'Added message with id {message_id} to filter.', ephemeral=True)
        await self.json_change(message_id)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Filter(bot), guilds=[discord.Object(id=guild_id)])