import discord
from discord.ext import commands

presence_message = "$help for commands"

class MyHelpCommand(commands.MinimalHelpCommand):

    async def send_pages(self):
        destination = self.get_destination()
        myembed = discord.Embed(color=discord.Color.from_rgb(255, 0, 0), description='')
        for page in self.paginator.pages:
            myembed.description += page
        await destination.send(embed=myembed)

    def add_bot_commands_formatting(self, commands):
        if commands:
            lines = []
            for command in commands:
                commandline = f"`${command.name}` {command.help}"
                lines.append(commandline)

            joined = '\n'.join(lines)
            self.paginator.add_line(joined)

    def get_opening_note(self):
        return "Commands overview:"

    def get_command_signature(self):
        return None

class HelpInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    # Perform on Start-up
    @commands.Cog.listener()
    async def on_ready(self):
        presence_message = "$help for commands."
        await self.bot.change_presence(activity=discord.Game(presence_message))
        print(f"Logged in as\n\tName: {self.bot.user.name}\n\tID: {self.bot.user.id}")
        print(f"Running pycord version: {discord.__version__}")

async def setup(bot):
    await bot.add_cog(HelpInfo(bot))