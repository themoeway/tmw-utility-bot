from venv import create
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
    output_channel_id = data_dict["bookmark-list"]
    fetch_channel_id = data_dict["resource-sharing"]
    bot_id = data_dict["bot_id"]
    guild_id = data_dict["guild_id"]
    
with open("cogs/jsons/filter.json") as file:
    data = json.load(file)
    ids = data["filter"]
    
with open("cogs/jsons/content.json") as content_file:
    data = json.load(content_file)
    title = data["title"]
    content = data["content"]
    
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
        channel = await self.bot.fetch_channel(int(output_channel_id))
        utc = pytz.UTC
        startw0 = datetime.datetime.today()
        print(startw0)
        endw1 = startw0 - timedelta(int(look_back_days))
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages ORDER BY bookmarks DESC")
        info = cur.fetchall()

        count = 1
        for (user_id, message_id, reaction_amount, content, link, create_date, attachments, keywords) in info:
            if message_id not in ids:
                if keywords == "[]":
                    keywords = ""
                else:
                    keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                    keywords = keywords.replace(" ", " | ")
                create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S.%f%z")
                if create_date < utc.localize(startw0) and create_date > utc.localize(endw1):
                    create_date = create_date.strftime("%b %d %Y")
                    red_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})', color=discord.Color.from_rgb(255, 0, 0))
                    user = await self.bot.fetch_user(int(user_id))
                    pfp = user.avatar.url
                    red_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                    if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                        red_embed.set_thumbnail(url=attachments)
                    await channel.send(embed=red_embed)
                    count += 1
                else:
                    create_date = create_date.strftime("%b %d %Y")
                    my_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})')
                    user = await self.bot.fetch_user(int(user_id))
                    pfp = user.avatar.url
                    my_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                    if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                        my_embed.set_thumbnail(url=attachments)
                    await channel.send(embed=my_embed)
                    count += 1

        await self.keyword_assignment()
        await self.changelog(ctx, channel)
    
    async def keyword_assignment(self):
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages ORDER BY bookmarks DESC")
        embed_messages = cur.fetchall()

        prep_list = []
        catergorization = []
        for (user_id, message_id, reaction_amount, content, link, create_date, attachments, keywords) in embed_messages:
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
    
    async def create_embed(self, ctx):
        date = datetime.datetime.today()
        date = date.strftime("%b %d %Y")
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(
            f"SELECT bookmarks, link FROM bookmarked_messages ORDER BY bookmarks ASC LIMIT 1")
        first_list_link = cur.fetchone()[1]
        info_embed = discord.Embed(title=f'Jump to the highest bookmarked message',color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
        info_embed.add_field(name=f'{title}', value=f'{content}')
        user = await self.bot.fetch_user(int(bot_id))
        pfp = user.avatar.url
        info_embed.set_footer(icon_url=(pfp), text=f'From {ctx.message.author}  |  List from {date}')

        return info_embed
    
    async def changelog(self, ctx, channel):
        info_embed = await self.create_embed(ctx)
        await channel.send(embed=info_embed)
        await self.recursion(ctx)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        msg_1 = await ctx.send(f'Do you want to preceed with these settings? Yes/No \n```json\n {json.dumps(data_dict, indent=4, sort_keys=True)}\n```')
        def user_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=user_check, timeout=60)
        allowed = ["Yes", "y", "yes", "YES", "Y"]
        if msg.content in allowed:
            msg_2 = await ctx.send("Settings have been saved. Starting fetch in 3...")
            await asyncio.sleep(0.5)
            await msg_2.delete()
            await asyncio.sleep(0.5)
            await msg.delete()
            await asyncio.sleep(0.5)
            await msg_1.delete()
            await asyncio.sleep(0.5)
            await ctx.message.delete()
            await self.create_message(ctx)
        else:
            msg_3 = await ctx.send("Cancelled quick setup.")
            await asyncio.sleep(0.5)
            await msg_3.delete()
            await asyncio.sleep(0.5)
            await msg.delete()
            await asyncio.sleep(0.5)
            await msg_1.delete()
            await asyncio.sleep(0.5)
            await ctx.message.delete()
            

def setup(bot):
    bot.add_cog(Posting(bot))