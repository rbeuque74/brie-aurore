from paste.deploy import appconfig
from pylons import config

from brie.config.environment import load_environment

conf = appconfig('config:development.ini', relative_to='.')
load_environment(conf.global_conf, conf.local_conf)

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.camembert_helpers import *

from brie.model import DBSession
from brie.model.camembert import *

#bind = Ldap.connect("uid=roven.gabriel," + ldap_config.username_base_dn, "foobar")
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

nextuid = 30000


base_chambres_dn = "ou=chambres," + ldap_config.base_dn


results = DBSession.query(Room, Interface).filter(Room.idinterface == Interface.idinterface).order_by(Room.name)   

for (room, interface) in results:
    ldap_room = bind.search_first(base_chambres_dn, "(cn=" + room.name + ")")
    print ldap_room.dn

    switch_id = {
        "x-switchInterface" : str(interface.idinterface)
    }

    bind.replace_attr(ldap_room.dn, switch_id) 

    uid_attr = {
        "objectClass" : "uidObject",
        "uid" : str(room.idroom)
    }

    bind.add_attr(ldap_room.dn, uid_attr)

#end for
