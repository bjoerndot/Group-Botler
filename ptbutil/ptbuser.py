# extracts the name of a user
def getUsername(update, modifier):
    entity = "@" if modifier else ''
    username = entity + update.message.from_user.username if update.message.from_user.username is not None else getFullName(update, modifier)
    return username


# extacts the full name of a user as inline-link
def getFullName(update, modifier):
    firstName = getFirstName(update)
    lastName = getLastName(update)
    username = "<a href='tg://user?id={}'>{} {}</a>".format(update.message.from_user.id, firstName, lastName) if modifier else "{} {}".format(firstName, lastName)
    return username

def getFirstName(update):
    return update.message.from_user.first_name if update.message.from_user.first_name else ""

def getLastName(update):
    return update.message.from_user.last_name if update.message.from_user.last_name else ""

def constructLinkableName(userId, fullName = None, username = None):
    if username == None:
        username = "<a href='tg://user?id={}'>{}</a>".format(userId, fullName)
    else:
        username = "@{}".format(username)
    return username

## TG related service ##
def getUserId(update):
    userId = update.message.from_user.id
    return userId

def get_group_title(update):
    group_title  = update.message.chat.title if update.message.chat.title else getUsername(update, True)
    return group_title
