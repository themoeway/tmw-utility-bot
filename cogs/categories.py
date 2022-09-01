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
    @commands.cooldown(3, 86400, commands.BucketType.user)
    async def categories(self, ctx):
        """
        Lists available keywords to search for
        """
        await ctx.message.author.send(file=discord.File(r'catergories.txt'))
        
    async def create_message(self, command_user, keyword):
        log = datetime.datetime.today()
        log = log.strftime("%Y/%m/%d %H:%M:%S")
        print(f'{log} Wating for category output')
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
                create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S.%f%z")
                if create_date < utc.localize(startw0) and create_date > utc.localize(endw1):
                    red_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})', color=discord.Color.from_rgb(255, 0, 0))
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                    except Exception:
                        user_name = "Deleted User"
                        red_embed.set_footer(text=f'From {user_name}  |  Posted on {create_date}')
                        if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                            red_embed.set_thumbnail(url=attachments)
                        await command_user.send(embed=red_embed)
                        count += 1
                    else:
                        try:
                            pfp = user.avatar.url
                        except Exception:
                            red_embed.set_footer(text=f'From {user.name}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                red_embed.set_thumbnail(url=attachments)
                            await command_user.send(embed=red_embed)
                            count += 1
                        else:
                            red_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                red_embed.set_thumbnail(url=attachments)
                            await command_user.send(embed=red_embed)
                            count += 1
                else:
                    create_date = create_date.strftime("%b %d %Y")
                    my_embed = discord.Embed(title=f'__**{count}#**__     {reaction_amount} 🔖       {keywords}', description=f'{content} \n [Link]({link})')
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                    except Exception:
                        user_name = "Deleted User"
                        my_embed.set_footer(text=f'From {user.name}  |  Posted on {create_date}')
                        if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                            my_embed.set_thumbnail(url=attachments)
                        await command_user.send(embed=my_embed)
                        count += 1
                    else:
                        try:
                            pfp = user.avatar.url
                        except Exception:
                            my_embed.set_footer(text=f'From {user.name}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                my_embed.set_thumbnail(url=attachments)
                            await command_user.send(embed=my_embed)
                            count += 1
                        else:
                            my_embed.set_footer(icon_url=(pfp), text=f'From {user.name}  |  Posted on {create_date}')
                            if attachments.endswith(".png") or attachments.endswith(".jpg") or attachments.endswith(".jpeg"):
                                my_embed.set_thumbnail(url=attachments)
                            await command_user.send(embed=my_embed)
                            count += 1
            else:
                count += 1
        await command_user.send("Done!!!")
    
    @commands.command()      
    @commands.cooldown(4, 86400, commands.BucketType.user)    
    async def category(self, ctx, keyword):
        """
        Outputs a list with the specified keyword
        """
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute(f"SELECT discord_user_id, keywords FROM bookmarked_messages")
        command_user = await self.bot.fetch_user(ctx.message.author.id)
        embed_messages = cur.fetchall()
        categories = []
        for id, keywords in embed_messages:
            if keywords != "[]":
                keywords = re.sub("\[\'|\'\]|'|  |,", "", keywords)
                categories.append(keywords) 
        for match in categories:
            if keyword in match:
                try:
                    await command_user.send("Preparing list...")
                except Exception:
                    await ctx.send(f'<@{command_user.id}> please change your privacy settings to ``Allow direct messages from server members.``')
                else:
                    return await self.create_message(command_user, keyword)
                break
        else:
            return await command_user.send(f"There is no {keyword} message.")
        
        
def setup(bot):
    bot.add_cog(Category(bot))