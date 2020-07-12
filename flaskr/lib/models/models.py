from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import relationship, deferred

from flaskr.lib.database import OrmModelBase
from flaskr.lib.database import request_session
from datetime import datetime
import bcrypt


class UserModel(OrmModelBase):
    """
    Database usermodel also used to login, and store money
    """
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer(), primary_key=True, autoincrement=True)

    username = Column(String(), unique=True, nullable=False)
    password = deferred(Column(LargeBinary(), nullable=False))

    balance = Column(Integer(), unique=False, nullable=False, default=1000)

    def __init__(self, username: str, password: str = None):
        self.username = username
        if password is not None:
            self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password)

    def pay(self, cost):
        """
        Tries to pay the cost with the current balance
        If it can do so, returns True, otherwise False
        """

        if self.balance > cost:
            self.balance -= cost
            db = request_session()
            db.commit()
            return True
        return False


class RoomModel(OrmModelBase):
    """
    Stores information about a room in which poker games are being played
    """
    __tablename__ = "room"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)

    author_id = Column(Integer(), ForeignKey("user.id"), nullable=False)
    author = relationship("UserModel")

    created = Column(DateTime(), nullable=False, default=datetime.now())
    temp_password = Column(String(), nullable=False)

    def __init__(self, name: str, author: UserModel, temp_password: str = ""):
        self.temp_password = temp_password
        self.name = name
        self.author_id = author.id
