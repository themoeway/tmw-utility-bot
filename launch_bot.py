import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
ouken = commands.Bot(command_prefix='kt$', intents=intents)

# @bot.check
# def check_guild(ctx):
#     try:
#         return ctx.guild.id == 947813835715256390
#     except AttributeError:
#         return True

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        ouken.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loaded the following cog: {filename}")
        
with open("token_new.txt") as token_file:
    bot_token = token_file.read()

ouken.run(bot_token)
