import discord
from discord.ext import commands
import sqlite3
from discord.utils import get
import asyncio
import re

#############################################################

#files
amount = 1
guild_id = 947813835715256390 #TMW GUILD ID

#############################################################

class List(commands.Cog):
    #Commands in relation to the List
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        self.log_channel = discord.utils.get(self.myguild.channels, name="bookmark-list")

    async def count_reactions(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        for reaction in reaction_message.reactions:
            if reaction.emoji == '🔖':
                if reaction.count >= amount:
                    return reaction.count

    async def new_or_old_message(self, payload):
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute("SELECT discord_user_id, message_id FROM bookmarked_messages")
        database = cur.fetchall()
        message_ids = []
        for row in database:
            message_ids.append(row[1])
        #payload id cannot be identifed in message_ids ???
        if payload.message_id in message_ids:
            return
        else:
            return

    async def keyword_assignment(self, payload):
        con = sqlite3.connect("words.db")
        cur = con.cursor()
        words = cur.fetchall()
        con.commit()
        con.close()
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        b = 0
        prep_list = []
        for keywords in words:
            if b >= 3:
                break
            if keywords[0] in reaction_message.content:
                keyword = keywords[0]
                prep_list.append(keyword)
                b += 1
        displayed_keywords = []
        for keywords in prep_list:
            if keywords != "[]":
                keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                displayed_keywords.append(keywords)

        return displayed_keywords

    async def adding_to_db(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        reaction = get(reaction_message.reactions)
        displayed_keywords = await self.keyword_assignment(payload)
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute('INSERT INTO bookmarked_messages (discord_user_id, bookmarks, message_id, content, link, created_at, attachments, keywords) VALUES (?,?,?,?,?,?,?,?)', 
        (int(reaction_message.author.id), int(reaction.count) , int(reaction_message.id) , str(reaction_message.content), str(reaction_message.jump_url), str(reaction_message.created_at) ,str(reaction_message.attachments), str(displayed_keywords)))
        con.commit()
        con.close()

    async def update_db(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute("SELECT bookmarks, content FROM bookmarked_messages WHERE message_id=?", (int(reaction_message.id)))
        reaction_messages = cur.fetchall()
        for match in reaction_messages:
            if match != reaction_message.reaction.count or match != reaction_message.content:
                cur.execute("UPDATE bookmarked_message SET bookmarks=? and content=? WHERE message_id=?", (int(reaction_message.reaction.count), str(reaction_message.content) ,int(reaction_message.id)))
        con.commit()
        con.close()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.log_channel:
            await asyncio.sleep(0.25)
            enough_reactions = await self.count_reactions(payload)
            if enough_reactions:
                await asyncio.sleep(0.25)
                new_bookmarked_message = await self.new_or_old_message(payload)
                if not new_bookmarked_message:
                    print("not in db")
                    await asyncio.sleep(0.25)
                    await self.adding_to_db(payload)
                else:
                    await asyncio.sleep(0.25)
                    print("in db")
                    await self.update_db(payload)

async def setup(bot):
    await bot.add_cog(List(bot))