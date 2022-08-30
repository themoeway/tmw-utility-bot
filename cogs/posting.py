import discord
from discord.ext import commands
import sqlite3
import datetime
from datetime import timedelta
import pytz
import asyncio
from collections import Counter
import json
import re

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    look_back_days = data_dict["look_back_days"] # 7 days
    wait_time = data_dict["wait_time"] # 6hrs
    fetch_channel_id = data_dict["resource-sharing"]
    guild_id = data_dict["guild_id"]

#############################################################


class Posting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        self.log_channel = discord.utils.get(self.myguild.channels, name="bookmark-list")
        self.log_channel_id = self.log_channel.id

    async def delete(self, ctx):
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages")
        info = cur.fetchall()
        limit = len(info)+5
        await self.log_channel.purge(limit=limit)

    async def recursion(self, ctx):
        await asyncio.sleep(wait_time)

        await self.delete(ctx)
        await self.create_message(ctx)

    async def create_message(self, ctx):
        channel = await self.bot.fetch_channel(int(fetch_channel_id))
        utc = pytz.UTC
        startw0 = datetime.datetime.today()
        endw1 = startw0 - timedelta(int(look_back_days))
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages ORDER BY bookmarks DESC")
        info = cur.fetchall()

        count = 1
        for (user_id, message_id, reaction_amount, content, link, create_date, attachments, keywords) in info:
            if keywords == "[]":
                keywords = ""
            else:
                keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                keywords = keywords.replace(" ", " | ")
            message = await channel.fetch_message(message_id)
            if message.created_at < utc.localize(startw0) and message.created_at > utc.localize(endw1):
                red_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})', color=discord.Color.from_rgb(255, 0, 0))
                user = await self.bot.fetch_user(int(user_id))
                pfp = user.avatar.url
                red_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                    red_embed.set_thumbnail(url=attachments)
                await channel.send(embed=red_embed)
                count += 1
            else:
                my_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})')
                user = await self.bot.fetch_user(int(user_id))
                pfp = user.avatar.url
                my_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                    my_embed.set_thumbnail(url=attachments)
                await channel.send(embed=my_embed)
                count += 1

        await self.keyword_assignment(ctx)
        await self.changelog(ctx)

    async def create_embed(self, ctx):
        date = datetime.datetime.today()
        date = date.strftime("%Y/%m/%d %H:%M:%S")
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(
            f"SELECT bookmarks, link FROM bookmarked_messages ORDER BY bookmarks ASC LIMIT 1")
        first_list_link = cur.fetchone()[1]
        info_embed = discord.Embed(title=f'Jump to the highest bookmarked message',color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
        info_embed.add_field(name=f'Changelog', value=f'- Categorization of each list item (700 most occuring words in resource-sharing, DM the bot with "t.words_db" for the DB) \n - Red coloring on embed indicates that the message is not older than a week \n - Attachment filename and image is now displayed \n - Post date of message was added')
        user = ctx.message.author
        pfp = user.avatar.url
        info_embed.set_footer(
            icon_url=(pfp), text=f'From {ctx.message.author}  |  List from {date}')

        return info_embed
    
    async def keyword_assignment(self, ctx):
        con = sqlite3.connect('bookmark-list.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages ORDER BY reaction_amount DESC")
        embed_messages = cur.fetchall()

        prep_list = []
        catergorization = []
        for (reaction_amount, username, message_content, message_link, message_date, attachments, keywords) in embed_messages:
            if keywords != "[]":
                keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                prep_list.append(keywords)
        for i in prep_list:
            for j in i.split():
                catergorization.append(j)
        freq = Counter(catergorization)
        counters = {str(k): v for k, v in freq.items()}
        sorted_freq = {k: v for k, v in sorted(counters.items(), key=lambda item: item[1], reverse=True)}

        f = open("catergories.txt", "w", encoding="utf-8")
        for r in range(len(sorted_freq)):
            for word, frequency in sorted_freq.items():
                f.write(f"{word}: {frequency} \n")
        con.close()
    
    async def changelog(self, ctx):
        info_embed = await self.create_embed(ctx)
        await self.log_channel.send(embed=info_embed)
        await self.recursion(ctx)

    @commands.command(hidden=True)
    async def start(self, ctx):
        await self.create_message(ctx)

def setup(bot):
    bot.add_cog(Posting(bot))