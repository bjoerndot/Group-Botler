import group_botler_commands as commands

class List:
    def __init__(self, id, title, created_by, created_at, chat_id, items = {}, edited_at = None, message_id = None):
        self.id = id
        self.title = title
        self.items = items
        self.created_by = created_by
        self.created_at = created_at
        self.edited_at = edited_at
        self.message_id = message_id,
        self.chat_id = chat_id

    def __str__(self):
        items = ", ".join(str(i) for i in self.items.values())
        return f'List: {{"title": "{self.title}", "id": {self.id}, "created_by": "{self.created_by}", "created_at": "{self.created_at}", "edited_at": "{self.edited_at}", "message_id": {self.message_id}, "chat_id": {self.chat_id}, "items": [{items}] }}'

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def show_list(self, is_group = False):
        list_items = ""
        for item in self.items.values():
            list_items += "\n" + item.show_item(is_group)
        return f"<b>{self.title}</b>\n{list_items}\n\nTo mark all items on this list as completed: {commands.CLOSE_LIST['full'].format(self.id)}\nTo add a new item to the list call: {commands.ADD_ITEM_TO_LIST['full'].format(self.id)} <i>list item text</i>"

    def print_list(self):
        return f"{self.title} <code>(created at: {self.created_at} - {self.get_num_of_items(True)} of {self.get_num_of_items()} items completed)</code>"

    def add_items(self, items):
        self.items = items

    def add_item(self, item):
        self.items.update({item.id: item})

    def add_message_id(self, message_id):
        self.message_id = message_id

    def set_item_completed(self, item_id, completed_by):
        self.items[item_id].set_completed(completed_by)

    def get_next_id(self):
        return len(self.items.keys()) + 1

    def set_all_items_completed(self, completed_by):
        for item in self.items:
            if not self.items[item].completed:
                self.set_item_completed(self.items[item].id, completed_by)

    def get_num_of_items(self, done = False):
        num_of_items = 0
        if done:
            for item in self.items.values():
                if item.completed:
                    num_of_items +=1
        else:
            num_of_items = len(self.items)
        return num_of_items