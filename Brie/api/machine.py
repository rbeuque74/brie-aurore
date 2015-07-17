# -*- coding: utf-8 -*-

import exception
import ldap
import re
import membre
from lib.ldap_helper import LdapEntryTree
from lib.brie_helper import registration_current_year

class Machine(object):
    """Classe modelisant un périphérique connecté au réseau"""

    def __init__(self, membre, name, mac, ip):
        #if o is None:
        #    raise BrieException(u"L'objet LDAP ne peut pas être nul")
        ##end if
        #if not isinstance(o, LdapEntry):
        #    raise BrieException(u"L'objet fourni n'est pas un objet LDAP")
        ##end if

        #self.o = ldap_object
        self.membre = membre
        self.o_machine = Machine.entry_attr(name)
        self.o_dns = Machine.dns_attr(name, "")
        self.o_dhcp = Machine.dhcp_attr(name, "")
        # TODO flat mac for auth
        self.o_auth = Machine.auth_attr("")
        self.name = name
        self.setMac(mac)
        self.setIP(ip)
        self.disabled = False
    #end def

    def __repr__(self):
        return "<Machine {0} {1} {2}>".format(self.name, self.mac, self.ip)

    def save(self, brie):
        machine_dn = "cn={0},cn=machines,{1}".format(self.name, self.membre.getDn())
        dns_dn = "cn=dns,{0}".format(machine_dn)
        dhcp_dn = "cn=dhcp,{0}".format(machine_dn)
        auth_dn = "cn=auth,{0}".format(machine_dn)
        try:
            brie.ldapconn().add_entry(machine_dn, self.o_machine)
            self.membre.machines.append(self)
        except ldap.ALREADY_EXISTS:
            brie.ldapconn().save(self.o_machine)
        try:
            brie.ldapconn().add_entry(dns_dn, self.o_dns)
        except ldap.ALREADY_EXISTS:
            brie.ldapconn().save(self.o_dns)
        try:
            brie.ldapconn().add_entry(dhcp_dn, self.o_dhcp)
        except ldap.ALREADY_EXISTS:
            brie.ldapconn().save(self.o_dhcp)
        try:
            brie.ldapconn().add_entry(auth_dn, self.o_auth)
        except ldap.ALREADY_EXISTS:
            brie.ldapconn().save(self.o_auth)
    #end def

    def getDn(self):
        return self.o_machine.dn
    #end def

    def getCn(self):
        return self.name
    #end def

    def getMac(self):
        return self.mac
    #end def

    def setMac(self, mac):
        try:
            self.o_dhcp.get("dhcpHWAddress").replace(self.o_dhcp.get("dhcpHWAddress").first(), "ethernet {0}".format(mac))
        except:
            self.o_dhcp["dhcpHWAddress"] = "ethernet {0}".format(mac)
        p = re.compile(ur'([^:]*):?')
        subst = u"\\1"
        flatmac = re.sub(p, subst, mac)
        try:
            self.o_auth.get("uid").replace(self.o_auth.get("uid").first(), flatmac)
            self.o_auth.get("userPassword").replace(self.o_auth.get("userPassword").first(), flatmac)
        except:
            self.o_auth["uid"] = flatmac
            self.o_auth["userPassword"] = flatmac
        self.mac = mac
    #end def

    def getIP(self):
        return self.ip
    #end def

    def setIP(self, ip):
        try:
            self.o_dns.get("dlzData").replace(self.o_dns.get("dlzData").first(), ip)
        except:
            self.o_dns["dlzData"] = ip
        self.ip = ip
    #end def

    def getDisabled(self):
        return self.disabled
    #end def

    def setDisabled(self, disabled):
        if disabled:
            uid = "machine_membre_disabled"
        else:
            uid = "machine_membre"
        try:
            self.o_dhcp.uid.replace(self.o_dhcp.uid.first(), uid)
        except:
            self.o_dhcp["uid"] = uid
        self.disabled = disabled
    #end def



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
    def get_machine_tuples_of_member(brie, membre):
        machine_dn = "{0}{1}".format(brie.PREFIX_MACHINES_MEMBRE_DN, membre.getDn())
        results = brie.ldapconn().get_childs(machine_dn)
        machine_list = []
        for machine_name in results.childs:
            machine_ldap = results.childs[machine_name]
            if not isinstance(machine_ldap.dns, LdapEntryTree) or not isinstance(machine_ldap.dhcp, LdapEntryTree):
                continue
            machine = Machine.from_ldap_object(membre, machine_ldap)
            machine_list.append(machine)
            #end if
        #end for

        return machine_list
    #end def


    @staticmethod
    def getByName(brie, name, residence):
        if membres is None:
            raise exception.BrieException(u"Impossible de récupérer les membres ou pas de membres correspondant à la requete")
        else:
            output = []
            for membre in membres:
                output.append(Membre.fromLdapObject(membre))
            #end for
        #end if
        return output
    #end def

    @staticmethod
    def get_machine_from_ip(brie, ip, residence):
        machine = brie.ldapconn().search_first(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(dlzData={0})".format(ip))
        if machine is None:
            raise exception.BrieNotFoundException()
        pattern = re.compile(r'^cn=dns,cn=(.+),{0}(.+)'.format(brie.PREFIX_MACHINES_MEMBRE_DN))
        result = re.search(pattern, machine.dn)
        if result is None:
            raise exception.BrieNotFoundException()
        machine_name = result.group(1)
        membre_dn = result.group(2)
        membre_obj = membre.Membre.getByDn(brie, membre_dn)
        machine_dn = "cn={0},{1}{2}".format(machine_name, brie.PREFIX_MACHINES_MEMBRE_DN, membre_dn)
        machine_ldap = brie.ldapconn().get_childs(machine_dn)
        return Machine.from_ldap_object(membre_obj, machine_ldap)
    #end def

    @staticmethod
    def get_machine_from_mac(brie, mac, residence):
        machine = brie.ldapconn().search_first(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(dhcpHWAddress=ethernet {0})".format(mac))
        if machine is None:
            raise exception.BrieNotFoundException()
        pattern = re.compile(r'^cn=dhcp,cn=(.+),{0}(.+)'.format(brie.PREFIX_MACHINES_MEMBRE_DN))
        result = re.search(pattern, machine.dn)
        if result is None:
            raise exception.BrieNotFoundException()
        machine_name = result.group(1)
        membre_dn = result.group(2)
        membre_obj = membre.Membre.getByDn(brie, membre_dn)
        machine_dn = "cn={0},{1}{2}".format(machine_name, brie.PREFIX_MACHINES_MEMBRE_DN, membre_dn)
        machine_ldap = brie.ldapconn().get_childs(machine_dn)
        return Machine.from_ldap_object(membre_obj, machine_ldap)
    #end def

    @classmethod
    def from_ldap_object(cls, o_membre, o_machine):
        if isinstance(o_machine, LdapEntryTree):
            mac = o_machine.dhcp.dhcpHWAddress.first().split(" ")[1]
            machine = Machine(o_membre, o_machine.cn.first(), mac, o_machine.dns.dlzData.first())
            if o_machine.dhcp.uid.first() == "machine_membre_disabled":
                machine.setDisabled(True)
            machine.o_machine = o_machine.value
            machine.o_dns = o_machine.dns.value
            machine.o_dhcp = o_machine.dhcp.value
            try:
                machine.o_auth = o_machine.auth.value
            except Exception:
                pass
            return machine
        #end if
        return None


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
    def get_dns_by_ip(user_session, search_dn, ip):
        return user_session.ldap_bind.search(search_dn, "(dlzData="+ ip +")")
    #end def

    @staticmethod
    def get_dhcps(user_session, machine_dn):
        return user_session.ldap_bind.search(machine_dn, "(objectClass=dhcpHost)")
    #end def

    @staticmethod
    def get_dhcp_by_mac(user_session, member_dn, mac):
        return user_session.ldap_bind.search_first(member_dn, "(dhcpHWAddress=ethernet "+mac+")")
    #end def

    @staticmethod
    def get_dns_by_name(user_session, member_dn, name):
        return user_session.ldap_bind.search_first(member_dn, "(dlzHostName="+name+")")
    #end def

