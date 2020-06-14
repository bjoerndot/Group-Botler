import json
import shelve
import datetime
from group_botler_triggers import Trigger, startup_trigger_script
from group_botler_constants import CREATOR
from user import *

def save_to_json(data, db_name):
    with open(db_name + ".json", "w") as outfile:
        json.dump(data, outfile)
    return


def get_data_from_json(db_name):
    json_data = {}
    with open(db_name + ".json", "r") as infile:
        json_data = json.load(infile)
    return json_data


def get_data_from_shelve(db_name, groups=None):
    # create empty object to store data from shelve in
    shelve_data = {}

    with shelve.open(db_name) as db:
        # get the groups, that shall be transfered - if none is given all groups will be transfered
        if not groups:
            keys = list(db.keys())
        else:
            keys = groups

        # copy all triggers
        if db_name == "triggers":
            for key in keys:
                # create object in empty data
                shelve_data[str(key)] = {}

                for e in db[str(key)]:
                    # store data by name as json
                    shelve_data[str(key)][e] = db[str(key)][e].toJSON()
        # copy all users
        elif db_name == "users":
            for key in keys:
                # create object in emtpty data
                shelve_data[str(key)]= db[str(key)].toJSON()
    return shelve_data


def store_data_in_shelve(data, db_name, groups):
    # store data for each group given
    for g in groups:
        with shelve.open(db_name, writeback=True) as db:
            shelve_group = db[str(g)]
            if db_name == "triggers":

                for item in data[str(g)]:
                    if item not in shelve_group:
                        shelve_group[str(item)] = Trigger.fromJSON(
                            data[str(g)][item])
            elif db_name == "users":
                shelve_group[str(g)] = User.fromJSON(data[str(g)])

            db[str(g)] = shelve_group


def backup(bot, groups=None):
    # stored as list to add "reminders" later
    databases = ["triggers", "users"]
    for db in databases:
        save_to_json(get_data_from_shelve(db, groups), db)
    bot.send_message(CREATOR, "Backup completed.")


def automated_backup(context):
    backup(context.bot)


def manual_backup(update, context):
    backup(context.bot)


def restore_backup(update, context):
    chat_id = update.message.chat.id
    # stored as list to add "reminders" later or to call it by user input
    databases = ["triggers"]
    restore(databases, [chat_id])
    startup_trigger_script()
    update.message.reply_html("Data restored.")


def restore(databases, groups):
    for db in databases:
        store_data_in_shelve(get_data_from_json(db), db, groups)
