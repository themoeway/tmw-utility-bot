from sqlite3 import Row
import discord
from discord.ui import Select, View
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import json

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = data_dict["guild_id"]

class BotManager(commands.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="reload_cog", description="Reloads cogs.")
    @app_commands.checks.has_role("Moderator")
    async def reload_cog(self, interaction: discord.Interaction):
        my_view = CogSelectView(timeout=1800)
        for cog_name in [extension for extension in self.bot.extensions]:
            cog_button = ReloadButtons(self.bot, label=cog_name)
            my_view.add_item(cog_button)
        await interaction.response.send_message(f"Please select the cog you would like to reload.",
                                                view=my_view,
                                                ephemeral=True)
        # options = []
        # for filename in os.listdir("./cogs"):
        #     if filename.endswith(".py"):
        #         item = discord.SelectOption(label=f'cogs.{filename}')
        #         options.append(item)
                
        # async def my_callback(interaction):
        #     for cog in select.values:
        #         await self.bot.reload_extension(f"{cog[:-3]}")
        #     selected_values = "\n".join(select.values)
        #     await interaction.response.send_message(f'Reloaded the following cog:\n{selected_values}')

        # select = Select(min_values = 1, max_values = int(len(options)), options=options)   
        # select.callback = my_callback
        # view = View()
        # view.add_item(select)
        # await interaction.response.send_message(f'Please select the cog you would like to reload.', view=view)
        
    @app_commands.command(name="stop", description="Stops cogs.")
    @app_commands.checks.has_role("Moderator")
    async def stop(self, interaction: discord.Interaction):
        if interaction.command_failed:
            await interaction.response.send_message(f'I had a brain fart, try again please.', ephemeral=True)
        options = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                item = discord.SelectOption(label=f'cogs.{filename}')
                options.append(item)
        async def my_callback(interaction):
            for cog in select.values:
                await self.bot.unload_extension(f"{cog[:-3]}")
            selected_values = "\n".join(select.values)
            await interaction.response.send_message(f'Unloaded the following cog:\n{selected_values}')

        select = Select(min_values = 1, max_values = int(len(options)), options=options)   
        select.callback = my_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message(f'Please select the cog you would like to reload.', view=view)
        
    @app_commands.command(name="sync", description="Syncs slash commands to the guild.")
    @app_commands.checks.has_role("Moderator")
    async def sync(self, interaction: discord.Interaction):
        self.bot.tree.copy_global_to(guild=discord.Object(id=guild_id))
        await self.bot.tree.sync(guild=discord.Object(id=guild_id))
        await interaction.response.send_message(f'Synced commands to guild with id {guild_id}.')
    
class CogSelectView(discord.ui.View):

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

class ReloadButtons(discord.ui.Button):

    def __init__(self, bot: commands.Bot, label):
        super().__init__(label=label)
        self.bot = bot

    async def callback(self, interaction):
        cog_to_reload = self.label
        await self.bot.reload_extension(cog_to_reload)
        await interaction.response.send_message(f"Reloaded the following cog: {cog_to_reload}")
        print(f"Reloaded the following cog: {cog_to_reload}")
        await asyncio.sleep(10)
        await interaction.delete_original_response()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotManager(bot), guilds=[discord.Object(id=guild_id)])
