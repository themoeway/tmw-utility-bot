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
        # self.log_channel = discord.utils.get(self.myguild.channels, name="bookmark-list")
        # self.log_channel_id = self.log_channel.id

    async def delete(self, ctx, channel):
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages")
        info = cur.fetchall()
        limit = len(info)+4
        await channel.purge(limit=limit)

    async def recursion(self, ctx, channel):
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Waiting for list deletion')
        await asyncio.sleep(wait_time)
        await self.delete(ctx, channel)
        await self.create_message(ctx, channel)
    
    async def create_message(self, ctx, channel):
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Wating for list output')
        await asyncio.sleep(15)
        utc = pytz.UTC
        startw0 = datetime.datetime.today()
        endw1 = startw0 - timedelta(int(look_back_days))
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM bookmarked_messages WHERE bookmarks=17")
        #cur.execute(f"SELECT * FROM bookmarked_messages ORDER BY bookmarks DESC")
        info = cur.fetchall()

        count = 1
        for (user_id, message_id, reaction_amount, content, link, create_date, attachments, keywords) in info:
            if message_id not in ids:
                if keywords == "[]":
                    keywords = ""
                else:
                    keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                    keywords = keywords.replace(" ", " | ")
                print(create_date)
                create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S.%f%z")
                print(create_date)
                print(utc.localize(startw0))
                if create_date < utc.localize(startw0) and create_date > utc.localize(endw1):
                    print("red")
                    create_date = create_date.strftime("%b %d %Y")
                    red_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})', color=discord.Color.from_rgb(255, 0, 0))
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                    except Exception:
                        user_name = "Deleted User"
                        red_embed.set_footer(text=f'From {user_name}  |  Posted on {create_date}')
                        if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                            red_embed.set_thumbnail(url=attachments)
                        await channel.send(embed=red_embed)
                        count += 1
                    else:
                        try:
                            pfp = user.avatar.url
                        except Exception:
                            red_embed.set_footer(text=f'From {user}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                red_embed.set_thumbnail(url=attachments)
                            await channel.send(embed=red_embed)
                            count += 1
                        else:
                            red_embed.set_footer(icon_url=(pfp), text=f'From {user}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                red_embed.set_thumbnail(url=attachments)
                            await channel.send(embed=red_embed)
                            count += 1
                else:
                    create_date = create_date.strftime("%b %d %Y")
                    my_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})')
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                    except Exception:
                        user_name = "Deleted User"
                        my_embed.set_footer(text=f'From {user}  |  Posted on {create_date}')
                        if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                            my_embed.set_thumbnail(url=attachments)
                        await channel.send(embed=my_embed)
                        count += 1
                    else:
                        try:
                            pfp = user.avatar.url
                        except Exception:
                            my_embed.set_footer(text=f'From {user}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                my_embed.set_thumbnail(url=attachments)
                            await channel.send(embed=my_embed)
                            count += 1
                        else:
                            my_embed.set_footer(icon_url=(pfp), text=f'From {user}  |  Posted on {create_date}')
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
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Updated catergories.txt')
        
    async def info_output(self):
        list_date = datetime.datetime.today()
        list_date = list_date.strftime("%b %d %Y %H:%M:%S %Z")
        list_del_time = datetime.datetime.today() + timedelta(seconds=wait_time)
        list_del_time = list_del_time.strftime("%b %d %Y %H:%M:%S %Z")
        log = datetime.datetime.today() 
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Updated info.json')
        
        return list_date, list_del_time
    
    async def create_embed(self, ctx):
        date = datetime.datetime.today()
        date = date.strftime("%b %d %Y")
        channel = await self.bot.fetch_channel(int(output_channel_id))
        async for first_message in channel.history(limit=int(1), oldest_first = True):
            first_list_link = first_message.jump_url
        list_date, list_del_time = await self.info_output()
        info_embed = discord.Embed(title=f'Jump to the highest bookmarked message',description=f'List from {list_date}\nNext refresh on {list_del_time}' ,color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
        info_embed.add_field(name=f'{title}', value=f'{content}')
        user = await self.bot.fetch_user(int(bot_id))
        pfp = user.avatar.url
        info_embed.set_footer(icon_url=(pfp), text=f'From {user}  |  List from {date}')

        return info_embed
    
    async def changelog(self, ctx, channel):
        info_embed = await self.create_embed(ctx)
        await channel.send(embed=info_embed)
        await self.recursion(ctx, channel)

    @commands.command(hidden=True)
    @commands.has_any_role("Moderator", "Administrator")
    async def start(self, ctx, channel):
        channel_id = channel.strip("<#>")
        channel = await self.bot.fetch_channel(int(channel_id))
        await self.create_message(ctx, channel)

        
def setup(bot):
    bot.add_cog(Posting(bot))
