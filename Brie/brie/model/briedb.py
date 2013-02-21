# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.dialects.postgresql import MACADDR, INET, BOOLEAN, DATE
#from sqlalchemy.orm import relation, backref

from brie.model import DeclarativeBase, metadata, DBSession

class Residences(DeclarativeBase):
    __tablename__ = "residences"

    name = Column(Unicode(128), primary_key=True)

#end class

class Ips(DeclarativeBase):
    __tablename__ = "ips"

    def __init__(self, ip, residence, taken):
        self.ip = ip
        self.residence = residence
        self.taken = taken
    #end

    ip = Column(Unicode(512), primary_key=True)
    residence = Column(Unicode(128), nullable=False)
    taken = Column(BOOLEAN, nullable=False)

#end class
