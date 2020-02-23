# COMMANDS

ADD_LIST = {"full": "/add_list", "regex": r"^/add_list"}
ADD_ITEM_TO_LIST = {"full": "/add_listitem_{}", "regex": r"^/add_listitem_\d*"} # list-id
ADD_ITEM_TO_LIST_WRONG = {"full": "/add_listitem_{}", "regex": r"^/add_listitem_\d*"} # list-id
RM_ITEM_FROM_LIST = {"full": "/del_{}_{}", "regex": r"^/del_\d*_\d*"} # list-id, item-id
CLOSE_LIST = {"full": "/cl_{}", "regex": r"^/cl_\d*"} # list-id
ALL_LISTS = {"full": "/lists"}
ALL_LISTS_ALT = {"full": "/list_lists"}
SHOW_LIST = {"full": "/show_list", "regex": r"^/show_list *"}
DELETE_LIST = {"full": "/del_list", "regex": r"^/del_list *"}