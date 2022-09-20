import asyncio
import discord
from discord.ext import commands
import sqlite3
from discord import app_commands
from discord.app_commands import Choice

class Books(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("d")
     
    #Deletes books of a club
        
    async def get_all_books(self, club_code):
        con = sqlite3.connect('prod_copy.db')
        cur = con.cursor()    
        cur.execute(f"SELECT * FROM activities WHERE club_code='{club_code}'")
        BOOKS = cur.fetchall()
        
        return BOOKS
        
    @app_commands.command(name="remove_books", description="Removes all the books of a club.")
    @app_commands.choices(media = [Choice(name="VN", value="VN")])
    async def remove_books(self, interaction: discord.Interaction, club_code: str):
        #bc! delete_book <code>
        BOOKS = await self.get_all_books(club_code)
        for (guild, name, code, points, created_at, club) in BOOKS:
            await interaction.channel.send(f"bc! delete_book {code}")
            await asyncio.sleep(1)
        print("done")
        await interaction.channel.send("Done")
        
    async def get_new_books(self, club_code):
        con = sqlite3.connect('kleine.db')
        cur = con.cursor()    
        cur.execute(f"SELECT * FROM activities WHERE club_code='{club_code}'")
        BOOKS = cur.fetchall()
        
        return BOOKS
    
    #Readds same books but with new point values
    @app_commands.command(name="batch_add", description="Adds a new set of books from a db.")
    @app_commands.choices(media = [Choice(name="VN", value="VN")])
    async def batch_add(self, interaction: discord.Interaction, club_code: str):
        #bc! new_book <club_code> <name> <code> [points=2.0] [created_at]
        BOOKS = await self.get_new_books(club_code)
        for (guild, name, code, points, created_at, club) in BOOKS:
            await interaction.channel.send(f"bc! new_book {club_code} {name} {code} {points}")
            await asyncio.sleep(1)
        print("done")
        await interaction.channel.send("Done")
        
    #Readds the users who have finished VNs
    @app_commands.command(name="let_books_finished", description="Finishes every book in db for specified users.")
    @app_commands.choices(media = [Choice(name="VN", value="VN")])
    async def let_books_finished(self, interaction: discord.Interaction, club_code: str):
        #bc! finished <member> <book_code> [points]
        BOOKS_to_finish = await self.get_new_books(club_code)
        for (guild, club, book_code, user_id, points) in BOOKS_to_finish:
            await interaction.channel.send(f"bc! finished {user_id} {book_code}")
            await asyncio.sleep(1)
        print("done")
        await interaction.channel.send("Done")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Books(bot))