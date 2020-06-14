import shelve, json
from user import User

def save_to_json(data, db_name):
    with open(db_name + ".json", "w") as outfile:
        json.dump(data, outfile)
    return

def get_data_from_json(db_name):
    json_data = {}
    with open(db_name + ".json", "r") as infile:
        json_data = json.load(infile)
    return json_data


db = shelve.open('users')
# print(db['873847623'].votes.date)
# keys = list(db.keys())

# data = {}

# for k in keys:
#     obj = db[k]
#     print(obj)
#     objjson = obj.toJSON()
#     data[k] = objjson

# save_to_json(data, 'shit')
    

data = get_data_from_json('shit')
for k in data:
    user = User.fromJSON(data[k])
    if not user.lists: 
        continue
    print(k)
    print(user.lists['0'].message_id)