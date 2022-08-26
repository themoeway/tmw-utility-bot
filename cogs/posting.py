from itertools import count
import discord
from discord.ext import commands
import sqlite3
import datetime
from datetime import timedelta
import pytz
import asyncio
import json

#############################################################

with open("cogs/channel_ids.json") as json_file:
    data_dict = json.load(json_file)
    look_back_days = data_dict["look_back_days"] # 7 days
    wait_time = data_dict["wait_time"] # 6hrs

#############################################################


class Posting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
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
        channel = self.log_channel
        utc = pytz.UTC
        startw0 = datetime.datetime.today()
        endw1 = startw0 - timedelta(look_back_days)

        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(
            f"SELECT * FROM bookmarked_messages ORDER BY bookmarks DESC")
        info = cur.fetchall()

        count = 0
        for (user_id, message_id, reaction_amount, content, link, create_date, attachments, keywords) in info:
            message = await channel.fetch_message(message_id)
            if message.created_at < utc.localize(startw0) and message.created_at > utc.localize(endw1):
                red_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}',
                                          description=f'{content} \n [Link]({link})', color=discord.Color.from_rgb(255, 0, 0))
                user = await self.bot.fetch_user(int(user_id))
                pfp = user.avatar.url
                red_embed.set_footer(
                    icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                    red_embed.set_thumbnail(url=attachments)
                await channel.send(embed=red_embed)
            else:
                my_embed = discord.Embed(
                    title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})')
                user = await self.bot.fetch_user(int(user_id))
                pfp = user.avatar.url
                my_embed.set_footer(
                    icon_url=(pfp), text=f'From {user.name}  |  Posted at {create_date}')
                if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                    my_embed.set_thumbnail(url=attachments)
                await channel.send(embed=my_embed)

        await self.changelog(ctx)

    async def create_embed(self, ctx):
        date = datetime.datetime.today()
        date = date.strftime("%Y/%m/%d %H:%M:%S")
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(
            f"SELECT bookmarks, link FROM bookmarked_messages ORDER BY bookmarks ASC LIMIT 1")
        first_list_link = cur.fetchone()[1]
        info_embed = discord.Embed(title=f'Jump to the highest bookmarked message',
                                   color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
        info_embed.add_field(name=f'Changelog', value=f'- Categorization of each list item (700 most occuring words in resource-sharing, DM the bot with "t.words_db" for the DB) \n - Red coloring on embed indicates that the message is not older than a week \n - Attachment filename and image is now displayed \n - Post date of message was added')
        user = ctx.message.author
        pfp = user.avatar.url
        info_embed.set_footer(
            icon_url=(pfp), text=f'From {ctx.message.author}  |  List from {date}')

        return info_embed

    async def changelog(self, ctx):
        info_embed = await self.create_embed(ctx)
        await self.log_channel.send(embed=info_embed)
        await self.recursion(ctx)

    @commands.command()
    async def start(self, ctx):
        await self.create_message(ctx)


async def setup(bot):
    await bot.add_cog(Posting(bot))
