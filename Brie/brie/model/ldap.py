# -*- coding: utf-8 -*-

from brie.config import ldap_config

class Member(object):
  
    @staticmethod
    def entry_attr(uid, prenom, nom, mail, uid_number):
        return  {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" :uid.encode("utf-8"),
            "cn" : (prenom + " " + nom.upper()).encode("utf-8"),
            "sn" : (nom.upper()).encode("utf-8"),
            "givenName" : (prenom).encode("utf-8"),
            "uidNumber" : uid_number,
            "gidNumber" : "10000",
            "homeDirectory" : ("/net/home/" + uid).encode("utf-8"),
            "mail" : mail.encode("utf-8"),
            "loginShell" : "/usr/bin/zsh".encode("utf-8")
        }
    #end def

 
    @staticmethod
    def get_by_dn(user_session, dn):
        return user_session.ldap_bind.search_dn(dn)
    #end def
 
    @staticmethod
    def get_by_uid(user_session, residence_dn, uid):
        return user_session.ldap_bind.search_first(ldap_config.username_base_dn + residence_dn, "(uid=" + uid + ")")
    #end def

    @staticmethod
    def get_all(user_session, residence_dn):
        return user_session.ldap_bind.search(ldap_config.username_base_dn + residence_dn, "(objectClass=pacatnetMember)")
    #end def

#end class

class Room(object):

    @staticmethod
    def memberIn_attr(member_dn):
        return {
            "x-memberIn" : str(member_dn)
        }
    #end def


    @staticmethod
    def get_by_name(user_session, residence_dn, name):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn + residence_dn, "(&(objectClass=pacaterieRoom)(cn=" + name + "))")
    #end def

    @staticmethod
    def get_by_uid(user_session, residence_dn, uid):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn + residence_dn, "(&(objectClass=pacaterieRoom)(uid=" + uid + "))")
    #end def

    @staticmethod
    def get_by_member_dn(user_session, residence_dn, dn):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn + residence_dn, "(&(objectClass=pacaterieRoom)(x-memberIn=" + dn + "))")
    #end def

    @staticmethod
    def get_areas(user_session, residence_dn):
        return user_session.ldap_bind.search(ldap_config.room_base_dn + residence_dn, "(objectClass=pacaterieArea)")
    #end def

    @staticmethod
    def get_floors(user_session, area_dn):
        return user_session.ldap_bind.search(area_dn, "(objectClass=pacaterieFloor)")
    #end def

    @staticmethod
    def get_rooms_of_floor(user_session, floor_dn):
        return user_session.ldap_bind.search(floor_dn, "(objectClass=pacaterieRoom)")
    #end def

    @staticmethod
    def get_rooms(user_session, residence_dn):
        return user_session.ldap_bind.search(ldap_config.room_base_dn + residence_dn, "(objectClass=pacaterieRoom)")
    #end def

#end class


class Wifi(object):
    
    @staticmethod
    def entry_attr(password):
        return {
            "objectClass" : ["top", "organizationalRole", "simpleSecurityObject"],
            "cn" : "wifi",
            "userPassword" : str(password)
        }
    #end def

    @staticmethod
    def password_attr(password):
        return {
            "userPassword" : str(password)
        }
    #end def

    @staticmethod
    def get_by_dn(user_session, dn):
        return user_session.ldap_bind.search_dn("cn=wifi," + dn)
    #end def

#end class

class Machine(object):

    @staticmethod
    def entry_attr(machine_id):
        return {
            "objectClass" : ["top", "organizationalRole"],
            "cn" : str(machine_id)
        }
    #end def

    @staticmethod
    def dhcp_attr(name, mac):
        return {
            "objectClass" : ["top", "uidObject", "dhcpHost"],
            "cn" : str(name),
            "uid" : "machine_membre",
            "dhcpHWAddress" : str("ethernet " + mac),
            "dhcpStatements" : str("fixed-address " + name)
        }
    #end def

    @staticmethod
    def dns_attr(name, ip):
        return {
            "objectClass" : ["top", "dlzAbstractRecord", "dlzGenericRecord"],
            "dlzData" : str(ip),
            "dlzHostName" : str(name),
            "dlzRecordId" : "1",
            "dlzTTL" : "3600",
            "dlzType" : "A"
        }
    #end def

    @staticmethod
    def auth_attr(flat_mac):
        return {
            "objectClass" : ["top", "organizationalRole", "simpleSecurityObject", "uidObject"],
            "cn" : "mac",
            "uid" : flat_mac,
            "userPassword" : flat_mac
        }
    #end def

    @staticmethod
    def get_machine_tuples_of_member(user_session, member_dn):
        results = user_session.ldap_bind.search(member_dn, "(objectClass=organizationalRole)")
        machines = list()
        for result in results:
            dhcp = user_session.ldap_bind.search_first(result.dn, "(objectClass=dhcpHost)")
            dns = user_session.ldap_bind.search_first(result.dn, "(objectClass=dlzGenericRecord)")
            if dhcp is not None and dns is not None:
                mac = dhcp.dhcpHWAddress.first().replace("ethernet ", "")
                machines.append(
                    (
                        dhcp.cn.first(), 
                        mac, 
                        dns.dlzData.first(), 
                        result.cn.first()
                    ) #tuple
                ) 
            #end if
        #end for

        return machines
    #end def

    @staticmethod
    def get_machine_by_id(user_session, member_dn, machine_id):
        return user_session.ldap_bind.search_first(member_dn, "(cn=" + machine_id + ")")
    #end def

    @staticmethod
    def get_dns_by_id(user_session, machine_dn, machine_id):
        return user_session.ldap_bind.search_first(machine_dn, "(objectClass=dlzAbstractRecord)")
    #end def

    @staticmethod
    def get_dhcp_by_mac(user_session, residence_dn, mac):
        return user_session.ldap_bind.search_first(residence_dn, "(dhcpHWAddress=ethernet "+mac+")")
    #end def

    @staticmethod
    def get_dns_by_name(user_session, residence_dn, name):
        return user_session.ldap_bind.search_first(residence_dn, "(dlzHostName="+name+")")
    #end def
#end class

class Groupes(object):
    
    @staticmethod
    def get_by_user_dn(user_session, residence_dn, user_dn):
        results = user_session.ldap_bind.search(ldap_config.group_base_dn + residence_dn, "(&(objectClass=groupOfUniqueNames)(uniqueMember=" + user_dn + "))")
        
        groups = list()


        for item in results:
            groups.append(item.cn.first())
        #end for

        return groups
    #end def

    @staticmethod
    def get_by_cn(user_session, residence_dn, cn):
        results = user_session.ldap_bind.search_first(ldap_config.group_base_dn + residence_dn, "(&(objectClass=groupOfUniqueNames)(cn=" + cn + "))")

        return results
    #end def

    @staticmethod
    def get_all(user_session, residence_dn):
        results = user_session.ldap_bind.search(ldap_config.group_base_dn + residence_dn, "(objectClass=groupOfUniqueNames)")

        return results
    #end def

    @staticmethod
    def unique_member_attr(member_dn):
        return {
            "uniqueMember" : str(member_dn)
        }
    #end def

#end class

class IpReservation:
    
    @staticmethod
    def entry_attr(ip):
        return {
            "objectClass" : ["top", "auroreIpReservation"],
            "cn" : str(ip)
        }
    #end def

    @staticmethod
    def taken_attr(description):
        return {
            "x-taken" : str(description)
        }
    #end def

    @staticmethod
    def get_first_free(user_session, residence_dn):
        results  = user_session.ldap_bind.search_first(ldap_config.ip_reservation_base_dn + residence_dn, "(&(objectClass=auroreIpReservation)(!(x-taken=*)))")

        return results
    #end def

    @staticmethod
    def get_ip(user_session, residence_dn, ip):
        results  = user_session.ldap_bind.search_first(ldap_config.ip_reservation_base_dn + residence_dn, "(&(objectClass=auroreIpReservation)(cn=" + ip + "))")
        
        return results
    #end def
        
#end class

class Plugins:
    
    @staticmethod
    def get_by_name(user_session, residence_dn, plugin_name):
        return user_session.ldap_bind.search_first(ldap_config.plugins_base_dn + residence_dn, "(cn=" + plugin_name + ")")
    #end def

#end class
