import dtutil

class User:
    def __init__(self, id, chat_type, first_name, last_name, group_name, name_handle, date_of_registration, last_updated, votes = {}, reminders = {}, lists = {}):
        self.id = id
        self.chat_type = chat_type
        self.first_name = first_name
        self.last_name = last_name
        self.group_name = group_name
        self.name_handle = name_handle
        self.date_of_registration = date_of_registration
        self.last_updated = last_updated
        self.votes = votes
        self.reminders = reminders
        self.lists = lists
    
    def __repr__(self):
        name = f'{self.first_name} {self.last_name}' if self.chat_type == "private" else self.group_name
        votes = "YES" if self.votes else ""
        reminders = "YES" if self.reminders else ""
        user_representation = f"""USER
---id = {self.id}
---chat-type = {self.chat_type}
---name = {name}
---handle = {self.name_handle}
---date of registration = {dtutil.getDateAndTime(self.date_of_registration)}
---last updated = {dtutil.getDateAndTime(self.last_updated)}
---votes = {votes}
---reminders = {reminders}"""
        return user_representation
    
    def __str__(self):
        name = self.group_name if self.group_name else f'{self.first_name} {self.last_name}'
        return f'<b>{name}</b> ({self.chat_type}): Reg. since <code>{dtutil.getDate(self.date_of_registration)}</code> | Last updated: <code>{dtutil.getDate(self.last_updated)}</code>'

    def get_lists(self):
        try:
            val = self.lists
        except:
            self.lists = {}
        finally:
            return self.lists