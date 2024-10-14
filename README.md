# TheMoeWay Utility Bot

📢 **New contributors [welcome](contribute.md)!**

## What is the Utility Bot?
The Utility Bot enhances the user experience on TheMoeWay Discord server by providing users with quality of life features.

Powerful features that it provides:
- 📝 Curates a list of the 100 most bookmarked messages in the server and allows specific lists to be made that contain certain keywords.
- 🗣️ Gives example sentences of a specified word in various types of Japanese Novels to help users learn how different words are used in context.
- 🧵 Closes discord threads when users get their question answered.
- 👩‍🏫 Works with the Gatekeeper Bot of TheMoeWay by allowing moderators to reset users quiz attempts.
- 🔖 Keeps track of the most bookmarked messages in the server allowing users to quickly get a view of the best resources.
- 🧎 Keeps track of the most kneeled to users in the server in form of a leaderboard.
- 🔝 Displays a rank distribution of the user base's ranks.
- 🐌 Sets slowmode in Discord text channels.
- 📔 Delets finished books from users by interacting with the TheMoeWay Book Club Bot.

## Usage Guide

By typing '/' into any discord chat, you will open up the discord slash command menu which will show you all the bots the server has. Now by clicking on the Utility Bot in that menu, you will be presented with all the commands you can use to help you.

`/fill_db [channel]`

Fills the databaase with the messages of the specified channel that have a bookmark reaction.

`/keywords_list [keyword]`

Creates a list of the most bookmarked messages on the server that contain the specified keywords. For more detail check out the [Gitbook](https://timm-1.gitbook.io/bookmarklistbot).

`/request [japanese_expression]`

Searches for Japanese sentence examples in Japanese Novels where the specified expression appears in.

`/solved`

Closes Discord forum threads.

`/reset [quiz_rank] [user]`

Resets users quiz attempts by interacting with the databse of the TheMoeWay Gatekeeper Bot.

`/kneelderboard`

Presents you with a leaderboard of the users who have been kneeled to the most.

`/ranktable`

Shows you the rank distribution of the rank roles in the user base.

`/slowmode [amount]`

Sets a Discord text channel to slow mode.

`/delete_finished`

Deletes finished books from users by interacting with the database of the TheMoeWay Book Club Bot.

## Installation

Before you can install and run the bot, make sure you have the following:
1. Python 3.9.0
   You can download Python from [here](https://www.python.org/downloads/release/python-390/).
2. Discord Developer Account
   You need a Discord account and a registered bot in the Discord Developer Portal.
3. Git (to clone this  repository)
   Download Git from [here](https://git-scm.com/).
4. A text editor
   You can use any text editor (e.g., VC code, Sublime Text, Atom).

## Steps to Install
### 1. Clone the Repository
First, clone the bot repository to your local machine.
```
git clone https://github.com/themoeway/tmw-utility-bot.git
cd tmw-utility-bot
```
### 2. Create a Virtual Environment (Optional but Recommended)
It is recommended to create a virtual environment to manage dependencies cleanly.
```
python -m venv venv
source venv/bin/activate   # For Linux/MacOS
# or
venv\Scripts\activate      # For Windows
```
### 3. Install Dependencies
Use pip to install the required dependencies specified in the requirements.txt file.
```
pip install -r requirements.txt
```
### 4. Create a Discord Bot Application
  1. Go to the Discord Developer Portal and log in.
  2. Click New Application and give it a name.
  3. In the Bot section, create a new bot and copy its Token.
  4. Tick `Presence Intent`, `Server Members Intent` and `Message Content Intent`.
  5. Under OAuth2 > URL Generator, enable `bot` and `applications.commands` scopes. Assign administrator permissions and copy the link and add the bot to your server.
  6. Paste the token at the bottom of the `launch_bot.py` file.
### 6. Run the Bot
To start the bot, run the following command:
```
python launch_bot.py
```
### 7. Change the Constant Values.
Change the settings in the ``cogs/jsons/settings.json``. The bookmark-list is the channel id of where the bookmarks are going to be posted.

## Contributing

🚀 **Dip your toes into contributing by looking at issues with the label [good first issue](https://github.com/themoeway/tmw-utility-bot/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).**

Since this is a distributed effort, we **highly welcome new contributors**! Feel free to browse the [issue tracker](https://github.com/themoeway/tmw-utility-bot/issues), and read our [contributing guidelines](contribute.md).

If you're looking to code, please let us know what you plan on working on before submitting a Pull Request. This gives the core maintainers an opportunity to provide feedback early on before you dive too deep. You can do this by opening a Github Issue with the proposal.
