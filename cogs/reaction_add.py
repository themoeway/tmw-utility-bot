from email import message
from itertools import count
from pickle import FALSE
import discord
from discord.ext import commands
import sqlite3
from discord.utils import get
import asyncio
import re
import json
import datetime

from bookmark import Bookmark

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    amount = data_dict["amount"]
    guild_id = data_dict["guild_id"]
    output_channel_id = data_dict["bookmark-list"]
    max_char = data_dict["max_char"]
    
with open("cogs/jsons/filter.json") as file:
    data = json.load(file)
    ids = data["filter"]

#############################################################


class reaction_add(commands.Cog):
    # Adds or updates messages based on their bookmarks
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        self.log_channel = discord.utils.get(self.myguild.channels, name="bookmark-list")

    async def count_reactions(self, payload):
        if payload.message_id not in ids:
            log = datetime.datetime.today()
            log = log.strftime("%Y/%m/%d %H:%M:%S")
            channel = self.bot.get_channel(payload.channel_id)
            reaction_message = await channel.fetch_message(payload.message_id)
            for reaction in reaction_message.reactions:
                if reaction.emoji == '🔖':
                    print(f'{log} {reaction_message.jump_url} has 🔖')
                    await Bookmark.dm_bookmark(self, payload)
                    if reaction.count >= amount:
                        print(f'{log} {reaction_message.jump_url} has {reaction.count}')
                        return reaction.count
                    else:
                        print(f'{log} {reaction_message.jump_url} < {amount}')
                        return "filtered"
                else:
                    return "filtered"
        else:
            return "filtered"

    async def new_or_old_message(self, payload):
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(
            "SELECT discord_user_id, message_id FROM bookmarked_messages")
        database = cur.fetchall()
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        message_ids = []
        for row in database:
            message_ids.append(row[1])
        if reaction_message.id in message_ids:
            return "exist"

    async def keyword_assignment(self, payload):
        con = sqlite3.connect('words.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM 'resource_sharing' ORDER BY freqs DESC")
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

    async def user_name_removal(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        split_message = reaction_message.content.split()
        user_id_list = []
        for e in split_message:
            if e.startswith("<@"):
                user_id_raw = re.findall("\<\@(.*?)\>", e)
                user_id = str(user_id_raw).strip("['']")
                user_id_new = re.sub('\D', '', user_id)
                user_id_list.append(user_id_new)

        user_name_list = []
        for r in user_id_list:
            user_name = await self.bot.fetch_user(r)
            user_name_list.append(str(user_name))

        for i in range(len(split_message)):
            if split_message[i].startswith("<@"):
                split_message[i] = user_name_list[0]
                del user_name_list[0]
        
        reaction_message_content = " ".join(str(g) for g in split_message)
        return reaction_message_content
                
    async def adding_to_db(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        reaction = get(reaction_message.reactions)
        displayed_keywords = await self.keyword_assignment(payload)
        reaction_message_content = await self.user_name_removal(payload)
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute('INSERT INTO bookmarked_messages (discord_user_id, bookmarks, message_id, content, link, created_at, attachments, keywords) VALUES (?,?,?,?,?,?,?,?)',
                    (int(reaction_message.author.id), int(reaction.count), int(reaction_message.id), str(reaction_message_content[:max_char]), str(reaction_message.jump_url), str(reaction_message.created_at), str(reaction_message.attachments), str(displayed_keywords)))
        con.commit()
        con.close()
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Added {reaction_message.jump_url} to DB')

    async def update_db(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction_message = await channel.fetch_message(payload.message_id)
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        count = max([reaction.count for reaction in reaction_message.reactions])
        displayed_keywords = await self.keyword_assignment(payload)
        reaction_message_content = await self.user_name_removal(payload)
        reaction_message_content = "\n" + str(reaction_message_content)
        update_query = """UPDATE bookmarked_messages SET bookmarks=?, content=?, keywords=? WHERE message_id=?"""
        cur.execute(update_query, (int(count), "\n" + str(reaction_message_content[:max_char]), str(displayed_keywords), int(reaction_message.id)))
        con.commit()
        con.close()
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Updated {reaction_message.jump_url} in DB')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != int(output_channel_id):
            await asyncio.sleep(0.25)
            enough_reactions = await self.count_reactions(payload)
            if enough_reactions != "filtered":
                await asyncio.sleep(0.25)
                bookmarked_message = await self.new_or_old_message(payload)
                if bookmarked_message != "exist":
                    await asyncio.sleep(0.25)
                    await self.adding_to_db(payload)
                else:
                    await asyncio.sleep(0.25)
                    await self.update_db(payload)

async def setup(bot):
    await bot.add_cog(reaction_add(bot))
