import random, math, re
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from typing import List

def draw_answer(answers):
    return random.choice(answers)

def get_text(text):
    if isinstance(text, list):
        text = draw_answer(text)
    return text

def reply(update, text, **kwargs):
    text = get_text(text)
    update.message.reply_html(text = text, **kwargs)

def indirect_reply_to(bot, chat_id, text, reply_to):
    text = get_text(text)
    bot.send_message(chat_id = chat_id, text = text, parse_mode = ParseMode.HTML, reply_to_message_id = reply_to)

def forward_message(bot, update, receiver):
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    bot.forward_message(receiver, chat_id, message_id)

def split_messages(list_to_split, maximum, header, callback, *args):
    message_segments = (len(list_to_split) + (maximum-1))//maximum
    segments = []
    for i in range(message_segments):
        text_parts = [header.format((i*maximum)+1, min(((i+1)*maximum), len(list_to_split)))]
        segments.append(text_parts)
    idx = 0
    for item in list_to_split:
        idx += 1
        for msg in range(message_segments):
            if (msg*maximum) < idx < ((msg+1)*maximum)+1:
                segments[msg].append(callback(item, *args))
    return segments

### keyboards

def calc_num_lines(length: int, items_per_row: int) -> int:
    return math.ceil(length / items_per_row)

def create_cb_code(case: int, answer: int) -> str:
    return "{}-{}".format(case, answer)

def unpack_cb_code(code: str):
    vals = code.split("-")
    return int(vals[0]), int(vals[1])

def build_inline_keyboard(args: List[str], case: int, items_per_row: int = 3):
    num_lines = calc_num_lines(len(args), items_per_row)
    lines = []
    for i in range(num_lines):
        lines.append([])
    index = 0
    for arg in args:
        index += 1
        for i in range(num_lines):
            if (i*items_per_row) < index < (i+1)*items_per_row+1:
                lines[i].append(InlineKeyboardButton(arg, callback_data=create_cb_code(case, index-1)))
    return lines

def get_inline_keyboard_markup(args: List[str], case: int, items_per_row: int = 3):
    return InlineKeyboardMarkup(build_inline_keyboard(args, case, items_per_row))

def single_line_keyboard(arg):
    reply_keyboard = [[arg]]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard = True)

def build_keyboard(args, items_per_row):
    reply_keyboard = []
    num_lines = calc_num_lines(len(args), items_per_row)
    idx = 0
    for l in range(num_lines):
        line = []
        for i in range(items_per_row):
            if idx < len(args):
                line.append(args[idx])
            idx += 1

        reply_keyboard.append(line)
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard = True)


# votes

def write_vote(question: str, options: List[str]) -> str:
    options = ["<b>{}</b>: ".format(o.lstrip(' ')) for o in options]
    text = "<b>{}</b>\n\n{}".format(question, "\n\n".join(options))
    return text

def write_anon_vote(question: str, options: List[str], value: str) -> str:
    options = ["<b>{}</b>: {}".format(o, value) for o in options]
    text = "<b>{}</b>\n\n{}".format(question, "\n\n".join(options))
    return text

def rewrite_vote(text: str, option: int, all_options, username: str) -> str:
    optionText = all_options[option]
    ### cleaning text, if user had already voted
    text = text.replace(" " + username + " |", "")
    text = text.splitlines()
    expression = re.escape(optionText) + r".*"
    for i in range(len(text)):
        if re.search(expression, text[i]):
            text[i] += "{} | ".format(username)
    text = "\n".join(text) + "\n"
    return text

# multipage

# def num_of_pages(length: int, items_per_page: int) -> int:
#     return math.ceil(length/items_per_page)

# def get_items_to_display(items: List[str], items_per_page: int, page: int) -> List[str]:
#     page = page-1
#     return items[items_per_page*page:items_per_page*(page+1)]

# def write_item_list(items: List[str], header: str, page: int, sum_of_pages: int, items_per_page: int) -> str:
#     text = f"<b>{header}</b>\n{page}/{sum_of_pages}\n\n"
#     join_text = []
#     for idx, i in enumerate(items):
#         join_text.append(f"{(idx+1)+((page-1)*items_per_page)}. {str(i)}")
#     text += "\n".join(join_text)
#     return text

# def build_carousel_list(page: int, length: int) -> List[str]:
#     if length > 2:
#         after = page+1 if page+1 <= length else length -2
#         before = page+2 if page-1==0 else page-1
#         pages = [before, page, after]
#         pages.sort()
#     else:
#         pages = [1,2]
#     final_menu = []
#     for p in pages:
#         if p == page:
#             final_menu.append("• {} •".format(p))
#         else:
#             final_menu.append(str(p))
#     if page != 1:
#         final_menu.insert(len(final_menu), "⏮")
#     if page!= length:
#         final_menu.insert(len(final_menu), "⏭")
#     return final_menu

# def setup_multipage_inline(list_of_items, header, items_per_page, callback, page = 1):
#     items = get_items_to_display(list_of_items, items_per_page, page)
#     num_pages = num_of_pages(len(list_of_items), items_per_page)
#     text = write_item_list(items, header, page, num_pages, items_per_page)
#     menu = build_carousel_list(page, num_pages)
#     keyboard_length = 2 if num_pages == 2 else 3
#     reply_markup = get_inline_keyboard_markup(menu, callback, keyboard_length)
#     return text, reply_markup

# def handle_multipage(bot, query, answer, options, header, items_per_page, list_of_items, callback):
#     num_pages = num_of_pages(len(list_of_items), items_per_page)
#     if options[answer] == "⏮":
#         page = 1
#     elif options[answer] == "⏭":
#         page = num_pages
#     else:
#         page = int(options[answer])
#     text, reply_markup = setup_multipage_inline(list_of_items, header, items_per_page, callback, page)
#     bot.answer_callback_query(query.id, text="Loading...")
#     bot.edit_message_text(text=text,
#                           chat_id=query.message.chat.id,
#                           message_id=query.message.message_id,
#                           reply_markup = reply_markup,
#                           parse_mode = ParseMode.HTML)
#     return menu