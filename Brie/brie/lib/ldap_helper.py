# -*- coding: utf-8 -*-
import ldap
#import ldap.modlist as modlist

from brie.config import ldap_config

class Ldap(object):
    __connection = None

    def __init__(self, connection):
        self.__connection = connection
    #end def
    
    @staticmethod
    def connect(dn, password):
        connection = None
#        try:
        connection = ldap.initialize(ldap_config.uri)
        connection.simple_bind_s(dn, password)
#        except:
#        return None
        #end try
       
        if connection is not None:
            return Ldap(connection)
        #end 
 
        return None
    #end def

    def search(self, dn, filter, scope = ldap.SCOPE_SUBTREE):
#        try:
        results = self.__connection.search_s(dn, scope, filter)
#        except:
#        return None
        #end try

        ldap_results = []
        
        for result in results:
            result_dn = result[0]
            attributes = result[1]
            val_dict = dict()

            for attribute in attributes.iteritems():
                name = attribute[0]
                values = attribute[1]
                ldap_value = LdapValue(name, values)
                val_dict[name] = ldap_value
            #end for
            
            ldap_result = LdapResult(result_dn, val_dict)
            ldap_results.append(ldap_result)
        #end for

        return ldap_results
    #end def

    def search_first(self, dn, filter, scope = ldap.SCOPE_SUBTREE):
        results = self.search(dn, filter, scope)
        if results is None: return None

        for result in results:
            return result
        #end for

        return None
    #end def

    def search_dn(self, dn):
        return self.search_first(dn, "(objectClass=*)", ldap.SCOPE_BASE)

    def replace_attr(self, dn, attributes):
        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_REPLACE, attribute[0], attribute[1]))
        #end for
        self.__connection.modify_s(dn, modlist)
    #end def

    def add_attr(self, dn, attributes):
        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_ADD, attribute[0], attribute[1]))
        #end for
        try:
            self.__connection.modify_s(dn, modlist)
        except ldap.TYPE_OR_VALUE_EXISTS:
            pass
    #end def

    def delete_attr(self, dn, attributes):
        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_DELETE, attribute[0], attribute[1]))
        #end for
        #try:
        self.__connection.modify_s(dn, modlist)
        #except:
        #    pass
    #end def

    def add_entry(self, dn, attributes):
        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((attribute[0], attribute[1]))
        #end for

        ##try:
        self.__connection.add_s(dn, modlist)
        ##except:
        ##    pass
    #end def

    def delete_entry(self, dn):
        #try:
        self.__connection.delete_s(dn)
        #except:
        #    pass
    #end def

    def delete_entry_subtree(self, dn):
        entries = self.search(dn, "(objectClass=*)")
        for entry in reversed(entries):
            self.delete_entry(entry.dn)
        #end for
    #end def

    def rename_entry(self, dn, newdn, superior):
        self.__connection.rename_s(dn, newdn, newsuperior= superior)

    def close(self):
        self.__connection.unbind()
            
#end class

class LdapResult(object):
    dn = None    

    def __init__(self, dn, var_dict):
        self.__dict__ = var_dict
        self.dn = dn
    #end def

    def has(self, attribute_name):
        return attribute_name in self.__dict__
    #end def

    def get(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self.__getattr__(name)
        #end if
    #end def

    def __getattr__(self, name):
        return None
    #end def

#end class

class LdapValue(object):
    name = None
    values = []

    def __init__(self, name, values):
        self.values = [value.decode("utf-8") for value in values]
        self.name = name
    #end def

    def first(self, default = None):
        for value in self.values:
            return value
        #end for
        
        return default
    #end def
#end class
    
