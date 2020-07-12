from typing import List

from flaskr.lib.database import request_session
from flaskr.lib.models.models import RoomModel


def get_rooms() -> List[RoomModel]:
    db = request_session()

    return db.query(RoomModel).all()


def get_room(room_id: int) -> RoomModel:
    db = request_session()
    return db.query(RoomModel).filter(RoomModel.id == room_id).one_or_none()
