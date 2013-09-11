# -*- coding: utf-8 -*-

from __future__ import absolute_import
from brie.config import ldap_config
import ldap
import datetime

class Member(object):
  
    @staticmethod
    def entry_attr(uid, prenom, nom, mail, uid_number):
        return  {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" :uid.encode("utf-8"),
            "cn" : (prenom + " " + nom.upper()).encode("utf-8"),
            "sn" : (nom.upper()).encode("utf-8"),
            "givenName" : (prenom).encode("utf-8"),
            "uidNumber" : str(uid_number),
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
    
    @staticmethod
    def get_by_name(user_session, residence_dn, name):
        return user_session.ldap_bind.search(ldap_config.username_base_dn + residence_dn, "(&(objectClass=pacatnetMember)(cn~=" + name + "))")
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
    def folder_attr():
        return {
            "objectClass" : ["organizationalRole", "top"],
            "cn" : "machines"
        }
    #end def

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
            "cn" : "dhcp",
            "uid" : "machine_membre",
            "dhcpHWAddress" : str("ethernet " + mac),
            "dhcpStatements" : str("fixed-address " + name)
        }
    #end def

    @staticmethod
    def dns_attr(name, ip):
        return {
            "objectClass" : ["top", "organizationalRole", "dlzAbstractRecord", "dlzGenericRecord"],
            "cn" : "dns",
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
            "cn" : "mac_auth",
            "uid" : flat_mac,
            "userPassword" : flat_mac
        }
    #end def

    @staticmethod
    def get_machine_tuples_of_member(user_session, member_dn):
        machine_dn = ldap_config.machine_base_dn + member_dn
        results = user_session.ldap_bind.search(machine_dn, "(objectClass=organizationalRole)", scope = ldap.SCOPE_ONELEVEL)
        machines = list()
        for result in results:
            dhcp = user_session.ldap_bind.search_first(result.dn, "(objectClass=dhcpHost)")
            dns = user_session.ldap_bind.search_first(result.dn, "(objectClass=dlzGenericRecord)")
            if dhcp is not None and dns is not None:
                mac = dhcp.dhcpHWAddress.first().replace("ethernet ", "")
                machines.append(
                    (
                        result.cn.first(), 
                        mac, 
                        dns.dlzData.first() 
                    ) #tuple
                ) 
            #end if
        #end for

        return machines
    #end def

    @staticmethod
    def get_machine_by_id(user_session, member_dn, machine_id):
        machines_dn = ldap_config.machine_base_dn + member_dn
        return user_session.ldap_bind.search_first(machines_dn, "(cn=" + machine_id + ")")
    #end def

    @staticmethod
    def get_dns_by_id(user_session, machine_dn):
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

class Cotisation:

    @staticmethod
    def entry_attr(time, residence, year, user_dn, user_info, amount_paid, valid_months):
        
        return {
            "objectClass" : ["top", "auroreCotisation", "aurorePayment"],
            "cn" : "cotisation-" + time,
            "x-time" : time,
            "description" : "cotisation",
            "x-year" : str(year),
            "x-residence" : residence,
            "x-action-user" : user_dn,
            "x-action-user-info" : user_info,
            "x-amountPaid" : amount_paid,
            "x-validMonth" : valid_months
        }
    #end def

    @staticmethod
    def extra_attr(time, residence, year, user_dn, user_info, description, amount_paid):
        return {
            "objectClass" : ["top", "aurorePayment"],
            "cn" : "extra-" + time,
            "x-time" : time,
            "description" : description,
            "x-year" : str(year),
            "x-residence" : residence,
            "x-action-user" : user_dn,
            "x-action-user-info" : user_info,
            "x-amountPaid" : amount_paid
        }
    #end def

    @staticmethod
    def folder_attr():
        return {
            "objectClass" : ["organizationalRole", "top"],
            "cn" : "cotisations"
        }
    #end def

    @staticmethod
    def year_attr(year):
        return {
            "objectClass" : ["organizationalRole", "top"],
            "cn" : str(year)
        }
    #end def

    @staticmethod
    def cashed_payment_attr():
        return {
            "x-paymentCashed" : "TRUE"
        }
    #end def

    @staticmethod
    def prix_annee(user_session, residence_dn):
        dn = ldap_config.cotisation_annee_base_dn + residence_dn
        return user_session.ldap_bind.search_dn(dn)
    #end def

    @staticmethod
    def prix_mois(user_session, residence_dn):
        dn = ldap_config.cotisation_mois_base_dn + residence_dn
        return user_session.ldap_bind.search_dn(dn)
    #end def

    @staticmethod
    def cotisations_of_member(user_session, member_dn, year):
        return user_session.ldap_bind.search("cn=" + str(year) + "," + ldap_config.cotisation_member_base_dn + member_dn, "(objectClass=auroreCotisation)")
    #end def

    @staticmethod
    def extras_of_member(user_session, member_dn, year):
        return user_session.ldap_bind.search("cn=" + str(year) + "," + ldap_config.cotisation_member_base_dn + member_dn, "(&(objectClass=aurorePayment)(!(objectClass=auroreCotisation)))")
    #end def

    @staticmethod
    def get_all_extras(user_session, residence_dn):
        dn = ldap_config.extra_base_dn + residence_dn
        return user_session.ldap_bind.search(dn, "(objectClass=organizationalRole)", scope = ldap.SCOPE_ONELEVEL)
    #end def

    @staticmethod
    def get_extra_by_name(user_session, residence_dn, name):
        dn = ldap_config.extra_base_dn + residence_dn
        return user_session.ldap_bind.search_first(dn, "(uid=" + name + ")")
    #end def

    @staticmethod
    def get_all_payment_by_year(user_session, residence_dn, year):
        dn = ldap_config.username_base_dn + residence_dn
        return user_session.ldap_bind.search(dn, "(&(objectClass=aurorePayment)(x-year=" + str(year) + "))")
    #end def

    @staticmethod
    def get_all_pending_payments(user_session, residence_dn, year):
        dn = ldap_config.username_base_dn + residence_dn
        return user_session.ldap_bind.search(dn, "(&(&(objectClass=aurorePayment)(x-year=" + str(year) + "))(!(x-paymentCashed=TRUE)))")
    #end def

    @staticmethod
    def get_pending_payments_of_admin(user_session, residence_dn, user_dn, year):
        dn = ldap_config.username_base_dn + residence_dn
        return user_session.ldap_bind.search(dn, "(&(&(&(objectClass=aurorePayment)(x-year=" + str(year) + "))(!(x-paymentCashed=TRUE)))(x-action-user=" + user_dn + "))")
    #end def
    
        

#end class
