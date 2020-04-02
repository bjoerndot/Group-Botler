from functools import wraps
import shelve, datetime
from telegram import ParseMode


# import general helper-tools
import dtutil

# import telegram-specific helper-tools
import ptbutil.ptbuser as ptbu
import ptbutil.ptbhelper as ptbh

import group_botler_constants as c
import group_botler_messages as msg

import group_botler_triggers as triggers

from user import User

def is_user_registered(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        id = update.effective_chat.id
        if not group_existent(id):
            register_new_user(update, context.bot)
        else:
            with shelve.open(c.SHELVE_MAIN) as db:
                user = db[str(id)]
                user = update_user(update, user)
                db[str(id)] = user
        func(update, context, *args, **kwargs)
    return wrapped

def update_user(update, user):
    u = update.effective_chat
    user.first_name = u.first_name
    user.last_name = u.last_name
    user.group_name = u.title
    user.name_handle = u.username
    user.last_updated = datetime.datetime.utcnow()
    return user

def existent_on_triggers(chat_id):
    with shelve.open(c.SHELVE_TRIGGERS) as db:
        flag_triggers = str(chat_id) in list(db.keys())
    return flag_triggers

def group_existent(chat_id):
    with shelve.open(c.SHELVE_MAIN) as db:
        flag = str(chat_id) in list(db.keys())

    return flag

def register_new_user(update, bot):
    """Creates a new User-Object and stores it in a shelve
    Also creates new user in triggers
    params: update:Update"""
    user = create_new_user(update)
    bot.send_message(c.ADMINISTRATION_CHANNEL, msg.S_NEW_REGISTRATION.format(str(user)), parse_mode = ParseMode.HTML)    
    triggers.register_user_in_triggers(update.message.chat.id)
    with shelve.open(c.SHELVE_MAIN) as db:
        data = db
        data.update({str(update.message.chat.id): user})
        db = data
    return

def create_new_user(update):
    user = User(
        update.message.chat.id, 
        update.message.chat.type, 
        ptbu.getFirstName(update), 
        ptbu.getLastName(update), 
        ptbu.get_group_title(update),
        ptbu.getUsername(update, True),
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow())
    return user