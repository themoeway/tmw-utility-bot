import sqlite3

con = sqlite3.connect('bookmarked-messages.db')
cur = con.cursor()
cur.execute("SELECT discord_user_id, message_id FROM bookmarked_messages")
database = cur.fetchall()
message_ids = []
for row in database:
    message_ids.append(row[1])
if 1012094725408423936 in message_ids:
    print("yes")
else:
    print("no")