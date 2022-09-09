from this import d
from xml.dom.minicompat import EmptyNodeList
import discord
from discord.ext import commands
from discord import app_commands
import json
from discord.ui import Select, View

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = data_dict["guild_id"]

#############################################################

class MyHelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        
    @app_commands.command(name="help", description="Shows info about the bot.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'Server: {interaction.guild}', color=discord.Color.blurple(), description=f'{self.bot.user.name} commands in this server start with ``kt$``')
        embed.add_field(name="Help & Support", value="Refer to Timm#3250\n[Gitbook](https://timm-1.gitbook.io/bookmarklistbot/)\n[Github](https://github.com/Timm04/timmbookmarkbot)")
        item = discord.ui.Button(style=discord.ButtonStyle.secondary, label=f"Intive {self.bot.user.name}", url="https://discord.com/api/oauth2/authorize?client_id=1014211242065395774&permissions=1532498406512&scope=bot%20applications.commands")
        view = View()
        view.add_item(item)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyHelpCommand(bot), guilds=[discord.Object(id=guild_id)])