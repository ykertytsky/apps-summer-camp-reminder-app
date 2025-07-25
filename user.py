import json

file_name = "users.json"

def add_task(user_id, task,time,deadline=None):
    users = get_json()
    time = str(time)
    deadline = str(deadline)
    print(users, 1)
    print(user_id)
    if user_id  in users:
        print(True)
    else:
        print(False)
    print(users[user_id], 1.1)
    if time in users[user_id]:
        users[user_id][time].append((task,deadline))
        print(users, 2)
    else:
        users[user_id][time] = [(task,deadline)]
        print(users, 3)
    with open(file_name, 'w') as f:
        json.dump(users, f)
    print(users, 4)

def get_tasks(user_id):
    users = get_json()
    return users[user_id]

def get_all_tasks(user_id):
    try:
        
        users = get_json()
        print(users)
        if users[user_id]:
            print(True)
            return users[user_id].values()
        else:
            print(False)
            return {}
    except:
        print("error in get_all_tasks")
        return {}

def get_json():
    with open(file_name, 'r') as f:
        users = json.load(f)
    print(users)
    return users
    
def append_user(user_id):
    users = get_json()
    if user_id in users:
        return
    users[user_id] = {}
    with open(file_name, 'w') as f:
        json.dump(users, f)
    print(user_id)