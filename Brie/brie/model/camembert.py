# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.dialects.postgresql import MACADDR, INET, BOOLEAN, DATE
#from sqlalchemy.orm import relation, backref

from brie.model import DeclarativeBase, metadata, DBSession


class Materiel(DeclarativeBase):
    __tablename__ = 'materiel'
    
    #{ Columns
    
    idmateriel = Column(Integer, primary_key=True)

    hostname = Column(Unicode(64))
    manageable = Column(Integer)
    snmpversion = Column(Integer)
    type = Column(Unicode(64))
    ostype = Column(Unicode(512))
    capabilities = Column(Integer)
    datecreation = Column(Integer)
    datelast = Column(Integer)
    
    #}

class Room(DeclarativeBase):
    __tablename__ = "room"
    
    idroom = Column(Integer, primary_key=True)
    
    idinterface = Column(Integer)
    name = Column(Unicode(32))

class Computer(DeclarativeBase):
    __tablename__ = "computer"
    
    idcomp = Column(Integer, primary_key = True)
    
    name = Column(Unicode(32), nullable = False)
    mac = Column(MACADDR, nullable = False)
    iduser = Column(Integer)
    ip = Column(INET)
#end class

class UserPacaterie(DeclarativeBase):
    __tablename__ = "user_pac"

    iduser = Column(Integer, primary_key = True)
    
    nom = Column(Unicode(64), nullable = False)
    prenom = Column(Unicode(64), nullable = False)
    datedeco = Column(DATE, nullable = False)
    mail = Column(Unicode(64))
    certif = Column(BOOLEAN, nullable = False)
    idroom = Column(Integer)
    special_case = Column(BOOLEAN)
    comment = Column(Unicode(64))
#end class

class Ip(DeclarativeBase):
    __tablename__ = "ip"
    
    ip = Column(INET, primary_key = True)
    idmateriel = Column(Integer, primary_key = True)
    main = Column(BOOLEAN)
    datecreation = Column(Integer)
    datelast = Column(Integer)
#end class

class IpUser(DeclarativeBase):
    __tablename__ = "ip_user"

    ip = Column(INET, primary_key = True)
    free = Column(BOOLEAN)
#end class

class Fdb(DeclarativeBase):
    __tablename__ = "fdb"

    idinterface = Column(Integer, primary_key = True)
    vlan = Column(Integer, primary_key = True)
    mac = Column(MACADDR, primary_key = True)
    datefirst = Column(Integer)
    datelast = Column(Integer)
    type = Column(Integer)
#end class

class Action(DeclarativeBase):
    __tablename__ = "action"

    idaction = Column(Integer, primary_key = True)
    idinterface = Column(Integer)
    numaction = Column(Integer, nullable = False)
    option = Column(Unicode(256))
#end class

class ActionLog(DeclarativeBase):
    __tablename__ = "action_log"

    idlog = Column(Integer, primary_key = True)
    loggeduser = Column(Unicode(64), nullable = False)
    logdate =  Column(Integer, nullable = False)
    idinterface = Column(Integer)
    numaction = Column(Integer, nullable = False)
    oldoption = Column(Unicode(256))
    newoption = Column(Unicode(256))
    iduser = Column(Integer)
    amount = Column(Unicode(64))
#end class

class Interface(DeclarativeBase):
    __tablename__ = "interface"

    idinterface = Column(Integer, primary_key = True)
    idmateriel = Column(Integer, nullable = False)
    ifnumber = Column(Integer, nullable = False)
    ifname = Column(Unicode(64))
    ifdescription = Column(Unicode(256)) 
    ifaddress = Column(MACADDR)
    ifspeed = Column(Integer)
    ifadminstatus = Column(Integer)
    ifoperstatus = Column(Integer)
    iftype = Column(Integer)
    ifvlan = Column(Integer)
    ifvoicevlan = Column(Integer)
    ifnativevlan = Column(Integer)
    ifmodule = Column(Integer)
    ifport = Column(Integer)
    portdot1d = Column(Integer)
    portfast = Column(BOOLEAN)
    portsecenable = Column(BOOLEAN)
    portsecstatus = Column(Integer)
    portsecmaxmac = Column(Integer)
    portseccurrmac = Column(Integer)
    portsecviolation = Column(Integer)
    portseclastsrcaddr = Column(MACADDR)
    portsecsticky = Column(BOOLEAN)
#end class
