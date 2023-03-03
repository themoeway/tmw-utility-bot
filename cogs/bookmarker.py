
import discord
import json
from discord.ext import commands
from discord import app_commands
from datetime import date as new_date, datetime, timedelta


#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
#############################################################

class Extras(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @app_commands.command(name='bookmark', description='Sends you a dm of the message you want to save.')
    async def bookmark(self, interaction: discord.Interaction, message_link: str):
        message_link = message_link.split('/')
        channel = await self.bot.fetch_channel(message_link[5])
        reaction_message = await channel.fetch_message(message_link[6])
        for reaction in reaction_message.reactions:
            async for user in reaction.users():
                if interaction.user == user and reaction.emoji == '🔖':
                    guild = self.bot.get_guild(guild_id)
                    author = reaction_message.author
                    reacted_at = datetime.now()
                    embed = discord.Embed(title=f"New 🔖 saved from {guild}'s {channel.name} channel", description=f'You added this bookmark on {reacted_at.strftime("%a %d %H:%M:%S")}\n', color=discord.Color.blurple())
                    embed.add_field(name='Link', value=f'{reaction_message.jump_url}', inline=False)
                    if len(reaction_message.content) > 900:
                        embed.add_field(name="Content",value=f'{reaction_message.content[:900]}', inline=False)                
                    if len(reaction_message.content) < 900:
                        embed.add_field(name="Content",value=f'{reaction_message.content}', inline=False)
                    try:
                        pfp = author.avatar.url
                    except:
                        embed.set_footer(text=f'From {author}  |  Posted on {reaction_message.created_at.strftime("%a %d %H:%M:%S")}')
                    else:
                        embed.set_footer(icon_url=(pfp), text=f'From {author}  |  Posted on {reaction_message.created_at.strftime("%a %d %H:%M:%S")}')
                    if reaction_message.attachments:
                        if reaction_message.attachments[0].filename.endswith(".png") or reaction_message.attachments[0].filename.endswith(".jpg") or reaction_message.attachments[0].filename.endswith(".jpeg"):
                            url = reaction_message.attachments[0].proxy_url
                            embed.set_image(url=url)
                        if reaction_message.attachments[0].filename.endswith('.zip') or reaction_message.attachments[0].filename.endswith('.txt') or reaction_message.attachments[0].filename.endswith('.apkg') or reaction_message.attachments[0].filename.endswith('.mp4') or reaction_message.attachments[0].filename.endswith('.mp3'):
                            attachments = '\n'.join([attachment.filename for attachment in reaction_message.attachments])
                            embed.add_field(name='File', value=f"{attachments}")
                    try:
                        await interaction.user.send(embed=embed)
                    except discord.errors.Forbidden:
                        return await interaction.response.send_message(ephemeral=True, content=f'<@{interaction.user.id}> please change your privacy settings to ``Allow direct messages from server members``. Jump back to the bookmarked message {reaction.message.jump_url}.', suppress_embeds=True)
                    else:
                        return await interaction.response.send_message(ephemeral=True, content=f'A DM has been sent to you. Jump back to the bookmarked message {reaction.message.jump_url}.', suppress_embeds=True)
        await interaction.response.send_message(ephemeral=True, content=f'You need to react with a 🔖 to the message you want to bookmark. Jump back to the bookmarked message {reaction.message.jump_url}.', suppress_embeds=True)
    
    # @app_commands.command(name='rm_bookmark', description='Removes one bookmark in DM.')  
    # async def rm_bookmark(self, interaction: discord.Interaction, message_link: str):
    #     await interaction.response.defer()          
    #     if not isinstance(interaction.channel.type, discord.DMChannel):
    #         return
    #     message_link = message_link.split('/')
    #     channel = await self.bot.fetch_channel(message_link[5])
    #     reaction_message_id = await channel.fetch_message(message_link[6])
    #     reaction_message = await interaction.channel.fetch_message(reaction_message_id)
    #     await reaction_message.delete()
    #     await interaction.edit_original_response(content='Deleted message.')
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extras(bot), guilds=[discord.Object(id=guild_id)])