from functools import wraps
import shelve

import group_botler_constants as c

import user_management as um


def is_user_registered(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        id = update.effective_chat.id
        if not um.group_existent(id):
            um.register_new_user(update, context.bot)
        else:
            with shelve.open(c.SHELVE_MAIN) as db:
                user = db[str(id)]
                user = um.update_user(update, user)
                db[str(id)] = user
        return func(update, context, *args, **kwargs)
    return wrapped
