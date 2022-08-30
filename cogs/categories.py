import discord
from discord.ext import commands
import sqlite3
import datetime
from datetime import timedelta
import pytz
import re
import json

with open("cogs/jsons/settings.json") as json_file:
    data_dict = json.load(json_file)
    amount = data_dict["amount"]
    history_limit = data_dict["history_limit"]
    output_channel_id = data_dict["bookmark-list"]
    fetch_channel_id = data_dict["resource-sharing"]
    max_char = data_dict["max_char"]
    guild_id = data_dict["guild_id"]
    look_back_days = data_dict["look_back_days"] # 7 days
    
class Category(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
    
    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def categories(self, ctx):
        """
        Lists available keywords to search for
        """
        await ctx.send(file=discord.File(r'catergories.txt'))
        
    async def create_message(self, keyword):
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
            if keyword in keywords:
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
    
    @commands.command()          
    async def category(self, ctx, keyword):
        """
        Outputs a list with the specified keyword
        """
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT discord_user_id, keywords FROM bookmarked_messages")
        embed_messages = cur.fetchall()
        catagories = []
        for id, keywords in embed_messages:
            if keywords != "[]":
                keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                catagories.append(keywords)   
        for match in catagories:
            if keyword == match:
                return await self.create_message(keyword)
        
        
def setup(bot):
    bot.add_cog(Category(bot))
        # con = sqlite3.connect('bookmark-list.db')
        # cur = con.cursor()
        # cur.execute(f"SELECT * FROM '2022/08/22 01:52:16' ORDER BY reaction_amount DESC")
        # embed_messages = cur.fetchall()

        # prep_list = []
        # catergorization = []
        # for (reaction_amount, username, message_content, message_link, message_date, attachments, keywords) in embed_messages:
        #     if keywords != "[]":
        #         keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
        #         prep_list.append(keywords)
        # for i in prep_list:
        #     for j in i.split():
        #         catergorization.append(j)
        # freq = Counter(catergorization)
        # counters = {str(k): v for k, v in freq.items()}
        # sorted_freq = {k: v for k, v in sorted(counters.items(), key=lambda item: item[1], reverse=True)}

        # f = open("catergories.txt", "w", encoding="utf-8")
        # for r in range(len(sorted_freq)):
        #     for word, frequency in sorted_freq.items():
        #         f.write(f"{word}: {frequency} \n")
        # con.close()
        # await ctx.send(file=discord.File(r'catergories.txt.db'))