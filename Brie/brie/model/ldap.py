# -*- coding: utf-8 -*-

from brie.config import ldap_config

class Member(object):
   
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
            "userPassword" : password
        }
    #end def

    @staticmethod
    def get_by_dn(user_session, dn):
        return user_session.ldap_bind.search_first("cn=wifi," + dn)
    #end def

#end class
