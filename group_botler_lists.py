# import telegram-specific libraries
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, JobQueue
from telegram import ParseMode, CallbackQuery
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html

import ptbutil.errorhandling as ptbe
import ptbutil.ptbhelper as ptbh
import ptbutil.ptbuser as ptbu

import datetime, re, shelve

# messages
import group_botler_messages as msg
import group_botler_constants as c
import group_botler_commands as gbc

from List import List
from Item import Item

# VERSION
# 0.0.1


### Persistent Storage Operations ###
# reminders are stored by their name
def add_list_to_storage(id, user_list):
    """Adds list to user-object in shelve
    params: id: int, user_list: List"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        lists = user.get_lists()
        lists.update({str(user_list.id): user_list})
        user.lists = lists
        db[str(id)] = user

def get_list_from_storage(id, list_id):
    """Retrieves the lists-dictionary from storage
    params: id: int/str, list_id: int/str"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        lists = user.get_lists()
        if(str(list_id) in lists):
            return user.lists[str(list_id)]
        else:
            return False

def get_lists_from_storage(id):
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        lists = user.get_lists()
        return lists

def delete_list_from_storage(id, list_id):
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        lists = user.get_lists()
        del lists[str(list_id)]
        user.lists = lists
        db[str(id)] = user

def add_list(update, context):
    # extract message text
    text = update.message.text[9:].strip()

    # split by newline to get the items - first item is title
    lines = text.split("\n")

    # remove all empty strings
    lines = list(filter(None, lines))

    # throw error, if no arguments are passed
    if(len(lines) == 0):
        ptbh.reply(update, msg.LIST_NO_ARGS)
        return
    
    # set title and other data
    title = lines.pop(0)
    created_at = datetime.datetime.utcnow().isoformat()
    created_by = ptbu.getUsername(update, True)
    chat_id = update.message.chat.id
    lists = get_lists_from_storage(chat_id)
    list_id = len(get_lists_from_storage(chat_id))
    while (str(list_id) in lists):
        list_id += 1

    # create new list
    new_list = List(list_id, title, created_by, created_at, chat_id)

    # check for items on list
    if(len(lines) > 0):
        items = {}
        
        # add items to list
        for index, line in enumerate(lines, 1):
            new_item = Item(index, list_id, line)
            items[index] = new_item
        new_list.add_items(items)

    # check if the list is below the TELEGRAM limit for messages
    text = new_list.show_list()
    
    if(len(text) > c.MESSAGE_MAX_LENGTH*0.8):
        ptbh.reply(update, msg.NEW_LIST_TOO_LONG)
        return

    # send list to user + retrieve the message_Id
    message_object = update.message.reply_html(text, quote=False)    
        
    # finalize new list with last data
    new_list.add_message_id(message_object.message_id)

    # store list in storage
    add_list_to_storage(chat_id, new_list)

    if(not pin_message(update, context, message_object)):
        is_admin, can_pin, _ = check_bot_rights(update)
        if(not is_admin):
            mod_message = "\n\n" + msg.NOT_ADMIN
        elif(not can_pin):
            mod_message = "\n\n" + msg.NO_PIN_RIGHTS
        if(not is_admin or not can_pin):
            edit_list_message(context, new_list, new_list.show_list() + mod_message)


def extract_list_id(text):
    return re.search(c.regex_list_id, text).groupdict()["list_id"]

def extract_item_id(text):
    return re.search(c.regex_item_id, text).groupdict()["item_id"]

def is_group(update):
    is_group = False
    if(update.message.chat.type == update.message.chat.GROUP or update.message.chat.type == update.message.chat.SUPERGROUP):
        is_group = True
    return is_group

def is_supergroup(update):
    is_supergroup = False
    if(update.message.chat.type == update.message.chat.SUPERGROUP):
        is_supergroup = True
    return is_supergroup

def check_bot_rights(update):
    chat = update.message.chat
    if(chat.type == chat.PRIVATE):
        return True, True, True
    is_admin = False
    can_pin = False
    can_delete = False
    # get list of admins
    admins = chat.get_administrators()
    for admin in admins:
        if(admin.user.username == c.OWN_USERNAME):
            is_admin = True
            can_pin = admin.can_pin_messages
            can_delete = admin.can_delete_messages
            break
    return is_admin, can_pin, can_delete


def delete_message(update):
    try:
        update.message.delete()
        return True
    except:
        return False

def pin_message(update, context, message):
    try:
        context.bot.pin_chat_message(chat_id = update.message.chat.id, message_id = message.message_id, disable_notification = True)
        return True
    except BadRequest:
        return False

def has_list_id(command, update, lists):
    list_id = extract_list_id(command)
    if(str(list_id) in lists):
        return list_id
    else:
        ptbh.reply(update, msg.LIST_ID_UNKNOWN.format(gbc.ALL_LISTS["full"]))
        return False

######### /add_listitem ##########
def add_item_to_list(update, context):
    lists = get_lists_from_storage(update.message.chat.id)
    command = update.message.text.strip()
    list_id = has_list_id(command, update, lists)

    if(not list_id): return

    current_list = lists[str(list_id)]
    # get new id
    item_id = current_list.get_next_id()

    command = command[(15+len(list_id)):]

    lines = command.split("\n")
    # remove all empty strings
    lines = list(filter(None, lines))

    # throw error, if no arguments are passed
    if(len(lines) == 0):
        ptbh.reply(update, msg.ADD_ITEM_NO_ARGS)
        return

    for i, ita in enumerate(lines):
        id = item_id + i
        item = Item(id, list_id, ita)
        current_list.add_item(item)
    
    text = current_list.show_list(is_group(update))
    if(len(text) > c.MESSAGE_MAX_LENGTH*0.8):
        ptbh.reply(update, msg.ADD_ITEM_LIST_TOO_LONG)
        return
    edit_list_message(context, current_list, text)
    add_list_to_storage(update.message.chat.id, current_list)
    ##### insert LINK to message
    if(is_supergroupgroup(update)):
        linkable_id = str(update.message.chat.id)[4:] if str(update.message.chat.id).startswith("-100") else update.message.chat.id
        ptbh.reply(update, msg.ITEMS_ADDED_W_LINK.format(linkable_id, current_list.message_id, current_list.title))
    else:
        ptbh.reply(update, msg.ITEMS_ADDED)

########## /del_ ##########
def remove_item_from_list(update, context):
    # get ids given in the command
    lists = get_lists_from_storage(update.message.chat.id)
    command = update.message.text.strip()
    list_id = has_list_id(command, update, lists)
    if(not list_id):
        return

    current_list = lists[str(list_id)]
    
    item_id = int(extract_item_id(command))
    
    try:
        item = current_list.items[item_id]
    except:
        ptbh.reply(update, msg.ITEM_ID_UNKNOWN)
        return

    if(item.completed):
        ptbh.reply(update, msg.ITEM_COMPLETED_ERROR)
        return

    # mod_message = modification of the list-message if the bot hasn't admin or delete rights.
    mod_message = ""
    if(not delete_message(update)):
        is_admin, _, can_delete = check_bot_rights(update)
        if(not is_admin):
            mod_message = "\n\n" + msg.NOT_ADMIN
        elif(is_admin and not can_delete):
            mod_message = "\n\n" + msg.NO_DELETE_RIGHTS
        else:
            raise RuntimeError('While processing the callback to delete a message this error occured: ')

    # finish completion and edit original message
    completed_by = ptbu.getUsername(update, True)
    current_list.set_item_completed(item_id, completed_by)
    text = current_list.show_list(is_group(update)) + mod_message
    edit_list_message(context, current_list, text)
    add_list_to_storage(update.message.chat.id, current_list)
    

def close_list(update, context):
    command = update.message.text.strip()
    lists = get_lists_from_storage(update.message.chat.id)
    list_id = has_list_id(command, update, lists)
    if(not list_id): return
    current_list = lists[str(list_id)]
    completed_by = ptbu.getUsername(update, True)
    current_list.set_all_items_completed(completed_by)

    text = current_list.show_list(is_group(update))
    edit_list_message(context, current_list, text)

    ptbh.reply(update, msg.ALL_SET_COMPLETED.format(completed_by))
    add_list_to_storage(update.message.chat.id, current_list)

def edit_list_message(context, current_list, text):
    context.bot.edit_message_text(chat_id = current_list.chat_id, message_id = current_list.message_id, text = text, parse_mode = ParseMode.HTML)

def write_list_item(list_obj):
    """Calls built-in print function while writing the list.
    params: list_obj: List
    returns str from List-Object"""
    return list_obj.print_list()

def show_lists(update, context):
    name = ptbu.get_group_title(update)
    lists = get_lists_from_storage(update.message.chat.id)
    lists_list = lists.values()
    # if the list is emtpy: return a help-message
    if not lists_list:
        ptbh.reply(update, msg.LIST_EMPTY)
        return
    # initializing header text here, as group_name needs to be filled but two blanks are required
    header = "<b>Lists for " + name + " - {}-{}</b>\n"
    # getting an array of messages
    messages = ptbh.split_messages(list_to_split=lists_list, maximum=c.T_NUM_OF_ITEMS_ON_LISTS_LIST, header = header, callback = write_list_item)
    for m in messages:
        m ="\n".join(m)
        update.message.reply_html(m, quote=False)

def get_list_by_title(lists, title):
    list_id = False
    for key, user_list in lists.items():
        if(user_list.title == title):
            list_id = key
            break
    return list_id

def delete_list(update, context):
    chat_id = update.message.chat.id
    title = update.message.text[9:].strip()
    lists = get_lists_from_storage(chat_id)
    list_id = get_list_by_title(lists, title)
    if(not list_id): 
        ptbh.reply(update, msg.LIST_ID_UNKNOWN.format(gbc.ALL_LISTS["full"]))
        return

    delete_list_from_storage(chat_id, list_id)
    ptbh.reply(update, msg.LIST_DELETED.format(title))


def show_list(update, context):
    chat_id = update.message.chat.id
    title = update.message.text[10:].strip()
    lists = get_lists_from_storage(chat_id)
    list_id = get_list_by_title(lists, title)
    if(not list_id): 
        ptbh.reply(update, msg.LIST_ID_UNKNOWN.format(gbc.ALL_LISTS["full"]))
        return

    current_list = lists[str(list_id)]
    message = update.message.reply_html(current_list.show_list(is_group(update)))
    current_list.add_message_id(message.message_id)
    add_list_to_storage(chat_id, current_list)
    pin_message(update, context, message)
