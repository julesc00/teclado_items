
from user import User


users = [
    User(1, "julito", "pass123"),
    User(2, "charbelito", "aaa")
]

username_mapping = {u.username: u for u in users}
userid_mapping = {u.id: u for u in users}


def authenticate(username, password):
    user = username_mapping.get(username, None)
    if user and user.password == password:
        return user


def identity(payload):
    user_id = payload["identity"]
    return username_mapping.get(user_id, None)
