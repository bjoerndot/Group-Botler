# import telegram-specific libraries
from telegram.ext.dispatcher import run_async
from telegram import ParseMode

# import general libraries
import re, datetime, shelve

# import general helper-tools
import dtutil

# import telegram-specific helper-tools
import ptbutil.ptbuser as ptbu
import ptbutil.ptbhelper as ptbh

# import string-matching librariy fuzzywuzzy
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

# import messages and constants
import group_botler_messages as msg
import group_botler_constants as c



# initalizing dictionary for cached access
TRIGGER_KEYS = {}

##
class Trigger:
    def __init__(self, trigger_text, type, content, last_use, num_of_uses):
        self.trigger_text = trigger_text
        self.type = type
        self.content = content
        self.last_use = last_use
        self.num_of_uses = num_of_uses
    
    def __repr__(self):
        return f'TRIGGER(Object) ({self.trigger_text}): Type = {self.type}, content-id = {self.content}, Last use = {dtutil.getDateAndTime(self.last_use)}, # of uses = {str(self.num_of_uses)}'

    def print(self):
        return f"{self.trigger_text} <code>({self.num_of_uses}x, Last: {dtutil.getDate(self.last_use)})</code>"

    def print_short(self):
        return self.trigger_text
    
    def print_long(self):
        return f'<b>{self.trigger_text}</b>:\n<code>{self.type}</code> (content-type),\n<code>{self.content}</code> (content),\n<code>{dtutil.getDate(self.type)}</code> (Last use), \n<code>{self.num_of_uses}x (# of uses)</code>'

def startup_trigger_script():
    """Load triggers into a cached value on startup"""
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        global TRIGGER_KEYS
        for chat in db:
            TRIGGER_KEYS[chat] = db[chat].keys()
    return

def register_user_in_triggers(chat_id):
    """Add new users to the triggers-shelve
    params: chat_id: int/str as key within the shelve"""
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        if str(chat_id) in db:
            return
        db[str(chat_id)] = {}

def write_trigger_to_DB(update, trigger, key, id):
    """Adds trigger to shelve and notifies user - throws an error, if the trigger couldn't be set.
    params: update: Update, trigger: Trigger, key: str, id: int/str"""
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        try:
            data = db[str(id)]
            data.update({key: trigger})
            db[str(id)] = data
            for chat in db:
                TRIGGER_KEYS[chat] = db[chat].keys()
            # notify user after successful storing
            update.message.reply_html(msg.TRIGGER_ADD_SUCCESS.format(key))
        except KeyError:
            if(str(id) not in db):
                update.message.reply_html(msg.TRIGGER_ERROR_NOT_REGISTERED)
    

def del_trigger_from_DB(update, key, id):
    """Deletes trigger from database, if trigger is found
    params: update: Update, key: str, id: int/str"""
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        try:
            data = db[str(id)]
            del data[key]
            db[str(id)] = data
            global TRIGGER_KEYS
            for chat in db:
                TRIGGER_KEYS[chat] = db[chat].keys()
            # notify user, if trigger was successfully delete
            update.message.reply_html(msg.TRIGGER_DEL_SUCCESS.format(key))
        except KeyError:
            # notifiy user, that the trigger couldn't be found
            update.message.reply_html(msg.TRIGGER_DEL_FAIL.format(key))

def fetch_trigger(key, chat_id):
    """Searches for key in the cached dictionary
    Uses fuzzywuzzy to find similar results, updated the Trigger-Instance
    and returns the found trigger."""
    # looking for similiar triggers
    match = process.extract(key, TRIGGER_KEYS[str(chat_id)], processor=None, scorer=fuzz.ratio, limit=1)
    # if match is higher than 90% = pretty strict/conservative
    if match[0][1] > 90:
        # get the matched word
        key = match[0][0]
        # take actual trigger-object from shelve and update it
        with shelve.open(c.SHELVE_TRIGGERS) as db:
            data = db[str(chat_id)]
            trigger = data[key]
            trigger.num_of_uses += 1
            trigger.last_use = datetime.datetime.utcnow()
            data.update({key: trigger})
            db[str(chat_id)] = data
            return trigger
    else:
        # return nothing, if nothing is found.
        return ""

def sort_triggers(triggers):
    """Sorts triggers alphabetically by trigger_text
    params: triggers: List of Trigger-Objects
    returns sorted triggers"""
    return sorted(triggers, key=lambda x: x.trigger_text)

def write_trigger_item(trigger):
    """Calls built-in print function while writing the list.
    params: trigger: Trigger
    returns str from Trigger-Object"""
    return trigger.print()

def send_trigger_list(update, trigger_list, group_name):
    """Sends a couple of messages to the user
    params: update: Update, trigger_list: List of Trigger-Objects, group_name: str
    """
    # if the list is emtpy: return a help-message
    if not trigger_list:
        ptbh.reply(update, msg.TRIGGER_EMPTY)
        return
    # initializing header text here, as group_name needs to be filled but two blanks are required
    header = "<b>Triggers for " + group_name + " - {}-{}</b>\n"
    # getting an array of messages
    messages = ptbh.split_messages(list_to_split=trigger_list, maximum=c.T_NUM_OF_ITEMS_ON_TRIGGER_LIST, header = header, callback = write_trigger_item)
    for m in messages:
        m ="\n".join(m)
        update.message.reply_html(m, quote=False)


def get_trigger_data(id):
    """"Creates a list of Triggers in the shelve
    params: id: str
    returns trigger_list: List of Trigger-Objects"""
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        data = db[id]
    trigger_list = sort_triggers(list(data.values()))
    return trigger_list


def list_triggers(update, context):
    """Creates a list of message that display all saved triggers
    params: update: Update, context: Context"""
    chat_id = str(update.message.chat.id)
    group_name = ptbu.get_group_title(update)
    triggers = get_trigger_data(chat_id)
    send_trigger_list(update, triggers, group_name)

def extract_type_content(message):
    """Unpacks Python-Telegram-Bot-Message-Object into type of content and content id
    params: message: Message
    returns: type: str, content: str"""
    if message.forward_from:
        type='forward'
        content = message.message_id
    elif message.audio:
        type = 'audio'
        content = message.audio.file_id
    elif message.document:
        type = 'document'
        content = message.document.file_id
    elif message.sticker:
        type = 'sticker'
        content = message.sticker.file_id
    elif message.video:
        type = 'video'
        content = message.video.file_id
    elif message.photo:
        type = 'photo'
        ####### QUESTIONABLE ########
        content = message.photo[-1].file_id
    else:
        type = 'text'
        content = message.text_html
    return type, content


def add_trigger(update, context):
    """Is called by /add_trigger args
    Prepares all necessary variables for storage in shelve
    params: update: Update, context: Context (for args)"""
    chat_id = update.message.chat.id
    message = update.message.reply_to_message
    if not message:
        ptbh.reply(update, msg.TRIGGER_NO_REPLY)
        return
    if not context.args:
        ptbh.reply(update, msg.TRIGGER_NO_ARGS)
        return
    trigger_text = normalize_trigger_text_from_array(context.args)
    type, content = extract_type_content(message)
    last_use = datetime.datetime.utcnow()
    num_of_uses = 0
    trigger = Trigger(trigger_text, type, content, last_use, num_of_uses)
    write_trigger_to_DB(update, trigger, trigger_text, chat_id)

def normalize_trigger_text_from_array(args):
    """Takes a list of strings joins them and returns them all lower case.
    params: args: List"""
    trigger_text = " ".join(args)
    trigger_text = trigger_text.lower()
    return trigger_text


def del_trigger(update, context):
    """Is called by /del_trigger args
    Prepares trigger_text and calls for deletion
    params: update:Update, context: Context"""
    trigger_text = normalize_trigger_text_from_array(context.args)
    del_trigger_from_DB(update, trigger_text, update.message.chat.id)

@run_async
def call_trigger(update, context):
    """Is called by every non-command in a chat
    looks, whether a phrase or a word is stored as trigger and retuns that trigger"""
    chat_id = update.message.chat.id
    trigger_text = update.message.text
    trigger_text = trigger_text.lower()
    trigger = fetch_trigger(trigger_text, chat_id)
    # return if nothing is found
    if trigger == "":
        return
    bot = context.bot
    # chose appropriate message-style based on the content type
    if(trigger.type == 'audio'):
        bot.send_audio(chat_id, trigger.content)
    elif(trigger.type == 'document'):
        bot.send_document(chat_id, trigger.content)
    elif(trigger.type == 'sticker'):
        bot.send_sticker(chat_id, trigger.content)
    elif(trigger.type == 'video'):
        bot.send_video(chat_id, trigger.content)
    elif(trigger.type == 'photo'):
        bot.send_photo(chat_id, trigger.content)
    elif(trigger.type == 'forward'):
        bot.forward_message(chat_id, chat_id, trigger.content)
    else:
        bot.send_message(chat_id, trigger.content, parse_mode = ParseMode.HTML)
