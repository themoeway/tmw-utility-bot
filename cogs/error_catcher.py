from datetime import datetime
from time import time
import discord
import re
import json
from discord.ext import commands
from discord import app_commands

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    admin_user_id = data["creator_id"]

#############################################################

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        admin_user = self.myguild.get_member(admin_user_id)
        await admin_user.create_dm()
        self.private_admin_channel = admin_user.dm_channel
        
        await self.private_admin_channel.send("Bot started.")
      
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        else:
            raise error  
        
    @commands.Cog.listener()
    async def on_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingAnyRole):
            await interaction.response.send_message("You do not have the permission to use this command.", ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"This command is currently on cooldown. You can use this command again after {int(error.retry_after)} seconds.", ephemeral=True)
        elif isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message(f'I did something wrong, please try again.', ephemeral=True)
        elif isinstance(error, app_commands.AppCommandError):
            await interaction.response.send_message(f'I did something wrong, please try again.', ephemeral=True)
        else:
            await self.private_admin_channel.send(f"{str(error)}\n\nTriggered by: `{interaction.message.content}`\n"
                                                  f"Here: {interaction.message.jump_url}")
            raise error

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot), guilds=[discord.Object(id=guild_id)])
