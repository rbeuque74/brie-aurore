#from paste.deploy import appconfig
#from pylons import config

#from brie.config.environment import load_environment

#conf = appconfig('config:development.ini', relative_to='.')
#load_environment(conf.global_conf, conf.local_conf)

import os
import sys

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.camembert_helpers import *

from brie.model import DBSession
from brie.model.camembert import *

#interface_name = os.environ["NAS_PORT_ID"]
#switch_ip = os.environ["NAS_IP_ADDRESS"]
#mac = os.environ["USERNAME"]

#bind = Ldap.connect("uid=roven.gabriel," + ldap_config.username_base_dn, "foobar")
bind = Ldap.connect("uid=admin,ou=Administrators,ou=TopologyManagement,o=netscaperoot", "t734DSSL61")

rooms_base_dn = "ou=chambres,dc=pacaterie,dc=u-psud,dc=fr"

interface_name = "FastEthernet0/43"
switch_ip = "172.17.24.2"
mac = "000f1f867189"

rooms = bind.search(rooms_base_dn, "(&(&(objectClass=pacaterieRoom)(x-switchInterface=" + interface_name + ")(x-switch=" + switch_ip + ")))")


def roomOrNone(member):
    if member.has("roomNumber"):
        return member.roomNumber.first()
    return None
#end def
    

def isOk():
    for room in rooms:
        print room.get("x-switchInterface").first()
        if room.has("x-memberIn"):
            print room.get("x-memberIn").first()
            associated_member_machine = bind.search_first(room.get("x-memberIn").first(), "(uid=" + mac + ")")
            print associated_member_machine.uid.first()
            return associated_member_machine is not None
        #end if
    #end for

    return False
#end def

ok = isOk()

if ok:
    sys.exit(0)
else:
    sys.exit(1)


