# import telegram-specific libraries
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

# import general libraries
import datetime, shelve, re

# import general helper-tools
import dtutil
import user_management as um

# import telegram-specific helper-tools
import ptbutil.ptbuser as ptbu
import ptbutil.ptbdecorators as ptbd
import ptbutil.ptbhelper as ptbh

# import messages and constants
import group_botler_messages as msg
import group_botler_constants as c


# import classes
from job import Job

class Reminder:
    def __init__(self, name, end_date, callback, reply_to, id, repeating, text, interval = None):
        self.name = name
        self.end_date = end_date
        self.callback = callback
        self.reply_to = reply_to
        self.id = id
        self.repeating = repeating
        self.text = text
        self.interval = interval
    
    def __repr__(self):
        return f'REMINDER(Object) ({self.name}): end_date/nextExecution = {dtutil.getDateAndTime(self.end_date)}, callback = {self.callback}, reply_to = {str(self.reply_to)}, id = {str(self.id)}, repeating = {self.repeating}, text = {self.text}, interval = {self.interval}'

    def get_remaining_time(self):
        return self.end_date - datetime.datetime.utcnow()

    def print(self):
        interval = f"{dtutil.get_timedelta_string(self.interval)}, Next: " if self.repeating else ""
        return f"<code>{self.name}</code>: {interval}{dtutil.getTime(self.end_date)}UTC"

    def print_long(self):
        remaining_time = dtutil.get_timedelta_string(self.get_remaining_time())
        interval = f"Interval: <b>{dtutil.get_timedelta_string(self.interval)}</b> - " if self.repeating else ""
        return f"<code>{self.name}</code>\n{interval}Remaining time: <b>{remaining_time}</b> - Reminder at: <b>{dtutil.getDateAndTime(self.end_date)}</b>\n"

    def next_execution(self):
        start_time = self.end_date
        now = datetime.datetime.utcnow()
        while start_time < now:
            start_time = start_time + self.interval
        return start_time

### This is what a reminder "object" looks like
# job = {name: "String", end_date: "Date", callback: "String", reply_to: "int", chatId: "int", repeating: "Bool", interval = "timedelta", text = "String"}

### Persistent Storage Operations ###
# reminders are stored by their name
def add_reminder_to_storage(id, reminder):
    """Adds reminder to user-object in shelve
    params: id: int/str, reminder: Reminder"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        user.reminders.update({reminder.name: reminder})
        db[str(id)] = user

def delete_reminder_from_storage(id, reminder_name):
    """Deletes reminder from user-object in shelve
    params: id: int/str, reminder_name: str"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        del user.reminders[reminder_name]
        db[str(id)] = user

def get_reminder_from_storage(id, reminder_name):
    """Gets reminder from storage, if existent
    params: id: int/str, reminder_name: str
    returns reminder: Reminder"""
    with shelve.open(c.SHELVE_MAIN) as db:
        try:
            reminder = db[str(id)].reminders[reminder_name]
            return reminder
        except KeyError:
            return ""

def check_reminder_existence(id, reminder_name):
    """Checks whether a reminder already exists
    params: id: int/str, reminder_name: str
    returns flog: Bool"""
    with shelve.open(c.SHELVE_MAIN) as db:
        user = db[str(id)]
        flag = True if reminder_name in user.reminders else False
        return flag


### Helpers ###
def get_reply_to_text(update):
    """If Pyhton-Telegram-Bots Update-Object has a reply_to, return the text
    params: update:Update
    returns: str"""
    try:
        message_text = update.message.reply_to_message.text
        return message_text
    except AttributeError:
        update.message.reply_html(msg.R_NO_REPLY)
        return update.message.text

def get_reply_to_id(update):
    """If Pyhton-Telegram-Bots Update-Object has a reply_to, return the id
    params: update:Update
    returns: int"""
    try:
        message_id = update.message.reply_to_message.message_id
        return message_id
    except AttributeError:
        print("reply to not there")
        update.message.reply_text(text=msg.R_NO_REPLY)
        return update.message.message_id

def get_hours_and_minutes(time_string):
    """Get Hours and minutes from a string
    params: time_string: str
    returns a tuple of int (hour, minute)"""
    if time_string.endswith("UTC"):
        time_string = time_string[:-3]
    hour_min_regex = r"(?P<hour>\d{1,}):(?P<minute>\d{2})"
    hour_min = re.match(hour_min_regex, time_string).groupdict()
    return int(hour_min.get("hour")), int(hour_min.get("minute"))

def get_future_time(hour, minute):
    """Find closest event in time in the future
    params: hour: int, minute: int
    returns Datetime-Object
    """
    next = datetime.datetime.utcnow().replace(hour=hour, minute=minute)
    if next < datetime.datetime.utcnow():
        next = next + datetime.timedelta(hours=24)
    return next

def extract_time_with_unit(input_value):
    """Extract seconds from input with unit (e.g. 120m)
    params: input_value: str
    returns seconds: int"""
    # run a regex on the input_value
    expression = r'(?P<value>\d*)(?P<unit>\w*)'
    value = re.match(expression, input_value).groupdict()
    try:
        seconds = int(value.get("value"))
        if value.get("unit") == "h":
            seconds = seconds * 3600
        elif value.get("unit") == "m":
            seconds = seconds * 60
        elif value.get("unit") == "s":
            seconds = seconds
        elif value.get("unit") == "d":
            seconds = seconds*60*60*24
        elif value.get("unit") == "w":
            seconds = seconds*60*60*24*7
        return seconds
    except ValueError:
        raise AttributeError()

def extract_time(input_value):
    """Takes a string and extracts the possible time meant
    params: input_value: str
    returns datetime.timedelta"""
    hours = 0
    minutes = 0
    seconds = 0
    # check if input_value is a simple number -> seconds:
    try:
        seconds = int(input_value)
    except ValueError:
        if ":" in input_value:
            hours, minutes = get_hours_and_minutes(input_value)
            # check if input is absolute time
            if input_value.endswith("UTC"):
                remind_time = get_future_time(hours, minutes).replace(second=0)
                seconds = (remind_time - datetime.datetime.utcnow()).total_seconds()
                # get timedelta until execution
                hours, minutes = 0, 0
        # if input_value doesn't have a ":" look for time indicators like s, m, h, etc.
        else:
            seconds = extract_time_with_unit(input_value)
    finally:
        return datetime.timedelta(hours=hours, seconds=minutes*60+seconds)

### Persistent to running ###
# go through all reminders in shelve reminders and reschedule the jobs which will happen in the future
def scheduleReminders(job_queue):
    to_delete = []
    with shelve.open(c.SHELVE_MAIN) as db:
        # get all registered users
        all_users = list(db.keys())
        # iterate through all registered users
        for user in all_users:
            # reminders from each user
            jobs = db[user].reminders
            # iterarte through each reminder
            for key, value in jobs.items():
                # check if a reminder is already out of date
                if datetime.datetime.utcnow() > value.end_date and not value.repeating:
                    to_delete.append((user, key))
                else:
                    # reschedules jobs
                    if value.callback == c.RUN_REMINDER:
                        job = Job(value.id, value.reply_to, str(key), str(key))
                        job_queue.run_once(run_reminder, value.end_date, context=job, name = str(key))
                    elif value.repeating:
                        next_execution = value.next_execution()
                        job = Job(value.id, 0, value.text, value.name)
                        job_queue.run_repeating(run_repeating_reminder, value.interval, next_execution, context=job, name = str(key))
                    else:
                        print("Could't schedule job {}: Missing function to call.".format(value["name"]))
                        to_delete.append((user, key))


    for item in to_delete:
        delete_reminder_from_storage(item[0], item[1])

### shows ###
@ptbd.creatorOnly
def list_all_reminders(update, context):
    db = shelve.open(c.SHELVE_MAIN)
    groups = list(db.keys())
    db.close()
    for group in groups:
        list_reminders(update, context, group)

def get_jobs(job_queue):
    """Return a list of jobs
    params: job_queue"""
    jobs = job_queue.jobs()
    return jobs

def get_reminders(jobs, chat_id):
    """Looks through a list of Python-Telegram-Bot-Jobs and looks them up in the database for chat_id
    params: jobs: List of PTB-Jobs, chat_id: int/str"""
    reminders = []
    with shelve.open(c.SHELVE_MAIN) as db:
        planned_reminders = db[str(chat_id)].reminders
        if not planned_reminders:
            return []
        for j in jobs:
            if j.context.name not in planned_reminders or j.removed:
                continue
            reminders.append(planned_reminders[j.context.name])
    return sorted(reminders, key=lambda k: k.end_date)

def print_reminders(reminders, short = True):
    """Creates a printable string from reminder-objects-list."""
    reminder_list_items = []
    for r in reminders:
        printed_reminder = r.print() if short else r.print_long()
        reminder_list_items.append(printed_reminder)
    reminder_list = "\n".join(reminder_list_items)
    if short:
        reminder_list += "\n\n/reminders_long for all details"
    return reminder_list

def create_reminder_list_message(job_queue, id, name, short = True):
    """Gathers all necessary information to write a reminder-list-message"""
    all_jobs = get_jobs(job_queue)
    print(all_jobs)
    if not all_jobs:
        return msg.R_NO_REMINDERS.format(name)
    reminders = get_reminders(all_jobs, id)
    print(reminders)
    if not reminders:
        return msg.R_NO_REMINDERS.format(name)
    reminder_list = print_reminders(reminders, short)
    return msg.R_REMINDER_LIST.format(name, reminder_list)

@um.is_user_registered
def list_reminders_summary(update, context):
    """Is called by /list_reminders or /reminders
    Gets all reminders and sends a list to users."""
    chat_id = update.message.chat.id
    chat_name = ptbu.get_group_title(update)
    reminder_message = create_reminder_list_message(context.job_queue, chat_id, chat_name)
    ptbh.reply(update, reminder_message, quote=False)

# list all jobs currently in queue
@um.is_user_registered
def list_reminders(update, context, chat_id = 0):
    """Is called by /reminders_long or /list_reminder_long"""
    chat_name = chat_id
    if not chat_id:
        chat_id = update.message.chat.id
        chat_name = ptbu.get_group_title(update)
    reminder_message = create_reminder_list_message(context.job_queue, chat_id, chat_name, False)
    ptbh.reply(update, reminder_message, quote=False)


def show_reminder(update, context):
    """Is called on /show_reminder
    Grabs reminder from shelve and sends it to users"""
    chat_id = update.message.chat.id
    reminder_name = context.args[0]
    reminder = get_reminder_from_storage(chat_id, reminder_name)
    if reminder.reply_to:
        context.bot.send_message(chat_id=chat_id, text=reminder.name, reply_to_message_id=reminder.reply_to)
    else:
        context.bot.send_message(chat_id = chat_id, text= reminder.text)

### Adds ###

# handlers #

# parse user information and schedule the reminder
@um.is_user_registered
def handle_reminders(update, context):
    """Is called with /add_reminder
    Since /add_reminder can take multiple arguments it needs to send the message to an appropriate handler
    params: update: Update, context: Context"""
    id = update.message.chat.id
    # check if this name is taken already
    try:
        name = context.args[0]
    except IndexError:
        ptbh.reply(update, msg.R_ERROR_ARGS_REMINDER)
        return
    if check_reminder_existence(id, name):
        # notify user
        ptbh.reply(update, msg.R_ERROR_JOB_EXISTS)
        return
    # distribute based on no. of arguments
    num_of_args = len(context.args)
    if num_of_args == 2:
        add_single_reminder(update, context)
    elif num_of_args == 3:
        add_reapeting_reminder(update, context)
    else:
        ptbh.reply(update, msg.R_ERROR_ARGS_REMINDER)
        return

def add_single_reminder(update, context):
    """Prepare single reminder for storage and setup
    params: update: Update, context: Context"""
    name = context.args[0]
    # get time to be reminded
    try:
        td = extract_time(context.args[1])
        message_id = get_reply_to_id(update)
        print(message_id)
        setup_reminder(context.bot, update, context.job_queue, update.message.chat.id, message_id, str(name), td)
    except AttributeError:
        ptbh.reply(update, msg.R_ERROR_ARG_REMINDER_TIME)

def add_reapeting_reminder(update, context):
    name = context.args[0]
    start_time = datetime.datetime.utcnow() + extract_time(context.args[2])
    interval = context.args[1]
    # extract interval information
    if interval == "daily":
        seconds = 24*60*60
    elif interval == "hourly":
        seconds = 1*60*60
    elif interval == "weekly":
        seconds = 7*24*60*60
    else:
        seconds = extract_time_with_unit(interval)
    interval = datetime.timedelta(seconds = seconds)
    message_text = get_reply_to_text(update)
    setup_repeating_reminder(context.bot, update, context.job_queue, update.message.chat.id, name, interval, start_time, message_text)

def setup_reminder(bot, update, job_queue, chat_id, message_id, name: str, timedelta: datetime.timedelta, abs_time = False, dt = 0):
    """Schedules the job in job_queue. Adds job to persistent storage. Notifies user"""
    remind_time = datetime.datetime.utcnow() + timedelta
    job = Job(chat_id, message_id, str(name), str(name))
    job_queue.run_once(run_reminder, remind_time, context=job, name = str(name))
    reminder = Reminder(name, remind_time, "run_reminder", message_id, chat_id, False, name)
    add_reminder_to_storage(chat_id, reminder)
    update.message.reply_html(msg.R_ADD_JOB_SUCCESS.format(name))

def setup_repeating_reminder(bot, update, job_queue, chat_id, name, interval, start_time, text):
    """Schedules the job in job_queue. Adds job to persistent storage. Informs user"""
    job = Job(chat_id, 0, text, name)
    job_queue.run_repeating(callback = run_repeating_reminder, interval = interval, first = start_time, context=job, name = name)
    reminder = Reminder(str(name), start_time, "run_repeating_reminder", 0, chat_id, True, text, interval)
    add_reminder_to_storage(chat_id, reminder)
    update.message.reply_html(msg.R_ADD_JOB_SUCCESS.format(name))

# function to execute once a reminder is set
def run_reminder(context):
    """Executes the job and deletes it from storage"""
    job = context.job
    delete_reminder_from_storage(job.context.id, job.context.text)
    context.bot.send_message(chat_id=job.context.id, text=job.context.text, reply_to_message_id=job.context.message_id)

def run_repeating_reminder(context):
    """Executes a repeating job and sets the next execution"""
    job = context.job
    id = job.context.id
    reminder = get_reminder_from_storage(id = id, reminder_name = job.context.name)
    next_execution = reminder.next_execution()
    reminder.end_date = next_execution
    add_reminder_to_storage(id = id, reminder = reminder)
    context.bot.send_message(chat_id=id, text=job.context.text)

### Deletes ###

# handlers #
@ptbd.creatorOnly
def kill_reminder(update, context):
    """Deletes a reminder from an foreign chat"""
    chat_id = context.args[0]
    reminder_name = context.args[1]
    delete_reminder(update, chat_id, reminder_name, context.job_queue)

@um.is_user_registered
def delete_reminder_handler(update, context):
    chat_id = update.message.chat.id
    reminder_name = "".join(context.args)
    delete_reminder(update, chat_id, reminder_name, context.job_queue)

# executioner #
def delete_reminder(update, chat_id, reminder_name, job_queue):
    if not check_reminder_existence(chat_id, reminder_name):
        update.message.reply_html(msg.R_ERROR_404)
        return
    job = job_queue.get_jobs_by_name(reminder_name)[0]
    if str(job.context.id) == str(chat_id):
        job.schedule_removal()
        delete_reminder_from_storage(chat_id, reminder_name)
        update.message.reply_html(msg.R_DEL_JOB_SUCCESS.format(reminder_name))
    else:
        update.message.reply_html(msg.R_ERROR_404)

def silent_delete_reminder(chat_id, reminder_name, job):
    job.schedule_removal()
    delete_reminder_from_storage(chat_id, reminder_name)
