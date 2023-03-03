from cgitb import reset
from msilib import change_sequence
from unittest import result
import discord
import json
from discord.ext import commands
from discord.ext import tasks
from datetime import timedelta
from discord import app_commands
import asyncio
import os
from discord.app_commands import Choice
import srt
import pickle
import datetime
import boto3
import subprocess
import sqlite3
import re

#############################################################

with open("cogs/jsons/settings.json") as json_file:
    data = json.load(json_file)
    guild_id = data["guild_id"]
    allowed_channels = data["allowed_channels"]

#############################################################


class MyView(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 900, data, beginning_index: int, end_index: int, request):
        super().__init__(timeout=timeout)
        self.data: list = data
        self.beginning_index: int = beginning_index
        self.ending_index: int = end_index
        self.request = request
    
    
    async def edit_embed(self, data, request, beginning_index, ending_index):
        myembed = discord.Embed(title=f'{len(data)} results for {request}')
        for result in data[beginning_index:ending_index]:
            myembed.add_field(name=f'{result[0]}: {result[1]}',value=f'{result[2]}', inline=False)
        if len(data) >= 2:
            myembed.set_footer(text="... not all results displayed but you can pick any index.\n" 
                                    "Pick an index to retrieve a scene next.")
        else:
            myembed.set_footer(text="Pick an index to retrieve a scene next.")
        return myembed
        
        
    @discord.ui.button(label='≪', style=discord.ButtonStyle.grey, row=1)
    async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index -= 10
        self.ending_index -= 10
        if self.beginning_index >= len(self.data):
            self.beginning_index = 0
            self.ending_index = 10
        myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
        
        
    @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple, row=1)
    async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index -= 5
        self.ending_index -= 5
        myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
    
    
    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple, row=1)
    async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index += 5
        self.ending_index += 5
        myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)        
        
        
    @discord.ui.button(label='≫', style=discord.ButtonStyle.grey, row=1)
    async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.beginning_index += 10
        self.ending_index += 10
        if self.beginning_index >= len(self.data):
            self.beginning_index -= 10
            self.ending_index -= 10
        myembed = await self.edit_embed(self.data, self.request, self.beginning_index, self.ending_index)
        await interaction.response.edit_message(embed=myembed)
        
        
    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red, row=1)
    async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        
class MediaCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded expressions finder.")
    
    async def vinnies_db(self, file):
        con = sqlite3.connect('vinnies.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM vndb WHERE filename='{file}'")
        vn = cur.fetchall()
        con.close()
        for (vn_series, link, image) in vn:
            return vn_series, link, image
        
    @app_commands.command(name="request", description="Searches for Japanese sentence examples in VN/LN/ANIME.")
    @app_commands.choices(media = [Choice(name="All media", value="All media")])
    async def request(self, interaction: discord.Interaction, media: str, expression: str):
        if not interaction.channel.id == 1020815784353730660:
            return
        await interaction.response.send_message(f'Searching for {expression} in {media}:')
        results = []
        foundindex = 0
        b = 0   
        if media == "All media":
            files = [file for file in os.listdir("data/") if file.endswith(".txt")]
            for file in files:
                script = open(fr"data/{file}", "r", encoding="utf-8")
                prev_sentences = []
                for count, text in enumerate(script):
                    if b == 1:
                        prev_sentences.append((count, text))
                        count = count - 1
                        ctx_sentence = prev_sentences[count][1]
                        index = len(results) - 1
                        results[index] = results[index] + (ctx_sentence,)
                        b = 0
                    if japanese_input in text:
                        if len(prev_sentences) == 0:
                            foundindex += 1
                            result = (foundindex, file, text)
                            results.append(result)
                            b = 1
                        elif len(prev_sentences) == 1:
                            foundindex += 1
                            count = count - 1
                            ctx_sentence = prev_sentences[count][1]
                            print(prev_sentences[count])
                            result = (foundindex, file, text, ctx_sentence)
                            results.append(result)
                            b = 1
                        elif len(prev_sentences) > 1:
                            foundindex += 1
                            count = count - 1
                            ctx_sentence = prev_sentences[count][1]
                            count = count - 1
                            ctx_sentence2 = prev_sentences[count][1]
                            result = (foundindex, file, text, ctx_sentence, ctx_sentence2)
                            results.append(result)
                            b = 1
                    else:
                        prev_sentences.append((count, text))
                        continue         
                count = 0
            
        if len(results) == 0:
            await interaction.channel.send("No results.")
            return

        myembed = discord.Embed(title=f"{len(results)} results for {expression}")
        for result in results[0:5]:
            myembed.add_field(name=f'{result[0]}: {result[1]}',value=f'{result[2]}', inline=False)
        if len(results) >= 5:
            myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
                                    "Pick an index to retrieve a scene next.")
        else:
            myembed.set_footer(text="Pick an index to retrieve a scene next.")
            
        beginning_index = 0
        end_index = 5
        
        options = []
        for result in results[0:5]:
            item = discord.SelectOption(label=f'{result[0]}')
            options.append(item)
            
        select = Select(min_values = 1, max_values = 1, options=options)   
        async def my_callback(interaction):
            relevant_result = select.view.data[(int(select.values[0])-1) + int(select.view.beginning_index)]      
            if media == "All media":
                file = str(relevant_result[1])
                vn_series, link, image = await self.vinnies_db(file)
                resultembed = discord.Embed(title=f"Result for {expression} in {vn_series.upper()}",description=f'{link}')
                resultembed.set_author(icon_url=interaction.user.avatar.url, name=interaction.user)
                resultembed.set_thumbnail(url=image)
                if len(relevant_result) == 3:
                    resultembed.add_field(name="Text:", value=f'||{relevant_result[3]}||{relevant_result[2]}||{relevant_result[4]}||', inline=False)
                    await interaction.channel.send(embed=resultembed)
                elif len(relevant_result) >= 4:
                    try:
                        resultembed.add_field(name="Text:", value=f'||{relevant_result[4]}{relevant_result[3]}||{relevant_result[2]}||{relevant_result[5]}||', inline=False)
                        await interaction.channel.send(embed=resultembed)
                    except Exception:
                        resultembed.add_field(name="Text:", value=f'||{relevant_result[4]}{relevant_result[3]}||{relevant_result[2]}', inline=False)   
                        await interaction.channel.send(embed=resultembed)
                elif len(relevant_result) == 2:
                    resultembed.add_field(name="Text:", value=f'{relevant_result[2]}||{relevant_result[3]}||', inline=False)
                    await interaction.channel.send(embed=resultembed)

        select.callback = my_callback
        view = MyView(data=results, beginning_index=beginning_index, end_index=end_index, request=expression)
        
        view.add_item(select)
        await interaction.followup.send(embed=myembed, view=view)
                
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MediaCog(bot))
