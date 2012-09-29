from paste.deploy import appconfig
from pylons import config

from brie.config.environment import load_environment

conf = appconfig('config:development.ini', relative_to='.')
load_environment(conf.global_conf, conf.local_conf)

from brie.config import ldap_config
from brie.lib.ldap_helper import *

from brie.model import DBSession
from brie.model.camembert import *

import socket

#bind = Ldap.connect("uid=roven.gabriel,ou=2010," + ldap_config.username_base_dn, "foobar")
bind = Ldap.connect("uid=admin,ou=Administrators,ou=TopologyManagement,o=netscaperoot", "t734DSSL61")

members = bind.search(ldap_config.username_base_dn, "(objectClass=pacatnetMember)")

def roomOrNone(member):
    if member.has("roomNumber"):
        return member.roomNumber.first()
    return None
#end def

def first(items):
    for item in items:
        return item
    
    return None
#end def

def area(room_number):
    floor_number = room_number % 100
    
    if floor_number <= 33: 
        return "sud"
    else:
        return "nord"
    #end if
#end def

results = DBSession.query(Room, Materiel, Interface).filter(Room.idinterface == Interface.idinterface).filter(Interface.idmateriel == Materiel.idmateriel)

for room, materiel, interface in results:
    aile = area(room.idroom)
    etage = str(room.idroom / 100)
    
    base_chambres_dn = "ou=chambres," + ldap_config.base_dn
    
    other_dn = "cn=" + etage + ",cn=" + aile + "," + base_chambres_dn
    
    full_dn = "cn=" + room.name + "," + other_dn

    print room

    switch_ip = socket.gethostbyname(str(materiel.hostname))

    
    attributes = {
        "objectClass" : "pacaterieRoom",
        "cn" : str(room.name),
        "x-switch" : str(switch_ip),
        "x-switchInterface" : str(interface.ifname)
    }
    

    print str(room.idinterface)
    
    print full_dn
    try: 
        bind.replace_attr(full_dn, attributes)
    except ldap.NO_SUCH_OBJECT:
        bind.add_entry(full_dn, attributes)
#    print attributes
#end for
    
    
