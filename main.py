#To setup this bot on your server for testing purposes following these steps
# 1. Download the libraries from requirements.txt
# 2. Change the roles in @commands.has_any_role("Moderator", "Administrator", "世界そのもののボット") to fit your server
# 3. Confirm that the user id in the on_message function is the one from the bot
# 4. If you dont want to search for bookmarked messages change the 🔖 emoji
# 5. Change the contents of the channel description in line 608

import discord
import os
import pytz
import regex as re
import asyncio
import datetime
import time
from discord.ext import commands
from datetime import date, tzinfo
from datetime import datetime
from datetime import timedelta
import datetime
import sqlite3

start_time = time.time()
intents = discord.Intents.all()
client = commands.Bot(command_prefix="t.", intents=intents)
client.remove_command('help')

output_channel = None
fetch_channel = None
target_amount = None
target_range = None
output_channel_name = None
fetch_channel_name = None
post_hour = None
post_minute = None
delete_hour = None
delete_minute = None
id = None
time_to_run = None
start_date = None
start_date_formatted = None
delete_Limit = None
next_start_time = None
split_message2 = None
deltime = None
look_back_days = None
info_desc = None
embed_allowed = "Yes"

@client.group()
async def help(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("```" + "\n" +
                       "Commands:" + "\n" +
                       "  t.find" + "             Displays a sorted list of bookmarks" + "\n" +
                       "  t.quick_setup" + "      Sets up the bot in one command" + "\n" +
                       "  t.fetch_channel" + "    Changes the channel where messages are fetched from" + "\n" +
                       "  t.output_channel" + "   Changes the output channel for the list" + "\n" +
                       "  t.history_limit" + "    Sets the amount of message to check for bookmarks" + "\n" +
                       "  t.amount" + "           Changes the minimum reaction amount" + "\n" +
                       "  t.post_time" + "        Changes post time of command" "\n" +
                       "  t.help" + "             Displays this message" + "\n" + "\n" +
                       "Type t.help <command> for more info on a command." + "```")


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def find(ctx):
    await ctx.send("```" + "\n" +
                   "Current find command: t.find " + "🔖 " + str(target_amount) + " " + str(target_range) + "\n" + "\n" +
                   "$find <emoji> <amount> [historyLimit]" + "\n" +
                   "\n" +
                   "Finds all messages that were reacted to with the emoji with atleast the amount of reactions in the range of messages" + "\n" +
                   "\n" +
                   "Example: Posting $find 🔖 5 2500 will find all messages that have 5 and more reactions of 🔖 in the last 2500 messages and give them out." +
                   "```")

@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def allowing_embeds(ctx, arg):
    global embed_allowed
    embed_allowed = arg
    delete_msg = await ctx.send(f"Information embed: {arg}")
    await asyncio.sleep(2)
    await delete_msg.delete()

@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def quick_setup(ctx, reaction_amount, range_limit, list_channel, search_channel, hours, minutes, delete, new_message_hl):

    global target_amount
    global target_range
    global output_channel
    global fetch_channel
    global post_hour
    global post_minute
    global deltime
    global look_back_days

    target_amount = reaction_amount
    target_range = range_limit
    output_channel = list_channel.strip("<#>")
    fetch_channel = search_channel.strip("<#>")
    post_hour = int(hours)
    post_minute = int(minutes)
    deltime = int(delete)
    look_back_days = int(new_message_hl)


    output_channel_name = client.get_channel(int(output_channel))
    fetch_channel_name = client.get_channel(int(fetch_channel))

    channel = client.get_channel(int(ctx.channel.id))

    msg_1 = await channel.send("Are you sure you want to preceed with these settings?" + "\n" + "```" + "\n" +
                               "Reaction amount:     >= " + str(target_amount) + "\n" +
                               "Messages to check:   " + str(target_range) + "\n" +
                               "Output channel:      #" + str(output_channel_name) + "\n" +
                               "Fetch channel:       #" + str(fetch_channel_name) + "\n" +
                               "Posting time:        " + str(hours) + ":" + str(minutes) + "\n" +
                               "Time interval:       " + str(deltime) + "hours" + "\n" + 
                               "Marking new msgs:    " + str(new_message_hl) + " days old" +"```" + "\n" +
                               "Yes/no")

    infotime = datetime.datetime.today()
    infotime_string = infotime.strftime("%Y/%m/%d %H:%M:%S")
    await ctx.message.author.send(str(infotime_string) + "\n" + "```" + "\n" +
                                  "Reaction amount:     >= " + str(target_amount) + "\n" +
                                  "Messages to check:   " + str(target_range) + "\n" +
                                  "Output channel:      #" + str(output_channel_name) + "\n" +
                                  "Fetch channel:       #" + str(fetch_channel_name) + "\n" +
                                  "Posting time:        " + str(hours) + ":" + str(minutes) + "\n" + 
                                  "Marking new msgs:    " + str(new_message_hl) + " days old" + "```")

    def user_check(m):
        return m.author == ctx.author and m.channel == channel

    msg = await client.wait_for("message", check=user_check, timeout=60)
    allowed = ["Yes", "y", "yes", "YES", "Y"]
    if msg.content in allowed:
        msg_2 = await channel.send("Settings have been saved. Starting fetch in 3...")
        await asyncio.sleep(1)

        await msg_2.delete()
        await asyncio.sleep(1)
        await msg.delete()
        await asyncio.sleep(1)
        await msg_1.delete()
        await asyncio.sleep(1)
        await ctx.message.delete()

        await asyncio.sleep(1)
        await find_post_time()
    else:
        msg_3 = await channel.send("Cancelled quick setup.")
        await asyncio.sleep(1)

        await msg_3.delete()
        await asyncio.sleep(1)
        await msg.delete()
        await asyncio.sleep(1)
        await msg_1.delete()
        await asyncio.sleep(1)

        await ctx.message.delete()


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def quick_setup(ctx):
    await ctx.send("```" + "\n" +
                   "t.quick_setup <amount> <history_limit> " + "<#output-text-channel> " + "<#fetch-text-channel> " + "<post-time-hour> " + "<post-time-minute> " + "\n" +
                   "\n" +
                   "Sets up the bot in one command. Allows for a quick list output." + "\n" +
                   "\n" +
                   "Example: $quick_setup 1 1000 #bookmarks #一般  20 20 20 21" +
                   "```")


@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def fetch_channel(ctx, arg):
    all_text_channels = []
    for server in client.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                id = channel.id
                all_text_channels.append(id)
    text_channels = (['<#{0}>'.format(i) for i in all_text_channels])
    try:
        if any(arg in s for s in text_channels):
            await ctx.send(f"Successfully set the target channel to {arg}.")
            global fetch_channel_name
            name2 = channel.name
            fetch_channel_name = name2
            global fetch_channel
            fetch_channel = arg.strip("<#>")
        else:
            await ctx.send("That channel does not exist.")
    except:
        exit


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def fetch_channel(ctx):
    await ctx.send("```" + "\n" +
                   "Current fetch channel: " + str(fetch_channel_name) + "\n" +
                   "\n" +
                   "t.fetch_channel <#text-channel>" + "\n" +
                   "\n" +
                   "Changes the fetch channel where the bookmarked messages are searched for." +
                   "```")


@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def output_channel(ctx, arg):
    all_text_channels = []
    for server in client.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                id = channel.id
                all_text_channels.append(id)
    text_channels = (['<#{0}>'.format(i) for i in all_text_channels])
    try:
        if any(arg in s for s in text_channels):
            await ctx.send(f"Successfully set the target channel to {arg}.")
            global output_channel_name
            name = channel.name
            output_channel_name = name
            global output_channel
            output_channel = arg.strip("<#>")
        else:
            await ctx.send("That channel does not exist.")
    except:
        exit


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def output_channel(ctx):
    await ctx.send("```" + "\n" +
                   "Current output channel: " + str(output_channel_name) + "\n" +
                   "\n" +
                   "t.channel <#text-channel>" + "\n" +
                   "\n" +
                   "Changes the output channel for the list." +
                   "```")


@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def amount(ctx, arg):
    try:
        global target_amount
        if int(arg) <= 0:
            await ctx.send("Please choose a number higher than 0.")
            return
        else:
            target_amount = int(arg)
            await ctx.send(f"Successfully set the minimum reaction amount to {target_amount}.")
    except ValueError:
        await ctx.send("Please chose a number.")


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def amount(ctx):
    await ctx.send("```" + "\n" +
                   "Current target channel: " + str(target_amount) + "\n" +
                   "\n" +
                   "t.amount <number>" + "\n" +
                   "\n" +
                   "Changes the minium amount of reactions a message should have to be added to the list." +
                   "```")


@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def deltime(ctx, arg):
    try:
        global deltime
        if int(arg) <= 0 or int(arg) > 59:
            await ctx.send("Please choose an appropriate minutes value.")
            return
        else:
            deltime = int(arg)
            await ctx.send(f"Successfully set the delete time to {deltime} minutes.")
    except ValueError:
        await ctx.send("Please chose a number.")


@help.command()
async def deltime(ctx):
    await ctx.send("```" + "\n" +
                   "Current delete time: " + str(deltime) + "\n" +
                   "\n" +
                   "t.deltime <number>" + "\n" +
                   "\n" +
                   "Changes the intval between the fetches." +
                   "```")

@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def description(ctx, arg):
    global info_desc
    info_desc = arg
    delete_msg = await ctx.send(f'Info embed description: {info_desc}')
    await asyncio.sleep(2)
    await delete_msg.delete()

@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def history_limit(ctx, arg3):
    try:
        global target_range
        if int(arg3) <= 0:
            await ctx.send("Please choose a number higher than 0.")
            return
        else:
            target_range = int(arg3)
            await ctx.send(f"Successfully set the amount of messages that are checked for a bookmark reaction to {target_range}.")
    except ValueError:
        await ctx.send("Please chose a number.")


@help.command()
async def history_limit(ctx):
    await ctx.send("```" + "\n" +
                   "Current history limit: " + str(target_range) + "\n" +
                   "\n" +
                   "t.history_limit <number>" + "\n" +
                   "\n" +
                   "Changes the amount of messages that are check for a bookmark reaction." +
                   "```")


@client.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def post_time(ctx, arg1, arg2):
    try:
        global post_hour
        global post_minute
        if int(arg1) and int(arg2) < 0:
            await ctx.send("Please choose a time higher than 0.")
            return
        if int(arg1) > 24 or int(arg2) > 59:
            await ctx.send("Please choose a time within 24 hours.")
        else:
            post_hour = int(arg1)
            post_minute = int(arg2)
            await ctx.send(f"Successfully set post time {post_hour}:{post_minute}.")
            await find_post_time()
    except ValueError:
        await ctx.send("Please chose a time.")


@help.command()
@commands.has_any_role("Moderator", "Administrator", "世界そのもののボット")
async def post_time(ctx):
    await ctx.send("```" + "\n" +
                   "Current post time: " + str(post_hour) + ":" + str(post_minute) + "\n" +
                   "\n" +
                   "t.post_time <number> <number>" + "\n" +
                   "\n" +
                   "Changes the post time of the command find." +
                   "```")


async def find_post_time():
    global start_date_formatted
    global start_date
    global time_to_run
    now = datetime.datetime.today()
    start_date_formatted = now
    time_to_run = start_date_formatted.replace(hour=post_hour, minute=post_minute)
    print(f"This is time to run {time_to_run}")

    wait_time = (time_to_run - start_date_formatted).total_seconds()
    print(f"This is wait time {wait_time}")

    await asyncio.sleep(wait_time)

    channel = client.get_channel(int(output_channel))
    await channel.send(f't.find 🔖 {target_amount} {target_range}')


async def automation():
    await asyncio.sleep(15)
    channel = client.get_channel(int(output_channel))
    await channel.send(f't.find 🔖 {target_amount} {target_range}')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="すべてのメセージを見れる 👁️👁️"))
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # Allowing only the bot to start the list output
    if message.author.id == 997928130327085096:
        if message.content.startswith(f't.find'):
                await message.delete()
                preparing_msg = await message.channel.send("Preparing new list...")
                start_time = time.time()
                num = 0
                msgSplit = message.content.split(" ")
                historyLimit = int(msgSplit[3]) if len(msgSplit) == 4 else 10
                list = []

                # con = sqlite3.connect('bookmark-list.db')
                # cur = con.cursor()
                # today_date = datetime.datetime.today()
                # today_date_string = "'" + \
                #     today_date.strftime("%Y/%m/%d %H:%M:%S") + "'"
                # table_query = '''CREATE TABLE {}(reaction_amount int, author text, content text, link text, message_date text, filenames text, image_link text)'''.format(
                #     today_date_string)
                # cur.execute(table_query)
                # con.commit()
                # con.close()

                # Fetching messages and looking for bookmark reactions
                channel = client.get_channel(int(fetch_channel))
                async for historical_message in channel.history(limit=historyLimit):
                    for reaction in historical_message.reactions:
                        if reaction.emoji == msgSplit[1]:
                            num = reaction.count
                            if num >= int(msgSplit[2]):

                                # Remove user pings
                                maxChar = 275
                                split_message = historical_message.content.split()
                                user_id_list = []
                                for e in split_message:
                                    if e.startswith("<@"):
                                        user_id_raw = re.findall("\<\@(.*?)\>", e)
                                        user_id = str(user_id_raw).strip("['']")
                                        user_id_new = re.sub('\D', '', user_id)
                                        user_id_list.append(user_id_new)

                                user_name_list = []
                                for r in user_id_list:
                                    user_name = await client.fetch_user(r)
                                    user_name_list.append(str(user_name))

                                for i in range(len(split_message)):
                                    if split_message[i].startswith("<@"):
                                        split_message[i] = user_name_list[0]
                                        del user_name_list[0]

                                # Remove links/embeds
                                # embed_list = []
                                # for p in split_message:
                                #     if p.startswith("https:"):
                                #         link_raw = re.sub(
                                #             "(https?:\/\/)?([\w\-])+\.{1}([a-zA-Z]{2,63})([\/\w-]*)*\/?\??([^#\n\r]*)?#?([^\n\r]*)", '', p)
                                #         #link_raw = re.sub("^https?:\/\/(.*)", '', p)
                                #         # embed_link_edited = str(link_raw).strip("['']")
                                #         # embed_link = "<" + embed_link_edited + ">"
                                #         embed_list.append(str(link_raw))

                                # for o in range(len(split_message)):
                                #     if split_message[o].startswith("https:"):
                                #         split_message[o] = embed_list[0]
                                #         del embed_list[0]

                                historical_message.content = " ".join(str(g) for g in split_message)
                                # if historical_message.author == "Deleted User#0000":
                                #     print(historical_message.author, type(historical_message.author))
                                #     historical_message.author = "Deleted User"
                                # The [{}] regex
                                
                                if "[{" in historical_message.content and "}]" in historical_message.content:
                                    description = re.findall('\[\{(.*?)\}\]', historical_message.content)[0]
                                    text = str(description).strip("['']")
                                    list.append((num, historical_message.author, + "\n" + text, historical_message.jump_url, historical_message.created_at, historical_message.attachments))
                                elif len(historical_message.content) > maxChar:
                                    list.append((num, historical_message.author, "\n" + historical_message.content[:maxChar] + "\n", historical_message.jump_url, historical_message.created_at, historical_message.attachments))
                                elif len(historical_message.content) == 0 and historical_message.attachments:
                                    for naming in historical_message.attachments:
                                        historical_message.content = naming.filename     
                                    list.append((num, historical_message.author, "\n" + historical_message.content, historical_message.jump_url, historical_message.created_at, historical_message.attachments))
                                else:
                                    list.append((num, historical_message.author, "\n" + historical_message.content, historical_message.jump_url, historical_message.created_at, historical_message.attachments))
                                
                                # con = sqlite3.connect('bookmark-list.db')
                                # cur = con.cursor()
                                # insert_query = f"INSERT INTO {today_date_string} (reaction_amount, author, content, link, message_date, filenames, image_link) VALUES (?,?,?,?,?)"
                                # value_query = (int(num), str(historical_message.author), str(historical_message.content), str(historical_message.jump_url), str(historical_message.created_at), str(itsfilename), str(itsimageurl))
                                # cur.execute(insert_query, value_query)
                                # con.commit()
                                # con.close()

                def sort_tup_first_ele(list):
                    return(sorted(list, key=lambda g: g[0], reverse=True))

                sortedList = sort_tup_first_ele(list)
                delete_Limit = len(sortedList)+5
                list_items = len(sortedList)
                channel = client.get_channel(int(message.channel.id))
                count = 1
                utc=pytz.UTC
                global look_back_days
                startw0 = datetime.datetime.today()
                endw1 = startw0 - timedelta(look_back_days)
                await preparing_msg.delete()
                await asyncio.sleep(2)
                con = sqlite3.connect('words.db')
                cur = con.cursor()
                cur.execute(f"SELECT * FROM 'resource_sharing' ORDER BY freqs DESC")
                words = cur.fetchall()

                # List output
                for (reaction_count, raw_username, message_content, message_link, message_date, message_attachments) in sortedList:
                    #if message_date < utc.localize(startw0) and message_date > utc.localize(endw1):
                    if utc.localize(message_date) < utc.localize(startw0) and utc.localize(message_date) > utc.localize(endw1):
                        message_date = message_date.strftime("%Y/%m/%d %H:%M:%S %Z%z")
    
                        if raw_username.name == "Deleted User":
                            raw_username = "Deleted User"
                            if message_attachments == []:
                                b = 0
                                displayed_keywords = []
                                for keywords in words:
                                    if b >= 3:
                                        break
                                    if keywords[0] in message_content:
                                        keyword = keywords[0]
                                        displayed_keywords.append(keyword)
                                        b += 1
                                embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                await message.channel.send(embed=embed)
                            elif message_attachments != []:
                                a = 0
                                for image in message_attachments:
                                    if a >= 1: break
                                    if image.content_type == "image/png" or "image/jpg" or "image/jpeg":
                                        image_url = image.url
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        a += 1
                                    else:
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                            count += 1
                        else:
                            user = await client.fetch_user(int(raw_username.id))
                            pfp = user.avatar_url
                            if message_attachments == []:
                                b = 0
                                displayed_keywords = []
                                for keywords in words:
                                    if b >= 3:
                                        break
                                    if keywords[0] in message_content:
                                        keyword = keywords[0]
                                        displayed_keywords.append(keyword)
                                        b += 1
                                if len(displayed_keywords) == 3:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                                elif len(displayed_keywords) == 2:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                                elif len(displayed_keywords) == 1:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                            elif message_attachments != []:
                                a = 0
                                for image in message_attachments:
                                    if a >= 1: break
                                    if image.content_type == "image/png" or "image/jpg" or "image/jpeg":
                                        image_url = image.url
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                                    else:
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})', color=discord.Color.from_rgb(255, 0, 0)) 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                            count += 1
                    #not red marking
                    else:
                        message_date = message_date.strftime("%Y/%m/%d %H:%M:%S %Z%z")
                        if raw_username.name == "Deleted User":
                            raw_username = "Deleted User"
                            if message_attachments == []:
                                b = 0
                                displayed_keywords = []
                                for keywords in words:
                                    if b >= 3:
                                        break
                                    if keywords[0] in message_content:
                                        keyword = keywords[0]
                                        displayed_keywords.append(keyword)
                                        b += 1
                                embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                await message.channel.send(embed=embed)
                            elif message_attachments != []:
                                a = 0
                                for image in message_attachments:
                                    if a >= 1: break
                                    if image.content_type == "image/png" or "image/jpg" or "image/jpeg":
                                        image_url = image.url
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            embed.set_thumbnail(url=image_url)
                                            await message.channel.send(embed=embed)
                                        a += 1
                                    else:
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                            count += 1
                        else:
                            user = await client.fetch_user(int(raw_username.id))
                            pfp = user.avatar_url
                            if message_attachments == []:
                                b = 0
                                displayed_keywords = []
                                for keywords in words:
                                    if b >= 3:
                                        break
                                    if keywords[0] in message_content:
                                        keyword = keywords[0]
                                        displayed_keywords.append(keyword)
                                        b += 1
                                if len(displayed_keywords) == 3:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})') 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                                elif len(displayed_keywords) == 2:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})') 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                                elif len(displayed_keywords) == 1:
                                    embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                    embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                    await message.channel.send(embed=embed)
                            elif message_attachments != []:
                                a = 0
                                for image in message_attachments:
                                    if a >= 1: break
                                    if image.content_type == "image/png" or "image/jpg" or "image/jpeg":
                                        image_url = image.url
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_thumbnail(url=image_url)
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                                    else:
                                        b = 0
                                        displayed_keywords = []
                                        for keywords in words:
                                            if b >= 3:
                                                break
                                            if keywords[0] in message_content:
                                                keyword = keywords[0]
                                                displayed_keywords.append(keyword)
                                                b += 1
                                        if len(displayed_keywords) == 3:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]} | {displayed_keywords[2]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 2:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]} | {displayed_keywords[1]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        elif len(displayed_keywords) == 1:
                                            embed = discord.Embed(title=f'__**{count}#**__     {reaction_count} {msgSplit[1]}       {displayed_keywords[0]}',description=f'{message_content} \n [Link]({message_link})') 
                                            embed.set_footer(icon_url=(pfp), text=f'From {raw_username}  |  Posted at {message_date}')
                                            await message.channel.send(embed=embed)
                                        a += 1
                            count += 1

                con.commit()
                con.close()
                
                channel = client.get_channel(int(message.channel.id))
                # Link to highest bookmarked message
                async for first_message in channel.history(oldest_first=True, limit=1):
                    first_list_link = first_message.jump_url

                fetch_channel_link = "<#" + fetch_channel + ">"
                today = datetime.datetime.today()
                global deltime
                # Change timedelta to change the wait time for the next list
                now = datetime.datetime.today()
                then = datetime.datetime.today() + timedelta(hours=deltime)
                wait_time = (then - now).total_seconds()

                waittime = datetime.datetime.today()
                waittime_string = waittime.strftime("%Y/%m/%d %H:%M:%S")

                global embed_allowed
                if embed_allowed == "Yes":
                    global info_desc
                    if info_desc == None:
                        embed = discord.Embed(title=f'Jump to the highest bookmarked message', color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
                        embed.add_field(name=f'Changelog', value=f'- Red coloring on embed indicates that the message is not older than a week \n - Attachment filename and image is now displayed \n - Post date of message was added')
                        user = message.author
                        pfp = user.avatar
                        embed.set_footer(icon_url=(pfp), text=f'From {message.author}  |  List from {waittime_string}')
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f'Jump to the highest bookmarked message', color=discord.Color.from_rgb(255, 255, 255), url=first_list_link)
                        embed.add_field(name=f'Changelog', value=f'{info_desc}')
                        user = message.author
                        pfp = user.avatar
                        embed.set_footer(icon_url=(pfp), text=f'From {message.author}  |  List from {waittime_string}')
                        await message.channel.send(embed=embed)

                # consol output for me
                print(str(waittime_string) + ": Waiting for list deletion " +
                    str(wait_time) + " seconds")
                print("Output time:" + " %s seconds " %
                    round((time.time() - start_time), 2))

                #db_thread = "<#" + str(1008685718131986493) + ">"

                await channel.edit(topic="Jump to the highest bookmarked message " + first_list_link + "\n" +
                                "\n" +
                                "**About**" + "\n" +
                                "List from " + str(waittime_string) + " (UTC)" + "\n" +
                                "Next refresh in " + str(deltime) + "hours" + "\n" +
                                "Scraped from " + fetch_channel_link + "\n" +
                                "Output time:" + " %s seconds " % round((time.time() - start_time), 2) + "\n" +
                                "List length: " + str(list_items) + "\n" +
                                "For more info see https://timm-1.gitbook.io/bookmarklistbot/" + "\n" +
                                #    "DB files in " + db_thread + "\n" +
                                "https://github.com/Timm04/timmbookmarkbot")

                # threads = message.channel.threads
                # for thread in threads:
                #     await thread.send(str(waittime_string), file=discord.File(r'bookmark-list.db'))

                # Waiting till new list is posted
                await asyncio.sleep(wait_time)
                # Deleting list
                await channel.purge(limit=delete_Limit)
                print("Waiting for t.find message")

                # Post the command for the list output
                await automation()
    await client.process_commands(message)

client.run(os.getenv('TOKEN'))
