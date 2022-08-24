import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.check
def check_guild(ctx):
    try:
        return ctx.guild.id == 947813835715256390
    except AttributeError:
        return True

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded the following cog: {filename}")
        

with open("token_new.txt") as token_file:
    bot_token = token_file.read()

async def main():
    async with bot:
        await load_extensions()
        await bot.start(bot_token)

asyncio.run(main())