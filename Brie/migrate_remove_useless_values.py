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

#bind = Ldap.connect("uid=roven.gabriel,ou=2011," + ldap_config.username_base_dn, "foobar")
bind = Ldap.connect("uid=admin,ou=Administrators,ou=TopologyManagement,o=netscaperoot", "t734DSSL61")

members = bind.search(ldap_config.username_base_dn, "(&(ou:dn:=2011)(objectClass=pacatnetMember))")

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

def add(uid, user, room_dn, nextuid):
    user_dn = "uid=" + uid + "," + ldap_config.username_base_dn
    mail = user.mail
    if mail is None:
        mail = ""
    attributes = {
        "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
        "uid" :(uid).encode("utf-8"),
        "cn" : (user.prenom + " " + user.nom.upper()).encode("utf-8"),
        "sn" : (user.nom.upper()).encode("utf-8"),
        "givenName" : (user.prenom).encode("utf-8"),
        "uidNumber" : str(nextuid),
        "gidNumber" : "10000",
        "homeDirectory" : ("/net/home/" + uid).encode("utf-8"),
        "mail" : (mail).encode("utf-8"),
        "x-room" : (room_dn).encode("utf-8"),
        "loginShell" : "/usr/bin/zsh".encode("utf-8")
    }
    
    bind.add_entry(user_dn, attributes)
    
#end def

filestream = open("people_to_change.txt", "r")

for line in filestream:
    uid = line.strip()
    print "++" + uid + "++"
    print "ou=2010," + ldap_config.username_base_dn
    result = bind.search_first(ldap_config.username_base_dn, "(uid=" + uid + ")")
    bind.rename_entry(result.dn, "uid=" + result.uid.first(), "ou=2010," + ldap_config.username_base_dn)

#end for
    
    
