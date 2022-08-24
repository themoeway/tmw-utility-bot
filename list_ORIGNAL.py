import discord
from discord.ext import commands
import sqlite3

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

    async def new_or_old_message(self, reaction_message):
        print("checking wheter message has one or none bookmarks")
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        database = cur.fetchall()
        
        for message_id in database:
            if message_id[2] != reaction_message.id:
                return

        con.commit()
        con.close()

    async def update_db(self, reaction_message):
        print("updating reaction count and message content")
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM bookmarked_message WHERE message_id=?", (int(reaction_message.id)))
        that_reaction_message = cur.fetchone()

        if that_reaction_message[1] != reaction_message.reaction.count:
            cur.execute("UPDATE bookmarked_message SET bookmarks=? and content=? WHERE message_id=?", (int(reaction_message.reaction.count), str(reaction_message.content) ,int(reaction_message.id)))
        
        con.commit()
        con.close()

    async def count_reactions(self, reaction_message):
        print("counting reactions")
        for reaction in reaction_message.reactions:
            if reaction.emoji == '🔖':
                if reaction.count >= amount:
                    return reaction.count

    async def keyword_assignment(self, reaction_message):
        print("keywords assignment")
        con = sqlite3.connect("words.db")
        cur = con.cursor()
        words = cur.fetchall()
        b = 0
        displayed_keywords = []
        for keywords in words:
            if b >= 3:
                break
            if keywords[0] in reaction_message.content:
                keyword = keywords[0]
                displayed_keywords.append(keyword)
                b += 1
        con.commit()
        con.close()
        
        return displayed_keywords

    async def adding_to_db(self, reaction_message):
        print("adding to db")
        displayed_keywords = await self.keyword_assignment(reaction_message)
        con = sqlite3.connect('bookmarked-messages.db')
        cur = con.cursor()
        print("adding to db")
        insert_query = f'INSERT INTO bookmarked_messages (discord_user_id, bookmarks, message_id, content, link, created_at, attachments, keywords) VALUES (?,?,?,?,?,?,?)'
        value_query = (int(reaction_message.author.id), int(reaction_message.reaction.count) , int(reaction_message.id) , int(reaction_message.reaction.count), str(reaction_message.content), str(reaction_message.jump_url), str(reaction_message.attachments[0].url), str(displayed_keywords))
        cur.execute(insert_query, value_query)
        con.commit()
        con.close()
        
        print("added")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.Reaction):
        if reaction.message.guild.id == guild_id and reaction.message.channel.id != self.log_channel:
            print("True")
            enough_reactions = await self.count_reactions(reaction.message)
            if enough_reactions:
                new_bookmarked_message = await self.new_or_old_message(reaction.message)
                if new_bookmarked_message:
                    await self.adding_to_db(reaction.message)
                else:
                    await self.update_db(reaction.message)

async def setup(bot):
    await bot.add_cog(List(bot))