
import discord
import json
from discord.ext import commands
from discord import app_commands
import asyncio

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
divine = [834999083512758293, 1026924690029170718]

#############################################################

class Ranks(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @app_commands.command(name="ranktable", description="See the rank distribution.")
    async def ranktable(self, interaction: discord.Interaction):
        idol_roles = ['Eternal Idol', 'Divine Idol', 'Prima Idol', 'Major Idol', 'Debut Idol', 'Trainee', 'Student']
        idol_count = ([role.name and len(role.members) for role in interaction.guild.roles if role.name in idol_roles])
        embed = discord.Embed(title=f"Role Distribution", description=f'''{idol_roles[0]}: {idol_count[6]}\n{idol_roles[1]}: {idol_count[5]}\n{idol_roles[2]}: {idol_count[4]}\n{idol_roles[3]}: {idol_count[3]}\n{idol_roles[4]}: {idol_count[2]}\n{idol_roles[5]}: {idol_count[1]}\n{idol_roles[6]}: {idol_count[0]}\n\nTotal member count: {interaction.guild.member_count}''',color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)
        
    async def edit_results_post(self, role, results_msg, beginning_index, end_index):
        embed = discord.Embed(title=f"Role {role}", description=f"In total {len(role.members)} users have the {role} role.", color=discord.Color.blurple())
        for member in role.members[beginning_index:end_index]:
            embed.add_field(name=f"{member}", value="\u200b")
        if len(role.members) >= 70:
            embed.set_footer(text="... not all results displayed but you can pick any index.\n"
                                    "Pick an index to go to the next page.")
        else:
            embed.set_footer(text="Pick an index to go to the next page.")

        await results_msg.edit(embed=embed)    
        
    @app_commands.command(name="rankuser", description="See all users with a specific role.")
    async def rankuser(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer()
        embed = discord.Embed(title=f"Role {role}", description=f"In total {len(role.members)} users have the {role} role.", color=discord.Color.blurple())
        for member in role.members[0:70]:
            embed.add_field(name=f"{member}", value="\u200b")
        if len(role.members) >= 70:
            embed.set_footer(text="... not all results displayed but you can pick any index.\n"
                                    "Pick an index to go to the next page.")
        else:
            embed.set_footer(text="Pick an index to go to the next page.")
            
        results_message = await interaction.edit_original_response(embed=embed)
        await results_message.add_reaction('⬅️')
        await results_message.add_reaction('➡️')
        
        def reaction_check(reaction, user):
            allowed_emoji = ['⬅️', '➡️']
            return user.id == interaction.user.id and str(reaction.emoji) in allowed_emoji and reaction.message.id == results_message.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=25.0, check=reaction_check)
            await reaction.remove(user)
            beginning_index = 0
            end_index = 70
            reaction_string = str(reaction.emoji)
            while reaction_string == "⬅️" or reaction_string == "➡️":
                if reaction_string == "⬅️":
                    beginning_index -= 70
                    end_index -= 70
                    if beginning_index < 0:
                        beginning_index = 0
                        end_index = 70
                    await self.edit_results_post(role, results_message, beginning_index, end_index)
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=reaction_check)
                    await reaction.remove(user)
                    reaction_string = str(reaction.emoji)

                elif reaction_string == "➡️":
                    beginning_index += 70
                    end_index += 70
                    if beginning_index >= len(role.members):
                        beginning_index -= 70
                        end_index -= 70
                    await self.edit_results_post(role, results_message, beginning_index, end_index)
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=reaction_check)
                    await reaction.remove(user)
                    reaction_string = str(reaction.emoji)

                else:
                    await interaction.channel.send("Unexpected error. Exiting...")

        except asyncio.TimeoutError:
            await interaction.channel.send("Function timed out. Exiting...")
            return

        if str(reaction.emoji) == '❌':
            await interaction.channel.send("Exiting...")
            return
        else:
            await interaction.channel.send("Exiting...")
            return
        
    # @app_commands.command(name="rank", description="Debugs gatekeeper bot.")
    # async def rank(self, interaction: discord.Interaction, currentroleid: discord.Role, newrankid: discord.Role):
    #     await interaction.response.defer()
    #     print(currentroleid, newrankid)
    #     myguild = interaction.guild
    #     interaction_user = interaction.user
    #     currentrole = myguild.get_role(currentroleid.id)
    #     newrank = myguild.get_role(newrankid.id)
    #     await self.role_behavior(interaction_user, currentrole, newrank)
    
    # async def role_behavior(self, interaction_user, currentrole, newrank):
    #     e = 0
    #     d = 0
    #     p = 0
    #     roles = [currentrole, newrank]
    #     for role in roles:
    #         if role.id in divine:
    #             d += 1
    #     print(f'e = {e}, d = {d}, p = {p}')
    #     if d == 2:
    #         print('d satisfied')
    #         currentrole = self.myguild.get_role(divine[1])
    #         await interaction_user.remove_roles(currentrole)
    #         newrankid = 1026918330566721576 #divine idol
    #         newrole = self.myguild.get_role(newrankid)
    #         await interaction_user.add_roles(newrole)
    #         # store.save_role_info(mainuserid, newrankid, created_at)
    #     if newrankid == 1026922492884951121 or newrankid == 1026924690029170718 or newrankid == 1027706897731702846:
    #         print("passed ")
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ranks(bot), guilds=[discord.Object(id=guild_id)])