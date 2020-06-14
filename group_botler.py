# import telegram-specific libraries
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, JobQueue
from telegram import ParseMode, CallbackQuery
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html

# import general libraries
from enum import Enum
import datetime
import shelve

# import general helper-tools
import dtutil
import user_management as um

# import telegram-specific helper-tools
import ptbutil.ptbuser as ptbu
import ptbutil.ptbdecorators as ptdb
import ptbutil.ptbhelper as ptbh
import ptbutil.errorhandling as ptbe

# import functionalities
import group_botler_reminder as reminder
import group_botler_triggers as triggers
import group_botler_votes as votes
import group_botler_lists as lists
import group_botler_backup as backup
import group_botler_decorators as dec

# import constants and messages
import group_botler_messages as msg
import group_botler_constants as c
import group_botler_commands as gbc

# import telegram-bot-token
from group_botler_private import TOKEN

#import classes
from user import *
from job import Job

# VERSION
# 1.0.0


class CallbackOptions(Enum):
    VOTE = 0
    HELP = 1

# basic functions for telegram bot
# Start: Registering user in shelve.


def start(update, context):
    """Welcome users and notify bot-creator
    Calls register_new_user if the user is unknown."""
    ptbh.reply(update, msg.START)
    chat_id = update.message.chat.id
    if not um.group_existent(chat_id):
        um.register_new_user(update, context.bot)
    if not um.existent_on_triggers(chat_id):
        triggers.register_user_in_triggers(chat_id)


@ptdb.creatorOnly
def show_users(update, context):
    user_list = []
    with shelve.open(c.SHELVE_MAIN) as db:
        user_list = list(db.values())
    messages = ptbh.split_messages(
        user_list, 20, "<b>Users</b> - {}-{}\n", str)
    for m in messages:
        m = "\n\n".join(m)
        ptbh.reply(update, m)


def create_help_inline_keyboard():
    """creates keyboard markup for /help-command"""
    return ptbh.get_inline_keyboard_markup(c.HELP_MENU.keys(), CallbackOptions.HELP.value, c.HELP_KEYBOARD_LENGTH)


@dec.is_user_registered
def help(update, context):
    """Send help-dialog to users
    params: update: Update, context: Context"""
    keyboard = create_help_inline_keyboard()
    text = msg.H_START
    ptbh.reply(update, text, reply_markup=keyboard)

# Handle Callback after the callback has been sorted


def handle_help_callback(bot, update, query, answer):
    """Handle help callback - displays new text after user clicked a button
    params: bot, update, query (callback.query), answer: str (from pthb.unpack_cb_code)"""
    keyboard = create_help_inline_keyboard()
    # create list to chose answer from
    help_menu = list(c.HELP_MENU.keys())
    text = c.HELP_MENU[help_menu[answer]]
    # if user clicks buttons of already active text, Telegram throws an BadRequest
    # send a answer that the button is already displayed
    try:
        bot.edit_message_text(
            text=text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML)
    except BadRequest:
        bot.answer_callback_query(query.id, text=msg.H_ALR_DIS)
        return


def handle_vote_callback(bot, update, query, answer):
    votes.handle_vote_callback(bot, update, query, answer)


@dec.is_user_registered
def sort_callback(update, context):
    """Unpacks callback-data and forwards the handling to the corresponding handler
    params: update: Update, context: Context
    """
    query = update.callback_query
    code = query.data
    case, answer = ptbh.unpack_cb_code(code)
    CALLBACK_HANDLERS[case](context.bot, update, query, answer)


@dec.is_user_registered
def ping(update, context):
    """PING - fixed reply to see, whether the bot is still running
    params - update: Update, context: Context"""
    ptbh.reply(update, text=msg.S_PING, quote=False)


@dec.is_user_registered
def forward_question(update, context):
    handle_question_feedback(update, context, "question")


@dec.is_user_registered
def forward_feedback(update, context):
    handle_question_feedback(update, context, "feedback")


def handle_question_feedback(update, context, fb_type):
    ptbh.forward_message(context.bot, update, c.FEEDBACK_CHANNEL)
    message_id = update.message.message_id
    chat_id = update.effective_chat.id
    user = f"{mention_html(update.effective_user.id, update.effective_user.first_name)} (@{update.effective_chat.username})"
    user_text = " ".join(context.args)
    text = msg.S_NEW_QUESTION_FEEDBACK.format(
        fb_type, str(user), user_text, fb_type, chat_id, message_id)
    context.bot.send_message(c.CREATOR, text, parse_mode=ParseMode.HTML)


def answer_to_user(update, context):
    # splitting whole text by " " and retrieve only the first argument to get the command
    text = update.message.text_html.split()
    command_items = text[0].split("_")
    user_id = command_items[1]
    message_id = command_items[2]
    text = " ".join(text)
    message = context.bot.send_message(int(user_id), text=text, reply_to_message_id=int(
        message_id), parse_mode=ParseMode.HTML)
    if message:
        context.bot.send_message(c.CREATOR, text=msg.S_MESSAGE_SUCCESS)


# callback otions
CALLBACK_HANDLERS = [handle_vote_callback, handle_help_callback]


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)
    print("Group Botler started")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    job = updater.job_queue

    job.run_repeating(callback=backup.automated_backup,
                      interval=24*60*60, first=dtutil.getNextWeekday(datetime.datetime.utcnow().weekday()+1, 3), context=Job(0, '', '', 'Service-job: Backup data'), name='Service-job: Backup data')

    print("Reschedule jobs.")
    reminder.scheduleReminders(job)
    print("All jobs rescheduled.")
    print("Startup triggers")
    triggers.startup_trigger_script()
    print("Triggers started.")

    # commmands for administration
    dp.add_handler(CommandHandler("show_users", show_users))
    dp.add_handler(CommandHandler("question", forward_question))
    dp.add_handler(CommandHandler("feedback", forward_feedback))
    dp.add_handler(MessageHandler(Filters.regex("/answer_"), answer_to_user))
    dp.add_handler(CommandHandler("backup", backup.manual_backup))
    dp.add_handler(CommandHandler("restore_backup", backup.restore_backup))

    # commands for standard-bot-operations
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.regex(r"^\*ping"), ping))

    # commands for votes
    dp.add_handler(CommandHandler("vote", votes.create_vote))
    dp.add_handler(CallbackQueryHandler(sort_callback))

    # commands for reminders
    dp.add_handler(CommandHandler("add_reminder", reminder.handle_reminders))
    dp.add_handler(CommandHandler(
        "reminders", reminder.list_reminders_summary))
    dp.add_handler(CommandHandler("list_reminders",
                                  reminder.list_reminders_summary))
    dp.add_handler(CommandHandler("reminders_long", reminder.list_reminders))
    dp.add_handler(CommandHandler(
        "list_reminders_long", reminder.list_reminders))
    dp.add_handler(CommandHandler(
        "reminders_all", reminder.list_all_reminders))
    dp.add_handler(CommandHandler(
        "del_reminder", reminder.delete_reminder_handler))
    dp.add_handler(CommandHandler("kill_reminder", reminder.kill_reminder))
    dp.add_handler(CommandHandler("show_reminder", reminder.show_reminder))

    # commands for triggers
    dp.add_handler(CommandHandler("add_trigger", triggers.add_trigger))
    dp.add_handler(CommandHandler("del_trigger", triggers.del_trigger))
    dp.add_handler(CommandHandler("list_triggers", triggers.list_triggers))
    dp.add_handler(CommandHandler("triggers", triggers.list_triggers))

    # commands for lists
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.ADD_ITEM_TO_LIST["regex"]), lists.add_item_to_list))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.ADD_LIST["regex"]), lists.add_list))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.RM_ITEM_FROM_LIST["regex"]), lists.remove_item_from_list))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.CLOSE_LIST["regex"]), lists.close_list))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.ALL_LISTS["full"]), lists.show_lists))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.ALL_LISTS_ALT["full"]), lists.show_lists))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.DELETE_LIST["regex"]), lists.delete_list))
    dp.add_handler(MessageHandler(Filters.regex(
        gbc.SHOW_LIST["regex"]), lists.show_list))

    # log all errors
    dp.add_error_handler(ptbe.error)
    dp.add_handler(MessageHandler(Filters.text, triggers.call_trigger))

    print("Listening for updates....")
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
