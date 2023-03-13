import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from discord.ui import Select
from discord.utils import get
import asyncio
from typing import Optional
import json
from discord.ext import tasks
import re 
import asyncpg
from dateutil.relativedelta import relativedelta
from datetime import datetime

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    guild_id = 617136488840429598
    book_sharing_id = data_dict["book_sharing"]
    audio_sharing_id = data_dict["audio_sharing"]
    vn_sharing_id = data_dict["vn_sharing"]
        
class Selfmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = []
        self.batch_update.add_exception_type(asyncpg.PostgresConnectionError)
        self.batch_update.start()
        
    def cog_unload(self):
        self.batch_update.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.tmw = self.bot.get_guild(617136488840429598)
        self.selfmute = self.tmw.get_role(1058369629740871750)
        self.batch_update.start()

    async def store_roles(self, id, roles, date):
        print(id, roles, date)
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        cur.execute("INSERT INTO mutes (user_id, roles, time) VALUES (?,?,?)", (int(id), str(roles), str(date)))
        con.commit()
        cur.close()
    
    async def get_muted_members(self):
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        query = """SELECT * FROM mutes"""
        cur.execute(query)
        con.commit()
        mutes = cur.fetchall()
        con.close()
        
        return mutes
    
    async def delete_mute(self, user_id):
        con = sqlite3.connect('mutes.db')
        cur = con.cursor()
        query = """DELETE FROM mutes WHERE user_id = ?"""
        data = ([user_id])
        cur.execute(query, data)
        con.commit()
        cur.close()

    @app_commands.command(name="selfmute", description="Mute yourself. UTC")
    @app_commands.checks.has_role("Administrator")
    async def request(self, interaction: discord.Interaction, hours: Optional[int] = 0, minutes: Optional[int] = 0, seconds: Optional[int] = 0):   
        import datetime
        if self.selfmute in interaction.user.roles:
            return
        date = discord.utils.utcnow() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        roles = [role.id for role in interaction.user.roles]
        await interaction.response.send_message(f"Alright {interaction.user.mention}, selfmute till {date}", ephemeral=True)
        await self.store_roles(interaction.user.id, roles, date)
        date = date.strftime("%H:%M:%S")
        await asyncio.sleep(3)
        for id in roles:
            role = self.tmw.get_role(id)
            if role.name == "@everyone":
                continue
            await interaction.user.remove_roles(role)
        await interaction.user.add_roles(self.selfmute)
    
    @tasks.loop(seconds=5)
    async def batch_update(self):
        mutes = await self.get_muted_members()
        now = discord.utils.utcnow()
        for mute in mutes:
            id = mute[0]
            when = mute[2]
            try:
                if datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f%z") < now:
                    self.tmw = self.bot.get_guild(guild_id)
                    self.selfmute = self.tmw.get_role(1058369629740871750)
                    member = self.tmw.get_member(int(id))
                else:
                    return
            except Exception:
                pass
            else:
                member = self.tmw.get_member(int(id))
                await member.remove_roles(self.selfmute)
                for role_id in mute[1].strip('][').split(', '):
                    if int(role_id) == 617136488840429598:
                        continue
                    try:
                        role = self.tmw.get_role(int(role_id))
                    except Exception:
                        continue
                    else:
                        await member.add_roles(role)
                await self.delete_mute(int(id))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Selfmute(bot))                    