
import discord
import json
from discord.ext import commands
from discord import app_commands
import asyncpg
from datetime import date as datetime
from discord.ext import tasks
from discord.utils import get


#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
#############################################################

class Solved(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.batch_update.add_exception_type(asyncpg.PostgresConnectionError)
        self.batch_update.start()
        
    def cog_unload(self):
        self.batch_update.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        self.questions_forum = get(self.tmw.channels, name='questions-forum') or self.tmw.get_channel(1019998042654511106)
        self.batch_update.start()

    @app_commands.command(name="solved", description="Marks a thread as solved.")
    async def solved(self, interaction: discord.Interaction):
        assert isinstance(interaction.channel, discord.Thread)
        await interaction.response.send_message(f'{interaction.user} closed the thread.')
        await interaction.channel.edit(locked=True, archived=True, reason=f'Marked as solved by {interaction.user} (ID: {interaction.user.id}')
        
    @app_commands.command(name="slow_mode", description="Set a TextChannel to slowmode.")
    @app_commands.checks.has_role("Moderator")
    async def slow_mode(self, interaction: discord.Interaction, channel: discord.TextChannel, delay: int):
        await channel.slowmode_delay(delay)
        await interaction.response.send_message(ephemeral=True, content=f'Set {channel} to {delay} seconds delay.')
        
    @tasks.loop(hours=24)
    async def batch_update(self):
        self.questions_forum = get(self.tmw.channels, name='questions-forum') or self.tmw.get_channel(1019998042654511106)
        now = datetime.now()
        for thread in self.questions_forum.threads:
            if thread.archived:
                continue
            if (now - thread.created_at.replace(tzinfo=None)).days >= 15:
                if 1014211242065395774 not in [member.id for member in await thread.fetch_members()]:
                    await thread.send(f'{thread.owner.mention} has your problem been solved? If so, do  ``/solved`` to close this thread.')
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Solved(bot), guilds=[discord.Object(id=guild_id)])
