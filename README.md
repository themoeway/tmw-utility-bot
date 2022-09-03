# timmbookmarkbot
A discord bot that posts a sorted list of bookmarked messages. 

## How does the bot work
Every six hours, the bot outputs the whole db (bookmarked-messsage.db) in the specified channel.
You can add messages to this db by either filling it up once with the kt$fill_db command. You can do this for multiple channel so the first list output will contain more messages.
Another way messages get into that db is achieved with the on_reaction_add event, that first checks if the messages, that was reacted to, was a bookmark reaction. If yes it looks at its reaction count and if that equals or goes above 10 it will go over to the next step, which is checking if the message is new or old. 
If the message is already in the db, then the db entry is updated with the new reaction count, message content and displayed keywords.
If the message doesn't exist in the db, then its added to it.

### How to change the parameters
All settings are in the json filles. Editing these will change the way the bot adds or updates messages in the db. 
The most important settings are amount, which is the minimum amount of reactions a message should have to get into the db, the emoji to check for, which is currently the bookmark reaction and the wait_time which represents the time you have to wait till the next list is posted.

#### Example
kt$start channel
This will output the list in the channel named channel
After the list is outputed it will wait wait_time, before deleting the list and reposting it again.
kt$fill_db channel
This will get every message that meets the specified criteria and adds it to the db.
kt$filter message_id
This is for filtering purposes to avoid double message.
