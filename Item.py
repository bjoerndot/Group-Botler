import group_botler_commands as commands


class Item:
    def __init__(self, id, list_id, text, completed=False, completed_by=None):
        self.id = id
        self.list_id = list_id
        self.text = text
        self.completed = completed
        self.completed_by = completed_by

    def __str__(self):
        return f'Item: {{"id": {self.id}, "list_id": {self.list_id}, "text": "{self.text}", "completed": {self.completed}, "completed_by": "{self.completed_by}"}}'

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def show_item(self, is_group=False):
        if(self.completed):
            if(is_group):
                return f"- <s>{self.text}</s> {self.completed_by}"
            return f"- <s>{self.text}</s>"
        else:
            return f"- {self.text} {commands.RM_ITEM_FROM_LIST['full'].format(self.list_id, self.id)}"

    def set_completed(self, completed_by):
        self.completed = True
        self.completed_by = completed_by

    
    @classmethod
    def fromDICT(cls, obj):
        """Turns data formatted as dict into an Item object

        Returns:
            Item: Fully usable Item object
        """

        return cls(
            obj["id"],
            obj["list_id"],
            obj["text"],
            obj["completed"],
            obj["completed_by"]
        )