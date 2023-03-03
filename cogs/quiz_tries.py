
import discord
import json
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import sqlite3

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    
#############################################################

class Quizes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    async def delete_try(self, user_id, quizcommand):
        con = sqlite3.connect('/root/book/quiz_attempts.db')
        cur = con.cursor()
        query = "DELETE FROM attempts WHERE discord_user_id=? AND quiz_level=?;"
        data = (int(user_id), str(quizcommand))
        cur.execute(query, data)
        con.commit()
        return con.close()
    
    @app_commands.command(name='reset', description='Resets the quiz cooldown for a user.')
    @app_commands.checks.has_role("Moderator")
    @app_commands.choices(quizcommand= [Choice(name="Eternal vocab", value="k!quiz jpdb20k+jpdb25k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Divine vocab", value="k!quiz jpdb15k+jpdb20k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="GN1", value="k!quiz gn1 nd 20 mmq=4"), Choice(name="GN2", value="k!quiz gn2 nd 20 mmq=4"), Choice(name="Prima vocab", value="k!quiz jpdb10k+jpdb15k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Major Idol", value="k!quiz jpdb5k+jpdb10k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Debut Idol", value="k!quiz jpdb2_5k+jpdb5k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"), Choice(name="Trainee", value="k!quiz jpdb1k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100")])
    async def reset(self, interaction: discord.Interaction, user: discord.Member, quizcommand: str):
        await interaction.response.defer()
        user_id = user.id
        await self.delete_try(user_id, quizcommand)
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
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Quizes(bot), guilds=[discord.Object(id=guild_id)])