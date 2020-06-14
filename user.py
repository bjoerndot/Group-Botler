import dtutil
import json
import datetime
from group_botler_votes import Vote
from group_botler_reminder import Reminder
from List import List

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
        """Gets all lists for this user and checks for existence

        Returns:
            Dict: Dictionary of List objects
        """
        try:
            val = self.lists
        except:
            self.lists = {}
        finally:
            return self.lists

    def toJSON(self):
        """Turns an User object into a json
        """
        def serialize(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, datetime.datetime):
                serial = obj.isoformat()
                return serial
            elif isinstance(obj, datetime.timedelta):
                serial = obj.total_seconds()
                return serial

            return obj.__dict__

        return json.dumps(self, default=serialize, sort_keys=True, indent=4)

    @classmethod
    def fromJSON(cls, obj):
        """Takes a json-object and turns it into a User"""
        # Data loaded from json
        data = json.loads(obj)

        # Each reminder needs to made into a class before it can be used
        reminders = {}
        for r in data["reminders"]:
            rem = Reminder.fromDICT(data["reminders"][r])
            reminders[r] = rem

        # Each list needs to made into a class before it can be used
        lists = {}
        for l in data["lists"]:
            li = List.fromDICT(data["lists"][l])
            lists[l] = li

        # Create the user-class
        return cls(
            data["id"],
            data["chat_type"],
            data["first_name"],
            data["last_name"],
            data["group_name"],
            data["name_handle"],
            datetime.datetime.fromisoformat(data["date_of_registration"]), # dates are stored as string and must be turned into a datetime
            datetime.datetime.fromisoformat(data["last_updated"]), # dates are stored as string and must be turned into a datetime
            Vote.fromJSON(data["votes"]), # Votes must be unpacked before they can be used
            reminders, # unpacked reminders, see above
            lists # unpacked lists, see above
        )