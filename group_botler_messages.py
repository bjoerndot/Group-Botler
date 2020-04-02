# Start the bot
START = """What a pleasure!
\nMay I introduce myself? I am <b>Group-Botler</b> 🤵. My goal is to be to your service.
Let me give you a little taste of my services: 
🗳 I can organize votings for you, 
⏰ send reminders and 
💬 set triggers - they are fun 😉
📄 create lists - shopping, To Do... you name it!
\nCall /help for an overview!

⚠️⚠️⚠️ IMPORTANT NOTICE: 2020-03-30
I am very sorry. Some data was lost on a recent error. Unfortunately it is gone forever. I am truly sorry 🙇🏽‍♂️🙇🏽‍♂️🙇🏽‍♂️. A backup module is setup and will - from now on - back up the data once a week. 
Unfortunately this means, that you have to re-set your triggers manually.
⚠️⚠️⚠️"""

# Settings

# Generic Answers
NOT_IMPLEMENTED = "This hasn't been implemented yet."

# Help
H_START = """
Mylords, myladies.
\nHow may I help you today? My goal is to help you out, where I can!
🗳 I can organize votings for you, 
⏰ send reminders and 
💬 set triggers - they are fun 😉
📄 create lists - shopping, To Do... you name it!
\nBelow you can find a couple of buttons. Click them to find out how you can interact with me.
\nIn your service - 🤵🤵🤵

⚠️⚠️⚠️ IMPORTANT NOTICE: 2020-03-30
I am very sorry. Some data was lost on a recent error. Unfortunately it is gone forever. I am truly sorry 🙇🏽‍♂️🙇🏽‍♂️🙇🏽‍♂️. A backup module is setup and will - from now on - back up the data once a week. 
In order to re-register for triggers, please call /start
Unfortunately this means, that you have to re-set your triggers manually.
⚠️⚠️⚠️
"""
H_VOTE = """🗳<b>VOTE</b>
\nCall non anonymus /vote with at least three arguments: 
1️⃣Question, 
2️⃣answer-option 1, 
3️⃣answer-option 2, e.g.:
<code>/vote Shall we debate on that?, Yes, No</code>
\n Arguments must be separated by commas."""

H_REMINDER_HEADER = "⏰<b>REMINDERS</b>"

H_ADD_REMINDER =f"""{H_REMINDER_HEADER} (1)
There are two types of reminders: One-time reminders or repeating reminders. Both can be called with /add_reminder - usually they should be called as an answer to a message, that you want to be reminded off.
\nONE-TIME REMINDERS
Pass the following arguments to /add_reminder: 
1️⃣ name of the reminder,
2️⃣ time to execution (as seconds <code>120</code>, <code>hh:mm</code> <b>OR</b> as <code>hh:mmUTC</code>), e.g.
<code>/add_reminder eggs 270\n/add_reminder eggs 00:05\n/add_reminder eggs 13:46UTC</code>
\nREPEATING REMINDERS
Pass the following arguments to /add_reminder:
1️⃣ name,
2️⃣ interval (as <code>daily</code>, <code>hourly</code> <b>OR</b> number followed by unit (e.g. 8h, 30s, 45m)),
3️⃣ time of first execution (as hh:mmUTC), e.g.:
<code>/add_reminder pet_dogs 8h 07:00UTC\n/add_reminder wakeup daily 19:34UTC</code>"""

H_EXISTING_REMINDERS = f"""{H_REMINDER_HEADER} (2)
\nOf course, sometimes you want to cancel a reminder or see all reminders you set. Here are a few more commands on reminders:
\nDELETE A REMINDER (/del_reminder):
Pass the following arguments to /del_reminder:
1️⃣ name, e.g.:
<code>/del_reminder eggs</code>
\nSHOW ALL REMINDERS (/list_reminders or /reminders):
Call /list_reminders or /reminders and you'll get a short list of reminders. If you want more information on your reminders call /list_reminders_long or /reminders_long
\nSHOW A REMINDER (/show_reminder):
Sometimes you don't remember anymore, what it was, that you wanted to be reminded off. In these cases you can call /show_reminder:
Simply pass the following argument to /show_reminder:
1️⃣ name, e.g.:
<code>/show_reminder eggs</code>"""

H_TRIGGERS = """💬<b>TRIGGERS</b>
\nTriggers are messages, images, GIFs, sound-files or just any type of content that can be sent through Telegram. This content can be called with a certain word or phrase.
Maybe you are using a certain GIF very often and don't want to search through @gif all the time? Make it a trigger!
ADD TRIGGERS (/add_trigger):
To add a trigger reply to the content you want to be triggered with /add_trigger and pass the following argument:
1️⃣ trigger-name, e.g.:
<code>/add_trigger funny</code>
\nCALL A TRIGGER:
If you want to trigger that content just type the trigger-name
\nDELETE TRIGGERS (/del_trigger):
To get rid of a trigger you can just call /del_trigger with the following argument:
1️⃣ trigger-name, e.g.:
<code>/del_trigger funny</code>
\nSHOW ALL TRIGGERS (/list_triggers or /triggers):
If you want to get an overview of all triggers, call /list_triggers or /triggers - this overview tells you the trigger-name, how often the trigger was used the last time it was used."""

H_LISTS = """📄<b>LISTS</b>
For shopping or for To Do's... for not forgetting things you wanted to bring your grandma... you literally name what your list shall be for!
Lists are an assembly of options which either can be 'undone' or '<s>done</s>'.
CREATE A LIST (/add_list):
To create a new list you need to call /add_list and pass it the following arguments:
1️⃣ list name,
2️⃣ (optionally) list items (separated by new lines), e.g.:
<code>/add_list My awesome list
dull item 1
dull item 2</code>

ADD ITEMS TO THE LIST (/add_listitem_X):
To add items to your list simply call /add_listitem_X (with X being the id of your list) and pass it the following arguments:
1️⃣ list items (separated by new lines), e.g.:
<code>/add_listitem_1 fun item 1
fun item 2</code>

CROSS ITEM OFF (/del_X_Y)
The easiest way to cross an item off is to click the command right after your item. This command is called with /del_X_Y with X being the id of your list and Y the id of your item.

DELETE LIST (/del_list)
You can also delete a list, if you call /del_list with the following argument:
1️⃣ list name, e.g.
<code>/del_list My awesome list</code>
"""

H_ABOUT = """<b>ABOUT</b>
This bot was written and is maintained by @oliverschw.
If you want to send /feedback or have a /question, send a message with /feedback or /question with the following arguments:
1️⃣ Your question or your feedback, e.g.:
<code>/question Can you add anonnymus voting?</code>
<code>/feedback Your bot is working fine. Thanks.</code>
"""

H_ALR_DIS = "This help-section is already displayed."

# Vote-Feature
VOTE_NO_ARGS = "It seems as if you didn't give any arguments. Please provide at least three arguments: 1️⃣ The Question in debate, 2️⃣ answer-option A, 3️⃣ answer-option B."
VOTE_NOT_ENOUGH_ARGS = "Make sure to provide a question and at least two options as answers."
VOTE_NO_ADMIN = "I can do my services best, if you give me admin-rights!"
VOTE_NOTIFY = ["Your vote has been recorded for: {}"]
VOTE_NO_CHANGE = "You have already voted for this."

# Reminders
### CRUD on jobs
R_ADD_JOB_SUCCESS = "Reminder <code>{}</code> successfully scheduled."
R_DEL_JOB_SUCCESS = "Reminder <code>{}</code> was deleted."
R_REMINDER_LIST = "<b>The following reminders are scheduled for {}</b>: \n\n{}"
R_NO_REMINDERS = "Currently no reminders are scheduled for {}."
R_NO_REPLY = "It is recommended to use this command as a reply to another message, which you want to be reminded of."
### Error-Messages
R_ERROR_404 = "This reminder was not found."
R_ERROR_JOB_EXISTS = "This reminder already exists. Please choose a new name."
R_ERROR_BATTLE_PREP_OLD = "This message is older than 24h, so the effect has already worn off."
R_ERROR_ARGS_REPEATING = "Not enough arguments. The command must look like: \n<code>/add_reminder name interval hh:mmUTC</code>"
R_ERROR_ARGS_REMINDER = "Please provide two arguments: job-name & time until execution (either as seconds or as hh:mm).\n\n<code>/add_reminder name 60</code>"
R_ERROR_ARG_REMINDER_TIME = "Please provide either the time in seconds as number (e.g 60) or as hh:mm or as absolute value hh:mmUTC\n/add_reminder name 60\n/add_reminder name 01:20\n/add_reminder name 13:25UTC"
R_ERROR_ARG_BAD_TIME = "For absolute reminders, <b>hours may range between 0 and 23 and minutes between 0 and 59</b>. Please check your reminder."

# Triggers
TRIGGER_ADD_SUCCESS = "Trigger <code>{}</code> was set. Enjoy!"
TRIGGER_DEL_SUCCESS = "Trigger <code>{}</code> was deleted."
TRIGGER_DEL_FAIL = "Trigger <code>{}</code> couldn't be deleted. Please check spelling."
TRIGGER_EMPTY = "You don't have any triggers set yet. Use /add_trigger <code>trigger_text</code> to add a trigger. See more at /help!"
TRIGGER_NO_REPLY = "You didn't use this command as a reply. Please reply to another message. Otherwise I won't know for sure, which content I shall trigger on that phrase.\n\nRefer to /help if anything is unclear!"
TRIGGER_NO_ARGS = "I don't know, which phrase I should use, to store this trigger... please call this command with arguments.\n<code>/add_trigger phrase to trigger</code>\n\nRefer to /help for more info."

TRIGGER_ERROR_NOT_REGISTERED = "Unfortunately I was not able to add your trigger. It seems as if you are newly looking for my service.\n\nIf you haven't done yet, please call /start."

# Servcie-Messages
S_FIRST_USE = "<b>First use detected:</b>\n\n\nChat (ID): <code>{}</code>\nChat (name): <b>{}</b>\nType: {}"
S_PING = "How can I help you?"
S_NEW_REGISTRATION = """<b>New user!</b> 🎊🎊🎊

{}"""
S_NEW_QUESTION_FEEDBACK = """<b>New {}</b>

From: {}
Message: <code>{}</code>
Markup: #{}

/answer_{}_{}
"""
S_MESSAGE_SUCCESS = "Message successfully transmitted."

# Lists
LIST_NO_ARGS = "To write a list you need to provide at least the lists title.\nE.g. <code>/add_list Shopping List</code>"
LIST_ID_UNKNOWN = "This list doesn't seem to exist. Run {} to see all your lists."
ITEM_ID_UNKNOWN = "This item seems to be not existing. Please doublecheck on your list!"
ITEM_COMPLETED_ERROR = "This item is already been crossed of your list. Well done!"
NOT_ADMIN = "<b>If you grant me admin privileges (allow me to pin and to delete messages) I can do a better and more silent service for you!</b>"
NO_DELETE_RIGHTS = "<b>If you allow me to delete message I can do a more silent service for you!</b>"
NO_PIN_RIGHTS = "<b>If you allow mw to pin message I can offer a far better service!</b>"
ADD_ITEM_NO_ARGS = "To add more items to your list, you must pass them onto the list.\nE.g. <code>/add_listitem_X item on list</code>"
ITEMS_ADDED_W_LINK = "Your items were added to the list. Check here: <a href='https://t.me/c/{}/{}'>{}</a>"
ITEMS_ADDED = "Your items were added to the list."
ALL_SET_COMPLETED = "On behalf of {} all items were set to completed. Congratulations! :)"
LIST_EMPTY = "You don't have any lists yet!"
ADD_ITEM_LIST_TOO_LONG = "This item can't be added as your list would become too long. Please start a new list!"
NEW_LIST_TOO_LONG = "This list can't be created as your list would be too long. Please separate some items onto another list."
LIST_DELETED = "The list {} has been deleted."