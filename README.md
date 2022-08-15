# timmbookmarkbot
Discord bot that return a sorted list of bookmarked messages from highest to lowest

@世界そのもののボット#1990 __**Changelog 2022/08/15:**__
- increased the wait time from 55min to 6hrs
- a DB file is posted in "bookmark-list-db" after each time the list is posted
- added gitbook link and "bookmark-list-db" link in the channel description 
- added this github page

<h1> Thing to do to make the bot run</h1>

- Change @commands.has_any_role("Moderator", "Administrator", "世界そのもののボット") to roles that you want to allow to use the command

- Change the id "997928130327085096" in line 393 where "if message.author.id == 997928130327085096:" to the id of your bot

- Change the thread id in line 529 where db_thread = "<#" + str(1008685718131986493) + ">" to match the thread where the db should be posted

- Change the channel description in line 531

- Change the token
