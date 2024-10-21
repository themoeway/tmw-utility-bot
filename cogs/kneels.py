import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import sys


millnames = ['','k','m','b']
        
class Kneels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cache = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.tmw = self.bot.get_guild(617136488840429598)
        self.selfmute = self.tmw.get_role(1058369629740871750)

    async def store_data2(self, kneel_message, kneel_count):
        con = sqlite3.connect('kneels2.db')
        cur = con.cursor() 
        cur.execute("""INSERT INTO kneels (discord_user_id, message_id, kneel_score, channel_id, message_created_at, users) VALUES (?,?,?,?,?,?)""", (int(kneel_message.author.id), int(kneel_message.id), int(kneel_count), int(kneel_message.channel.id), str(kneel_message.created_at)))
        con.commit()
        con.close()  

    async def store_data(self, kneel_message, kneel_count):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        cur.execute("""INSERT INTO kneels (discord_user_id, message_id, kneel_score, channel_id, message_created_at) VALUES (?,?,?,?,?)""", (int(kneel_message.author.id), int(kneel_message.id), int(kneel_count), int(kneel_message.channel.id), str(kneel_message.created_at)))
        con.commit()
        con.close()  
    
    @app_commands.command(name="get_kneel_data", description="ikneel")
    @app_commands.checks.has_role("Moderator")
    async def get_kneel_data(self, interaction: discord.Interaction, target_channel: discord.ForumChannel):
        await interaction.response.defer(ephemeral=True)
        async for message in target_channel.history(oldest_first=False, limit=100000000000):
            kneel_count = []
            for reaction in message.reactions:
                if reaction.emoji == "🧎" or reaction.emoji == "🧎‍♂️" or reaction.emoji == "🧎‍♀️" or str(reaction.emoji) == "<:ikneel:1018615871326912623>" or str(reaction.emoji.name).startswith("ikneel"):
                    kneel_count.append(reaction.count)
                    continue
                else:
                    continue
            if kneel_count == []:
                continue
            else:
                await self.store_data(message, sum(kneel_count))
        await interaction.edit_original_response(content=f'Done with {target_channel}')
    
    async def get_leaderboard(self, interaction):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        query = f"""
        WITH scoreboard AS (
            SELECT
                discord_user_id,
                SUM(
                kneel_score
                ) AS total
            FROM kneels
            GROUP BY discord_user_id
            ), leaderboard AS (
            SELECT
                discord_user_id,
                total,
                RANK () OVER (ORDER BY total DESC) AS rank
            FROM scoreboard
            )
            SELECT * FROM leaderboard
            WHERE (
            rank <= 20
            ) OR (
            rank >= (SELECT rank FROM leaderboard WHERE discord_user_id = ?) - 1
            AND
            rank <= (SELECT rank FROM leaderboard WHERE discord_user_id = ?) + 1
            );
        """
        data = (interaction.user.id, interaction.user.id,)
        cur.execute(query, data)
        return cur.fetchall()

    @app_commands.command(name="kneelderboard", description="ikneel")
    async def kneel_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=f'Kneeling...')
        leaderboard = await self.get_leaderboard(interaction)
        leaderboard_length = 20
        user_rank = [rank for uid, total, rank in leaderboard if uid == interaction.user.id]
        user_rank = user_rank and user_rank[0]
        
        def make_ordinal(n):
            '''
            Convert an integer into its ordinal representation::

                make_ordinal(0)   => '0th'
                make_ordinal(3)   => '3rd'
                make_ordinal(122) => '122nd'
                make_ordinal(213) => '213th'
            '''
            n = int(n)
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
            if 11 <= (n % 100) <= 13:
                suffix = 'th'
            return f'{n}{suffix}'
        
        async def leaderboard_row(user_id, points, rank):
            ellipsis = '...\n' if user_rank and rank == (user_rank-1) and rank > 21 else ''
            try:
                user = await self.bot.fetch_user(user_id)
                display_name = user.display_name if user else 'Unknown'
            except Exception:
                display_name = 'Unknown'
            return f'{ellipsis}**{make_ordinal(rank)} {display_name}**: {points}'

        leaderboard_desc = '\n'.join([await leaderboard_row(*row) for row in leaderboard])
        title = "Kneel scoreboard"
        embed = discord.Embed(title=title, description=leaderboard_desc)

        await interaction.edit_original_response(embed=embed)
        
    async def db_compare_existing(self, kneel_message):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor()
        query = """SELECT EXISTS(
        SELECT * FROM kneels WHERE message_id=?
        ) AS didTry"""
        cur.execute(query, [kneel_message.message_id])
        bool = cur.fetchall()[0][0] == 1
        
        return bool
    
    async def add_kneel_score(self, kneel_message):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        score_query = """SELECT * FROM kneels WHERE message_id=?"""
        cur.execute(score_query, [kneel_message.message_id])
        score = cur.fetchall()[0][2] 
        
        score = score + 1
        
        query = """UPDATE kneels SET kneel_score=? WHERE message_id=?"""
        cur.execute(query, (score, kneel_message.message_id))
        con.commit()
        con.close()

        
    async def new_kneel_message(self, kneel_message):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        cur.execute("""INSERT INTO kneels (discord_user_id, message_id, kneel_score, channel_id, message_created_at) VALUES (?,?,?,?,?)""", (int(kneel_message.author.id), int(kneel_message.id), int(1), int(kneel_message.channel.id), str(kneel_message.created_at)))
        con.commit()
        con.close()    
        
    async def subtract_kneel_score(self, kneel_message):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        score_query = """SELECT * FROM kneels WHERE message_id=?"""
        cur.execute(score_query, [kneel_message.message_id])
        score = cur.fetchall()[0][2] 
        
        score = score - 1
        
        query = """UPDATE kneels SET kneel_score=? WHERE message_id=?"""
        cur.execute(query, (score, kneel_message.message_id))
        con.commit()
        con.close()
    
    async def check_reaction(self, payload):
        tmw = await self.bot.fetch_guild(payload.guild_id)
        channel = await tmw.fetch_channel(payload.channel_id)
        kneel_message = await channel.fetch_message(payload.message_id)
        if kneel_message.author.id == payload.user_id:
            return
        if str(payload.emoji) == "🧎" or str(payload.emoji) == "🧎‍♂️" or str(payload.emoji) == "🧎‍♀️" or str(payload.emoji) == "<:ikneel:1018615871326912623>" or str(payload.emoji.name).startswith("ikneel"):
            bool = await self.db_compare_existing(payload)
            if bool:
                if str(sys._getframe().f_back.f_code.co_name) == "on_raw_reaction_remove":
                    return await self.subtract_kneel_score(payload)
                else:
                    return await self.add_kneel_score(payload)
            else:
                return await self.new_kneel_message(kneel_message)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.check_reaction(payload)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.check_reaction(payload)
        
    async def find_kneel_message(self):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        score_query = """SELECT * FROM kneels ORDER BY kneel_score DESC"""
        cur.execute(score_query)
        data = cur.fetchall()
        
        return data
        
    @app_commands.command(name="kneelmessage", description="Finds messages that were reacted to with a kneel. Place=1 will return the most kneeled message.")
    async def kneelmessage(self, interaction: discord.Interaction, place: int):
        await interaction.response.defer(ephemeral=True)
        data = await self.find_kneel_message()
        try:
            channel = await interaction.guild.fetch_channel(int(data[place - 1][3]))
            message = await channel.fetch_message(int(data[place - 1][1]))
        except Exception:
            return await interaction.edit_origina_response(content=f'Message got deleted. It had data[0][2] kneels.')
        await interaction.edit_original_response(content=f'{place}# kneeled message: {message.jump_url}')

    async def update_kneel_score(self, message, count):
        con = sqlite3.connect('kneels.db')
        cur = con.cursor() 
        score_query = """UPDATE kneels SET kneel_score=? WHERE message_id=?"""
        cur.execute(score_query, (count, message.id))
        con.commit()
        con.close()
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Kneels(bot))                    
