import group_botler_messages as msg

CREATOR = 420797901
ADMINISTRATION_CHANNEL = -1001496911160
FEEDBACK_CHANNEL = -1001322936764

SHELVE_MAIN = "users"
SHELVE_TRIGGERS = "triggers"

SHOW_USERS_ITEMS = 20

HELP_KEYBOARD_LENGTH = 2

HELP_MENU = {
    "🗳VOTE": msg.H_VOTE,
    "⏰REMINDERS (1)": msg.H_ADD_REMINDER,
    "⏰REMINDERS (2)": msg.H_EXISTING_REMINDERS,
    "💬TRIGGERS": msg.H_TRIGGERS,
    "📄LISTS": msg.H_LISTS,
    "About": msg.H_ABOUT
}

# Trigger-Script
T_NUM_OF_ITEMS_ON_TRIGGER_LIST = 30

# Reminders
# Reminder-Callback-Name
RUN_REMINDER = "run_reminder"
RUM_REPEATING = "run_repeating_reminder"

# Lists
regex_list_id = r"^/([a-zA-Z]*_)*(?P<list_id>\d*)"
regex_item_id = r"^/[a-zA-Z]*_\d*_(?P<item_id>\d*)"

OWN_USERNAME = "groupbotler"
T_NUM_OF_ITEMS_ON_LISTS_LIST = 25

MESSAGE_MAX_LENGTH = 4096