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
    def get_by_uid(user_session, uid):
        return user_session.ldap_bind.search_first(ldap_config.username_base_dn, "(uid=" + uid + ")")
    #end def

#end class

class Room(object):

    @staticmethod
    def get_by_name(user_session, name):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn, "(&" + ldap_config.room_filter + "(cn=" + name + "))")
    #end def

    @staticmethod
    def get_by_uid(user_session, uid):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn, "(&" + ldap_config.room_filter + "(uid=" + uid + "))")
    #end def

    @staticmethod
    def get_by_member_dn(user_session, dn):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn, "(&" + ldap_config.room_filter + "(x-memberIn=" + dn + "))")
    #end def

    @staticmethod
    def get_by_interface(user_session, interface_id):
        return user_session.ldap_bind.search_first(ldap_config.room_base_dn, "(&" + ldap_config.room_filter + "(x-switchInterface=" + str(interface_id) + "))")

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
    def get_machines_of_member(user_session, member_dn):
        results = user_session.ldap_bind.search(member_dn, "(objectClass=organizationalRole)")
        machines = list()
        for result in results:
            dhcp = user_session.ldap_bind.search_first(result.dn, "(objectClass=dhcpHost)")
            dns = user_session.ldap_bind.search_first(result.dn, "(objectClass=dlzGenericRecord)")
            if dhcp is not None and dns is not None:
                mac = dhcp.dhcpHWAddress.first().replace("ethernet ", "")
                machines.append((dhcp.cn.first(), mac, dns.dlzData.first()))
            #end if
        #end for

        return machines
    #end def

#end class

