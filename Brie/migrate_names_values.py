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


results = DBSession.query(Room)

for room in results:
    ldap_room = bind.search_first(base_chambres_dn, "(cn=" + room.name + ")")
    member_of = {
        "x-memberIn" : None
    }
    
    try:
        bind.delete_attr(ldap_room.dn, member_of)
        print "deleted " + ldap_room.dn
    except:
        pass
    #end try

#end for
    

results = DBSession.query(UserPacaterie, Room).filter(UserPacaterie.idroom == Room.idroom)

for (user, room) in results:
    uid = Translations.to_uid(user.prenom, user.nom)
    print uid

    member = bind.search_first(ldap_config.username_base_dn, "(uid=" + uid + ")")
    
    print room.name

    member_dn = ""    

    if member is None:
        member_dn = "uid=" + uid + ",ou=2012," + ldap_config.username_base_dn

        mail = user.mail
        if mail is None:
            mail = ""
        attributes = {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" :(uid).encode("utf-8"),
            "cn" : (user.prenom + " " + user.nom.upper()).encode("utf-8"),
            "sn" : (user.nom.upper()).encode("utf-8"),
            "givenName" : (user.prenom).encode("utf-8"),
            "uidNumber" : str(-1),
            "gidNumber" : "10000",
            "homeDirectory" : ("/net/home/" + uid).encode("utf-8"),
            "mail" : (mail).encode("utf-8"),
            "loginShell" : "/usr/bin/zsh".encode("utf-8")
        }

        bind.add_entry(member_dn, attributes)

    else:
        member_dn = member.dn
    #end if
    


    ldap_room = bind.search_first(base_chambres_dn, "(cn=" + room.name + ")")
    
    print ldap_room.dn
    print member_dn

    new_member_of = {
        "x-memberIn" : str(member_dn)
    }

    bind.replace_attr(ldap_room.dn, new_member_of)
#end for
