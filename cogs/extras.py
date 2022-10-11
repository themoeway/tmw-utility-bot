from unicodedata import name
import discord
import json
from discord.ext import commands
from discord.ext import tasks
from datetime import timedelta
from discord import app_commands
import asyncio

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

    @app_commands.command(name="github", description="Get a link to the github repository hosting the code for this bot")
    async def github(self, interaction: discord.Interaction):
        link = "https://github.com/Timm04/timmbookmarkbot"
        await interaction.response.send_message(link)
    
    @app_commands.command(name="gitbook", description="Get the link to the gitbook.")
    async def gitbook(self, interaction: discord.Interaction):
        link = "https://timm-1.gitbook.io/bookmarklistbot/"
        await interaction.response.send_message(link)
    
    @app_commands.command(name="settings", description="Displays the search settings.")
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'```json\n{json.dumps(data, indent=4, sort_keys=True)}\n```')
        
    async def edit_results_post(self, role, results_msg, beginning_index, end_index):
        embed = discord.Embed(title=f"Role {role}", description=f"In total {len(role.members)} users have the {role} role.", color=discord.Color.blurple())
        for member in role.members[beginning_index:end_index]:
            embed.add_field(name=f"{member}", value="\u200b")
        if len(role.members) >= 70:
            embed.set_footer(text="... not all results displayed but you can pick any index.\n"
                                    "Pick an index to retrieve a scene next.")
        else:
            embed.set_footer(text="Pick an index to retrieve a scene next.")

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
        
    @app_commands.command(name="ranktable", description="See the rank distribution.")
    async def ranktable(self, interaction: discord.Interaction):
        idol_roles = ['Eternal Idol', 'Divine Idol', 'Prima Idol', 'Major Idol', 'Debut Idol', 'Trainee', 'Student']
        idol_count = ([role.name and len(role.members) for role in interaction.guild.roles if role.name in idol_roles])
        embed = discord.Embed(title=f"Role Distribution", description=f'{idol_roles[0]}: {idol_count[6]}\n{idol_roles[1]}: {idol_count[5]}\n{idol_roles[2]}: {idol_count[4]}\n{idol_roles[4]}: {idol_count[3]}\n{idol_roles[4]}: {idol_count[2]}\n{idol_roles[5]}: {idol_count[1]}\n{idol_roles[6]}: {idol_count[0]}\n\nTotal member count: {interaction.guild.member_count}',color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="tmw_reading_ranking", description="Returns an excel sheet of a bookmeter and vndb ranking.")
    async def tmw_reading_ranking(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://docs.google.com/spreadsheets/d/1se6GUAH5EfSYJ-yIdlppd5MjqUEobZo1Tn9mzZGUm-w/edit#gid=436577013")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
            
    @app_commands.command(name="vn_club_point_system", description="Returns a google sheet of VNs and their associated points.")
    async def vn_club_point_system(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://docs.google.com/document/d/e/2PACX-1vTtIPq9MXzu0m1g5aZvUykWoJhyVODwOgb8dDJP_B-hMqgtNZBUP9mQtr_5vTW-ICLTlG3uFWEWGUVX/pub")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
            
    @app_commands.command(name="tmw_vn_picks", description="Returns a vndb account of all VNs the VN club played.")
    async def tmw_vn_picks(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://vndb.org/u209617/ulist?q=&l=2&s=800")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
    
    @app_commands.command(name="tmw_novel_picks", description="Returns the bookmeter of the Novel club.")
    async def tmw_novel_picks(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://bookmeter.com/users/1313898/books/read")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
            
    @app_commands.command(name="tmw_manga_picks", description="Returns the MAL of the Manga club.")
    async def tmw_manga_picks(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://myanimelist.net/profile/TMW_MangaClub")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
            
    @app_commands.command(name="tmw_joseimuke_picks", description="Returns an excel sheet of the Joseimuke club picks.")
    async def tmw_joseimuke_picks(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("https://docs.google.com/spreadsheets/d/1pHSFB3EH6ARdgHo-l0KAGsprM5Zfcewxxt-eF9Q3Ixo/edit#gid=1333508788")    
        except Exception:
            await interaction.response.send_message("Something went wrong", ephemeral=True)
    
    @app_commands.command(name="solved", description="Marks a thread as solved.")
    async def solved(self, interaction: discord.Interaction):
        assert isinstance(interaction.channel, discord.Thread)
        await interaction.response.send_message(f'{interaction.user} closed the thread.')
        await interaction.channel.edit(locked=True, archived=True, reason=f'Marked as solved by {interaction.user} (ID: {interaction.user.id}')
    
    @app_commands.command(name='reset', description='Resets the quiz cooldown for a user.')
    @app_commands.checks.has_role("Moderator")
    @app_commands.choices(quizcommand= [Choice(name="Eternal vocab", value="k!quiz jpdb20k+jpdb25k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Divine vocab", value="k!quiz jpdb15k+jpdb20k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="GN1", value="k!quiz gn1 nd 20 mmq=4"), Choice(name="GN2", value="k!quiz gn2 nd 20 mmq=4"), Choice(name="Prima vocab", value="k!quiz jpdb10k+jpdb15k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Major Idol", value="k!quiz jpdb5k+jpdb10k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Debut Idol", value="k!quiz jpdb2_5k+jpdb5k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Trainee", value="k!quiz jpdb1k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100")])
    async def reset(self, interaction: discord.Interaction, user: discord.Member, quizcommand: str):
        await interaction.response.defer()
        user_id = user.id
        con = sqlite3.connect('/root/book/quiz_attempts.db')
        cur = con.cursor()
        query = "DELETE FROM attempts WHERE discord_user_id=? AND quiz_level=?;"
        data = (int(user_id), str(quizcommand))
        cur.execute(query, data)
        con.commit()
        con.close()
        await interaction.edit_original_response(content=f'Reset the cooldown for <@{user.id}> on ``{quizcommand}``.')
    
    async def get_unix(self):
        con = sqlite3.connect('/root/book/quiz_attempts.db')
        cur = con.cursor()
        query = "SELECT STRFTIME('%s', DATE('now', '+' || (7 - STRFTIME('%w')) || ' days'));"
        cur.execute(query)
        return cur.fetchone()
        
    async def get_cooldowns(self, user_id):    
        con = sqlite3.connect('/root/book/quiz_attempts.db')
        cur = con.cursor()
        query = """SELECT * FROM attempts WHERE discord_user_id=? AND created_at >= DATE('now', '-' || STRFTIME('%w') || ' days') """
        data = (user_id)
        cur.execute(query, (data,))
        return cur.fetchall()
        
    @app_commands.command(name='cooldowns', description='Shows the quiz cooldowns of a user.')
    async def cooldowns(self, interaction: discord.Interaction, user: discord.Member):
        user_id = user.id
        cooldowns = await self.get_cooldowns(user_id)
        unixstamp = await self.get_unix()
        #await interaction.channel.send("\n".join([format + cooldown[1] + format for cooldown in cooldowns]))
        if cooldowns != []:
            embed = discord.Embed(title=f'''{user}'s quiz cooldowns''', description=f'The following commands are on cooldown untill <t:{int(unixstamp[0])}:R> at <t:{unixstamp[0]}>.', color=discord.Color.blurple())
            format = r"``"
            cooldowns = "\n".join([format + cooldown[1] + format for cooldown in cooldowns])
            embed.add_field(name='Commands', value=f'{cooldowns}')
        if cooldowns == []: 
            embed = discord.Embed(title=f'''{user}'s quiz cooldowns''', description=f'{user} has no commands on cooldown.', color=discord.Color.blurple())
            embed.add_field(name='Commands', value=f'No cooldowns.')
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="test", description="test.")
    @app_commands.checks.has_role("Moderator")
    async def test(self, interaction: discord.Interaction, emoji: str):
        embed = discord.Embed(title="TEst", description="dad")
        embed.set_thumbnail(url="https://s2.vndb.org/cv/21/27521.jpg")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Extras(bot), guilds=[discord.Object(id=guild_id)])
