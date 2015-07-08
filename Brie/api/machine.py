# -*- coding: utf-8 -*-

import exception

class Machine(object):
    """Classe modelisant un périphérique connecté au réseau"""

    o = None

    def __init__(self, ldap_object):
        if o is None:
            raise BrieException(u"L'objet LDAP ne peut pas être nul")
        #end if
        if not isinstance(o, LdapEntry):
            raise BrieException(u"L'objet fourni n'est pas un objet LDAP")
        #end if

        self.o = ldap_object
    #end def

    def getDn(self):
        return self.o.dn
    #end def

    def getCn(self):
        return self.o.cn.first()
    #end def

    def getMac(self):
        pass
        #TODO return
    #end def

    def getIP(self):
        pass
        #TODO return
    #end def


