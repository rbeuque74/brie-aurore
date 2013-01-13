# -*- coding: utf-8 -*-

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.camembert_helpers import *

from brie.model import DBSession
from brie.model.camembert import *
from brie.model.ldap import Machine, Member

class Migration:

    @staticmethod
    def first(target_list, default = None):
        for item in target_list:
            return item
        #end for
        
        return default
    #end def

    @staticmethod
    def import_all(bind, target_id):
        Migration.delete_room_member(bind, target_id)
        Migration.import_member(bind, target_id)
        Migration.import_machines(bind, target_id)
    #end def
 
    @staticmethod
    def delete_room_member(bind, target_id):
        results = DBSession.query(Room).filter(Room.idroom == target_id)

        room = Migration.first(results)
        
        if not room is None:
            ldap_room = bind.search_first(ldap_config.room_base_dn, "(cn=" + room.name + ")")

            print room.name
            member_of = {
                "x-memberIn" : None
            }

            try:
                bind.delete_attr(ldap_room.dn, member_of)
            except:
                pass
            #end try
        #end if
    #end def

    @staticmethod
    def import_member(bind, target_id):
        results = DBSession.query(UserPacaterie, Room).filter(UserPacaterie.idroom == Room.idroom).filter(Room.idroom == target_id)
        
        user, room = Migration.first(results)

        if user is not None and room is not None:
            uid = Translations.to_uid(user.prenom, user.nom)

            member = bind.search_first(ldap_config.username_base_dn, "(uid=" + uid + ")")

            member_dn = ""
            if member is None:
                member_dn = "uid=" + uid + ",ou=2012," + ldap_config.username_base_dn

                print member_dn

                mail = user.mail
                if mail is None:
                    mail = ""
                attributes = Member.entry_attr(uid, user.prenom, user.nom, mail, str(-1))
                bind.add_entry(member_dn, attributes)

            else:
                member_dn = member.dn
            #end if



            ldap_room = bind.search_first(ldap_config.room_base_dn, "(cn=" + room.name + ")")


            new_member_of = {
                "x-memberIn" : str(member_dn)
            }

            bind.replace_attr(ldap_room.dn, new_member_of)
        #end if
    #end def

    @staticmethod
    def import_machines(bind, target_id):
        print target_id

        results = DBSession.query(UserPacaterie, Room).filter(UserPacaterie.idroom == Room.idroom).filter(Room.idroom == target_id)
        user, room = Migration.first(results)
        
        print room.idroom
        print user.idroom

        if user is None: return

        uid = Translations.to_uid(user.prenom, user.nom)

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


            machine_attributes = Machine.entry_attr(machine_id)
            bind.add_entry(machine_dn, machine_attributes)

            dhcp_dn = "cn=" + str(machine.name) + "," + machine_dn
            dhcp_attributes = Machine.dhcp_attr(machine.name, machine.mac)
            bind.add_entry(dhcp_dn, dhcp_attributes)

            mac_auth_dn = "cn=mac," + machine_dn
            flat_mac = str(machine.mac).replace(":", "")

            mac_auth_attributes = Machine.auth_attr(flat_mac)
            bind.add_entry(mac_auth_dn, mac_auth_attributes)

            dns_dn = "dlzHostName=" + machine.name + "," + machine_dn
            dns_attributes = Machine.dns_attr(machine.name, machine.ip)
            bind.add_entry(dns_dn, dns_attributes)

            machine_id = 1 + machine_id

        #end for machine
            
    #end def
                    
#end class
