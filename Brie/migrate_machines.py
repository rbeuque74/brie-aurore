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


results = DBSession.query(UserPacaterie)

for user in results:
    uid = Translations.to_uid(user.prenom, user.nom)
    print uid

    member = bind.search_first(ldap_config.username_base_dn, "(uid=" + uid + ")")
    

    print member.dn

    machines = DBSession.query(Computer).filter(Computer.iduser == user.iduser)

    machine_id = 1

    for machine in machines:
        print machine_id
        print machine.name
        print machine.mac
        print machine.ip

        machine_dn = "cn=" + str(machine_id) + "," + member.dn

        existant = bind.search_first(machine_dn, "(objectClass=*)")

        if existant is not None:
            bind.delete_entry_subtree(existant.dn)
            print "deleted : " + existant.dn

        print machine_dn
        
        machine_attributes = {
            "objectClass" : ["top", "organizationalRole"],
            "cn" : str(machine_id)
        }        

        bind.add_entry(machine_dn, machine_attributes)

        dhcp_dn = "cn=" + str(machine.name) + "," + machine_dn

        print dhcp_dn

        dhcp_attributes = {
            "objectClass" : ["top", "uidObject", "dhcpHost"],
            "cn" : str(machine.name),
            "uid" : "machine_membre",
            "dhcpHWAddress" : str("ethernet " + machine.mac),
            "dhcpStatements" : str("fixed-address " + machine.name)
        }

        bind.add_entry(dhcp_dn, dhcp_attributes)

        mac_auth_dn = "cn=mac," + machine_dn
        
        print mac_auth_dn

        flat_mac = str(machine.mac).replace(":", "")

        print flat_mac

        mac_auth_attributes = {
            "objectClass" : ["top", "organizationalRole", "simpleSecurityObject", "uidObject"],
            "cn" : "mac",
            "uid" : flat_mac,
            "userPassword" : flat_mac       
        }
        
        bind.add_entry(mac_auth_dn, mac_auth_attributes)

        dns_dn = "dlzHostName=" + machine.name + "," + machine_dn 
        
        print dns_dn

        dns_attributes = {
            "objectClass" : ["top", "dlzAbstractRecord", "dlzGenericRecord"],
            "dlzData" : str(machine.ip),
            "dlzHostName" : str(machine.name),
            "dlzRecordId" : "1",
            "dlzTTL" : "3600",
            "dlzType" : "A"
        }

        bind.add_entry(dns_dn, dns_attributes)
       
        machine_id = 1 + machine_id
 
    #end for machine

    

#end for
