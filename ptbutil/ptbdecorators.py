from functools import wraps
from telegram import ParseMode

ACCESS_DENIED = "Access denied"


def creatorOnly(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != 420797901:
            context.bot.send_message(user_id, text=ACCESS_DENIED, parse_mode = ParseMode.HTML)
            return
        return func(update, context, *args, **kwargs)
    return wrapped
