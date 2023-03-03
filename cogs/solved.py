
import discord
import json
from discord.ext import commands
from discord import app_commands


#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
#############################################################

class Solved(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @app_commands.command(name="solved", description="Marks a thread as solved.")
    async def solved(self, interaction: discord.Interaction):
        if interaction.user.id == 694499855174992032: #jsph :))
            return
        assert isinstance(interaction.channel, discord.Thread)
        await interaction.response.send_message(f'{interaction.user} closed the thread.')
        await interaction.channel.edit(locked=True, archived=True, reason=f'Marked as solved by {interaction.user} (ID: {interaction.user.id}')
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Solved(bot), guilds=[discord.Object(id=guild_id)])