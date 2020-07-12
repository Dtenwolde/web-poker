from flaskr.lib.database import request_session
from flaskr.lib.models.models import UserModel
from typing import Optional

def get_user(username: str = None, user_id: int = None) -> Optional[UserModel]:
    db = request_session()

    sub = db.query(UserModel)
    if username is not None:
        sub = sub.filter(UserModel.username == username)
    elif user_id is None:
        sub = sub.filter(UserModel.id == user_id)
    else:
        return None
    return sub.one_or_none()


def get_users():
    db = request_session()
    return db.query(UserModel).all()

