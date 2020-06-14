# import telegram-specific libraries
from telegram.error import BadRequest
from telegram import ParseMode


# import general libraries
import datetime
import shelve
import json

# import
import group_botler_decorators as dec

# import telegram-specific helper-tools
import ptbutil.ptbuser as ptbu
import ptbutil.ptbhelper as ptbh

# import constants and messages
import group_botler_messages as msg
import group_botler_constants as c
from group_botler import CallbackOptions


class Vote:
    def __init__(self, date: datetime.datetime, question: str, answer_options: list, result: str):
        self.date = date
        self.question = question
        self.answer_options = answer_options
        self.result = result

    @classmethod
    def fromJSON(cls, obj):
        if not obj:
            return

        return cls(
            datetime.datetime.fromisoformat(obj["date"]),
            obj["question"],
            obj["answer_options"],
            obj["result"],
        )

    # TODO: add toJSON and fromJSON method


def write_vote_to_DB(id, vote):
    """Write the vote to shevle
    params: id: str/int, vote: Vote-Object"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        user.votes = vote
        db[str(id)] = user


def fetch_vote_from_DB(id):
    """Fetches vote from shelve
    params: id: str/int"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
    return user.votes


@dec.is_user_registered
def create_vote(update, context):
    id = update.message.chat.id
    args = update.message.text[6:]
    args = args.split(", ")
    len_args = len(args)
    if not len_args:
        ptbh.reply(update, text=msg.VOTE_NO_ARGS, quote=False)
        return
    elif len_args < 3:
        ptbh.reply(update, text=msg.VOTE_NOT_ENOUGH_ARGS, quote=False)
        return
    # preparing question and answers
    question = args[0]
    del args[0]
    answer_options = args
    keyboard = ptbh.get_inline_keyboard_markup(
        answer_options, CallbackOptions.VOTE.value, 1)
    message_text = ptbh.write_vote(question, answer_options)
    vote = Vote(datetime.datetime.utcnow(), question,
                answer_options, message_text)
    write_vote_to_DB(id, vote)
    message = update.message.reply_html(
        message_text, reply_markup=keyboard, quote=False)
    chat_type = update.message.chat.type
    if chat_type == "supergroup" or chat_type == "group":
        try:
            context.bot.pin_chat_message(
                message.chat.id, message.message_id, disable_notification=True)
        except BadRequest:
            ptbh.reply(update, msg.VOTE_NO_ADMIN, quote=False)


def handle_vote_callback(bot, update, query, answer):
    id = query.message.chat.id
    username = update.callback_query.from_user.username if update.callback_query.from_user.username else f'{update.callback_query.from_user.first_name} {update.callback_query.from_user.last_name}'
    vote = fetch_vote_from_DB(id)
    result = ptbh.rewrite_vote(
        vote.result, answer, vote.answer_options, username)
    keyboard = ptbh.get_inline_keyboard_markup(
        vote.answer_options, CallbackOptions.VOTE.value, 1)
    try:
        bot.edit_message_text(
            text=result,
            chat_id=id,
            message_id=query.message.message_id,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML)
        notification = ptbh.draw_answer(
            msg.VOTE_NOTIFY).format(vote.answer_options[answer])
    except BadRequest:
        notification = msg.VOTE_NO_CHANGE
    finally:
        bot.answer_callback_query(query.id, text=notification)
        vote.result = result
        write_vote_to_DB(id, vote)
