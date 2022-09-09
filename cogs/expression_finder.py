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

class MediaCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.s3_client = boto3.client('s3')
        self.subtitle_data = list()
        
    @app_commands.command(name="create_sub_data", description="Creates anime subtitle data.")    
    @app_commands.checks.has_role("Moderator") 
    async def create_sub_data(self, interaction: discord.Interaction):  
        subtitle_files = [subtitle for subtitle in os.listdir('data/subs/') if subtitle.endswith('.srt')]
        for counter, subtitle_name in enumerate(subtitle_files):
            with open(fr'data/subs/{subtitle_name}', encoding='utf-8') as subtitle_file:
                subtitle_text = subtitle_file.read()
                try:
                    subtitle_generator = srt.parse(subtitle_text)
                    search_pairs = [(subtitle.index, subtitle.content) for subtitle in subtitle_generator]
                except srt.SRTParseError:
                    print(f"Subtitle excluded due to error: {subtitle_name}")
                    continue
                self.subtitle_data.append((f'{subtitle_name}', search_pairs))
                print(f"Loaded {counter + 1} out of {len(subtitle_files)} subtitles. ({round(counter/ len(subtitle_files), 4) * 100}%)")

        with open("data/subs/subs_data", "wb") as subsdata:
            pickle.dump(self.subtitle_data, subsdata)

        await interaction.channel.send("Done.")
        
#     async def get_sub_timings(self, subtitle_name, subtitle_index):
#         with open(fr'data/subs/{subtitle_name}', encoding='utf-8') as subtitle_file:
#             subtitle_text = subtitle_file.read()
#             subtitle_generator = srt.parse(subtitle_text)
#             all_subtitles = list(subtitle_generator)
#             indexes_to_extract = list(range(subtitle_index-2, subtitle_index+3))
#             subtitle_lines = [subtitle for subtitle in all_subtitles if subtitle.index in indexes_to_extract]
#             content = " 　".join([subtitle.content for subtitle in subtitle_lines])
#             if len(subtitle_lines) >= 5:
#                 beginning_time = subtitle_lines[1].start
#             else:
#                 beginning_time = subtitle_lines[0].start - datetime.timedelta(seconds=5)
#             end_time = subtitle_lines[-1].end + datetime.timedelta(seconds=4)
#             return content, beginning_time, end_time

#     async def edit_results_post(self, results, results_msg, beginning_index, end_index, japanese_input):
#         myembed = discord.Embed(title=f"{len(results)} results for {japanese_input}")
#         for result in results[beginning_index:end_index]:
#             myembed.add_field(name=f"{result[0]} in {result[1]}", value=f"{result[2]}", inline=False)
#         if len(results) >= 5:
#             myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
#                                     "Pick an index to retrieve a scene next.")
#         else:
#             myembed.set_footer(text="Pick an index to retrieve a scene next.")

#         await results_msg.edit(embed=myembed)

#     async def get_nearest_key_frame_time(self, filename, beginning_time):
#         path = "data/video/"
#         print(filename, beginning_time, path)
#         cmd = f"ffprobe -v error -skip_frame nokey -show_entries frame=pkt_pts_time -select_streams v -of csv=p=0 {path + filename}"
#         print(cmd)
#         key_frames = subprocess.check_output(cmd, shell=True).decode().split()
#         print(key_frames)
#         print("We have the following key frames: ", key_frames)
#         key_frame_times = []
#         for key_frame_seconds in key_frames:
#             print(key_frame_seconds)
#             seconds, microseconds = key_frame_seconds.split(".")
#             time = datetime.timedelta(seconds=float(seconds), microseconds=float(microseconds) - 1)
#             key_frame_times.append(time)
#         print(key_frame_times)
#         last_key_frame_time = [time for time in key_frame_times if beginning_time.total_seconds() - time.total_seconds() > 0][-1]
#         if last_key_frame_time.total_seconds() <= 0:
#             last_key_frame_time = last_key_frame_time.resolution
#         return last_key_frame_time

#     async def fix_times(self, beginning_time, end_time, filename):
#         # Fix beginning time below zero
#         if beginning_time.total_seconds() <= 0:
#             beginning_time = beginning_time.resolution

#         # Fix end time after end
#         video_length_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
#         video_lengths = subprocess.check_output(video_length_cmd, shell=True).decode().split('.')
#         video_length = datetime.timedelta(seconds=float(video_lengths[0]), microseconds=float(video_lengths[1]))
#         if video_length.total_seconds() - end_time.total_seconds() <= 1:
#             end_time = video_length

#         return beginning_time, end_time

#     async def create_video(self, filename, beginning_time, end_time):
#         path = "data/video/"
#         await self.fix_times(beginning_time, end_time, path + filename)
#         # previous_key_frame_time = await self.get_nearest_key_frame_time(filename, beginning_time)
#         previous_key_frame_time = beginning_time
#         start = "0" + str(previous_key_frame_time)[0:14]
#         print(start)
#         end_time = end_time - previous_key_frame_time
#         print(end_time)
#         end = "0" + str(end_time)[0:7]
#         # cmd = f"ffmpeg -avoid_negative_ts 1 -i {path + filename} -ss {start} -to {end} -c copy {path}result_{filename[:-3] + 'mp4'}"
#         cmd = f"ffmpeg -ss {start} -i {path + filename} -to {end} -c copy -avoid_negative_ts make_zero {path}result_{filename[:-3] + 'mp4'}"
#         os.system(cmd)

    @commands.Cog.listener()
    async def on_ready(self):
        with open("data/subs/subs_data", "rb") as subsdata:
            self.subtitle_data = pickle.load(subsdata)

        print(f"Loaded subtitle data with {len(self.subtitle_data)} files.")

    async def download_file(self, filename):
        return (f"data/video/{filename}")
        #self.s3_client.download_file("djtvideoarchive", f"{filename}", f"data/video/{filename}")
    
    async def vinnies_db(self, file):
        con = sqlite3.connect('vinnies.db')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM vndb WHERE filename='{file}'")
        vn = cur.fetchall()
        con.close()
        for (vn_series, link, image) in vn:
            return vn_series, link, image
        
    # async def get_nss_files(self, sentence):
    #     file_list = []  
    #     nss_files = [nss for nss in os.listdir("muramasa/nss/") if nss.endswith(".nss")]
    #     for counter, nss_name in enumerate(nss_files):
    #         nss_file = open(fr"muramasa/nss/{nss_name}", "rb")
    #         for count, line in enumerate(nss_file):
    #             file_list.append((count, line))  
    #         nss = []
    #         for count, script in file_list:
    #             script = script.decode('shift_jisx0213')
    #             nss.append((count, script)) 
    #         src_path = await self.regex_nss_files(nss, sentence)
    #         if src_path != None:
    #             return src_path
                
    # async def regex_nss_files(self, nss, sentence):
    #     for count, script in nss:   
    #         # kanjis = re.findall(">[^>]*<\/R", script)
    #         kanjis = re.findall("(?<=\>).+?(?=\<)", script)
    #         if kanjis != []:
    #             kanji = "〈" + kanjis[0] + "〉"
    #             furiganas = re.findall('(?<=\=\")([ぁ-んァ-ン])+?(?=\"\>)', script)
    #             if furiganas != []:
    #                 furigana = furiganas[0]
    #                 furigana = "《" + furigana + "》"
                    
    #                 pair = kanji + furigana
                    
    #                 script = "".join(script.splitlines())
    #                 #How do i also catch more occurances of the kanji regex, cause this only fixes the first occurance
    #                 first_match = re.findall("<RUBY text=.*?</RUBY>", script)[0]
    #                 parts = script.split(first_match)
    #                 script = f'{parts[0]}{pair}{first_match.join(parts[1:])}'
    #                 y = list(nss[count])
    #                 y[1] = "".join(script.splitlines())
    #                 x = tuple(y)
    #                 changed_nss = [x if e[0] == x[0] else e for e in nss]  
    #                 src_path = await self.find_audio(changed_nss, sentence)
    #                 if src_path != None:
    #                     return src_path
                
    # async def find_audio(self, changed_nss, sentence):
    #     possible_src_paths = []
    #     for count, script in changed_nss:
    #         try:
    #             if sentence[:15] in script:
    #                 count = count - 1
    #                 possible_src_paths.append((changed_nss[count]))
    #                 count = count - 1
    #                 possible_src_paths.append((changed_nss[count]))
    #                 count = count - 1
    #                 possible_src_paths.append((changed_nss[count]))
    #                 break 
    #         except Exception:
    #             return
    #     if possible_src_paths != []:
    #         src_path = await self.get_voice_path(possible_src_paths)
    #         return src_path
        
    # async def get_voice_path(self, possible_src_paths):
    #     b = 0
    #     for count, path in possible_src_paths:
    #         if b == 3:
    #             print("no voice file")
    #             break
    #         if re.findall('src="(.*?)">', path):
    #             src_path = re.findall('src="(.*?)">', path)
    #             return src_path
    #         else:
    #             b += 1
                
    @app_commands.command(name="request", description="Searches for Japanese sentence examples in VN/LN/ANIME.")
    @app_commands.choices(media = [Choice(name="Visual Novels", value="Visual Novels"), Choice(name="Light Novels", value="Light Novels"), Choice(name="Anime", value="Anime")])
    async def request(self, interaction: discord.Interaction, media: str, japanese_input: str):
        if interaction.channel_id != allowed_channels:
            await interaction.response.send_message(f'Please use this command in <#{allowed_channels}>' , ephemeral=True)
            return

        await interaction.response.send_message(f'Searching for {japanese_input} in {media}:')
        results = []
        foundindex = 0
        if media == "Visual Novels":
            vn_files = [vn for vn in os.listdir("data/vns/") if vn.endswith(".txt")]
            for counter, vn_name in enumerate(vn_files):
                vn_file = open(fr"data/vns/{vn_name}", "r", encoding="utf-8")
                prev_sentences = []
                for count, content in enumerate(vn_file):
                    if japanese_input not in content:
                        prev_sentences.append((count, content))
                        continue
                    
                    foundindex += 1
                    count = count - 1
                    prev_sentence = "".join([x for x in prev_sentences[count][1]])
                    count = count - 1
                    prev_sentence2 = "".join([x for x in prev_sentences[count][1]])
                    results.append((foundindex, vn_name, content, prev_sentence, prev_sentence2))                 

        elif media == "Light Novels":
            await interaction.response.send_message("This option is not available yet.", ephemeral=True)
        
        elif media == "Anime":
            await interaction.response.send_message("This option is not available yet.", ephemeral=True)
            # for filename, subdata in self.subtitle_data:
            #     for srtindex, content in subdata:
            #         if japanese_input not in content:
            #             continue

            #         foundindex += 1
            #         result = (foundindex, filename, content, srtindex)
            #         results.append(result)
            
        if len(results) == 0:
            await interaction.channel.send("No results.")
            return

        myembed = discord.Embed(title=f"{len(results)} results for {japanese_input}")
        for result in results[0:5]:
            myembed.add_field(name=f"{result[0]} in {result[1]}", value=f"{result[2]}", inline=False)
        if len(results) >= 5:
            myembed.set_footer(text="... not all results displayed but you can pick any index.\n"
                                    "Pick an index to retrieve a scene next.")
        else:
            myembed.set_footer(text="Pick an index to retrieve a scene next.")
            
        results_message = await interaction.channel.send(embed=myembed)
        await results_message.add_reaction('1️⃣')
        await results_message.add_reaction('2️⃣')
        await results_message.add_reaction('3️⃣')
        await results_message.add_reaction('4️⃣')
        await results_message.add_reaction('5️⃣')
        await results_message.add_reaction('⬅️')
        await results_message.add_reaction('➡️')
        #await results_message.add_reaction('❌')

        def reaction_check(reaction, user):
            allowed_emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '⬅️', '➡️']
            return user.id == interaction.user.id and str(reaction.emoji) in allowed_emoji and reaction.message.id == results_message.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=25.0, check=reaction_check)
            await reaction.remove(user)
            beginning_index = 0
            end_index = 5
            reaction_string = str(reaction.emoji)
            while reaction_string == "⬅️" or reaction_string == "➡️":
                if reaction_string == "⬅️":
                    beginning_index -= 5
                    end_index -= 5
                    if beginning_index < 0:
                        beginning_index = 0
                        end_index = 5
                    await self.edit_results_post(results, results_message, beginning_index, end_index, japanese_input)
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=reaction_check)
                    await reaction.remove(user)
                    reaction_string = str(reaction.emoji)

                elif reaction_string == "➡️":
                    beginning_index += 5
                    end_index += 5
                    if beginning_index >= len(results):
                        beginning_index -= 5
                        end_index -= 5
                    await self.edit_results_post(results, results_message, beginning_index, end_index, japanese_input)
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=reaction_check)
                    await reaction.remove(user)
                    reaction_string = str(reaction.emoji)

                else:
                    await interaction.channel.send("Unexpected error. Exiting...")

        except asyncio.TimeoutError:
            await interaction.channel.send("Function timed out. Exiting...")
            return

        if str(reaction.emoji) == "1️⃣":
            result_index = beginning_index
        elif str(reaction.emoji) == "2️⃣":
            result_index = beginning_index + 1
        elif str(reaction.emoji) == "3️⃣":
            result_index = beginning_index + 2
        elif str(reaction.emoji) == "4️⃣":
            result_index = beginning_index + 3
        elif str(reaction.emoji) == "5️⃣":
            result_index = beginning_index + 4
        elif str(reaction.emoji) == '❌':
            await interaction.channel.send("Exiting...")
            return
        else:
            await interaction.channel.send("Exiting...")
            return

        try:
            relevant_result = results[result_index] # (1, 'aete mushisuru.txt', '\u3000――本日の気温、三十六度。\n')
        except IndexError:
            await interaction.channel.send("Invalid index. Exiting...")
            return

        if media == "Anime:":
            await interaction.channel.send("Creating video file...")

            content, beginning_time, end_time = await self.get_sub_timings(relevant_result[1], relevant_result[3])

            video_file_name = f"{relevant_result[1][:-3]}mp4"

            from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
            ffmpeg_extract_subclip(fr"{video_file_name}", beginning_time, end_time, targetname="test/test.mp4")
            # await self.download_file(video_file_name)
            await self.create_video(video_file_name, beginning_time, end_time)

            stripped_content = content.replace('\n', '　 ')

            video_file = discord.File(f"data/video/result_{video_file_name[:-3] + 'mp4'}")
            await interaction.channel.send(embed=resultembed, file=video_file)
            
        elif media == "Visual Novels":
            file = relevant_result[1]
            vn_series, link, image = await self.vinnies_db(file)
            resultembed = discord.Embed(title=f"Result {result_index + 1} for {japanese_input} in {vn_series[:-4].upper()}",description=f'{link}')
            resultembed.add_field(name="Text:", value=f'||{relevant_result[4]}{relevant_result[3]}||{relevant_result[2]}', inline=False)
            resultembed.set_thumbnail(url=image)
            # if file == "muramasa.txt":
            #     sentence = relevant_result[2]
            #     sentence = sentence[1:]
            #     src_path = await self.get_nss_files(sentence)
            #     print(src_path)
            #     if src_path != None:
            #         audio_file = discord.File(fr"muramasa/{src_path[0] + '.ogg.'}")
            #         await interaction.channel.send(embed=resultembed, file=audio_file)
            #     else:
            #         await interaction.channel.send(embed=resultembed)
            # else:
            #     await interaction.channel.send(embed=resultembed)
            await interaction.channel.send(embed=resultembed)

        #await asyncio.sleep(1)

        # for file in os.listdir('data/video/'):
        #     if not file == "placerholder":
        #         os.remove(f'data/video/{file}')
                
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MediaCog(bot), guilds=[discord.Object(id=guild_id)])
