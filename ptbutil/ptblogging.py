import datetime
from telegram import ParseMode
import ptbutil.ptbuser as ptbu
import dtutil

## log to Channel ##
def logToChannel(receiver, bot, update, origin, message):
    timeOfAccess = datetime.datetime.now()
    serviceMessage = message.format(ptbu.getUserId(update), origin, ptbu.getUsername(update.message.from_user, True), dtutil.getDateAndTime(timeOfAccess))
    bot.send_message(receiver, text = serviceMessage, parse_mode = ParseMode.HTML)

def sendMessageToLog(receiver, bot, message):
    bot.send_message(receiver, message, parse_mode = ParseMode.HTML)
