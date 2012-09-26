from bradmin import Base, DBSession

from sqlalchemy import (
    Column,
    Integer,
    Text,    
    DateTime,
    Float,
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import logging
log = logging.getLogger(__name__)

def init_db():
    session = DBSession()
    try:
        session.query(User).filter_by(username = "admin").one()
    except NoResultFound:
        admin = User("admin", "default")
        session.add(admin)
        session.commit()
    
class User(Base):
    __tablename__ = 'users'
    username = Column(Text, primary_key=True)
    password = Column(Text)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
