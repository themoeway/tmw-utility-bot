import discord
import json
from discord.ext import commands
from discord.ui import Button, View
from datetime import date as new_date, datetime, timedelta


#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]

#############################################################

class Bookmark(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        
    async def dm_bookmark(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        author = await self.bot.fetch_user(reaction_message.author.id)
        react_user = payload.member
        reacted_at = datetime.now()
        embed = discord.Embed(title=f"New 🔖 saved from {guild}'s {channel.name} channel", description=f'You added this bookmark on {reacted_at.strftime("%a %d %H:%M:%S")}\n', color=discord.Color.blurple())
        embed.add_field(name='Link', value=f'{reaction_message.jump_url}', inline=False)
        embed.add_field(name="Content",value=f'{reaction_message.content}', inline=False)
        pfp = author.avatar.url
        embed.set_footer(icon_url=(pfp), text=f'From {author}  |  Posted on {reaction_message.created_at.strftime("%a %d %H:%M:%S")}')
        if reaction_message.attachments:
            if reaction_message.attachments[0].filename.endswith(".png") or reaction_message.attachments[0].filename.endswith(".jpg") or reaction_message.attachments[0].filename.endswith(".jpeg"):
                url = reaction_message.attachments[0].proxy_url
                embed.set_image(url=url)
        button = Button(label="Remove", style=discord.ButtonStyle.danger)
        async def button_callback(interaction):
            msg = interaction.message
            await msg.delete()
        button.callback = button_callback
        view = View(timeout=None)
        view.add_item(button)
        #await react_user.send(embed=embed, view=view)
        try:
            await react_user.send(embed=embed, view=view)
        except Exception:
            await channel.send(f"<@{react_user.id}> please change your privacy settings to ``Allow direct messages from server members``.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bookmark(bot))