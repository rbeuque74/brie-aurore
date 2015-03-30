# -*- coding: utf-8 -*-

import exception 

class Membre(object):
    """Classe modelisant les membres"""

    o = None
    
    def __init__(self, prenom, nom, email, mobile):
        self.o =  {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" : u"",
            "cn" : u"",
            "sn" : u"",
            "givenName" : u"",
            "uidNumber" : u"",
            "mobile" : u"",
            "gidNumber" : "10000",
            "homeDirectory" : u"",
            "mail" : u"",
            "loginShell" : "/bin/bash"
        }
    #end def

    def toLdapObject(self):
        return  {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" :uid.encode("utf-8"),
            "cn" : (prenom + " " + nom.upper()).encode("utf-8"),
            "sn" : (nom.upper()).encode("utf-8"),
            "givenName" : (prenom).encode("utf-8"),
            "uidNumber" : str(uid_number),
            "mobile" : str(phone),
            "gidNumber" : "10000",
            "homeDirectory" : ("/net/home/" + uid).encode("utf-8"),
            "mail" : mail.encode("utf-8"),
            "loginShell" : "/usr/bin/zsh".encode("utf-8")
        }
    #end def
    
    @classmethod
    def fromLdapObject(cls, o):
        membre = cls(o.cn.first())
        
        if o is None:
            raise BrieException(u"L'objet LDAP ne peut pas être nul")
        #end if
        if not isinstance(o, LdapEntry):
            raise BrieException(u"L'objet fourni n'est pas un objet LDAP")
        #end if

        membre.o = ldap_object
        return residence
    #end def

    def getDn(self):
        return self.o.dn
    #end def

    def getPrenom(self):
        return self.o.givenName.first()
    #end def
    
    def getNom(self):
        return self.o.sn.first()
    #end def

    def getCn(self):
        return self.o.cn.first()
    #end def

    def getUid(self):
        return self.o.uid.first()
    #end def

    def getUidNumber(self):
        return self.o.uidNumber.first()
    #end def

    def getMobile(self):
        return self.o.mobile.first()
    #end def

    def getGidNumber(self):
        return self.o.gidNumber.first()
    #end def

    def getHomeDirectory(self):
        return self.o.homeDirectory.first()
    #end def

    def getMail(self):
        return self.o.mail.first()
    #end def

    def getLoginShell(self):
        return self.o.loginShell.first()
    #end def

    @staticmethod
    def getByDn(brie, dn):
        membre = brie.ldapconn().search_dn(dn)
        if membre is None:
            raise BrieException(u"Le membre demandé n'existe pas")
        else:
            return Membre(membre)
        #end if
    #end def

    @staticmethod
    def getByUid(brie, membre_uid, residence):
        membre = brie.ldapconn().search_first(brie.PREFIX_MEMBRES_DN + residence.getDn(), u"(uid=" + membre_uid + u")")
        if membre is None:
            raise BrieException(u"Le membre demandé n'existe pas")
        else:
            return Membre(membre)
        #end if
    #end def

    @staticmethod
    def getByName(brie, name, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(&(objectClass=pacatnetMember)(cn~=" + name + "))")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres correspondant à la requete")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def
    
    @staticmethod
    def getByEmail(brie, email, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(&(objectClass=pacatnetMember)(mail=" + email + "))")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres correspondant à la requête")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def

    @staticmethod
    def getAll(brie, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), u"(objectClass=pacatnetMember")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres dans la résidence")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def
    

    @staticmethod
    def getNonResponsableReseau(brie, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(&(objectClass=pacatnetMember)(!(memberof=cn=responsablereseau,ou=groupes,"+residence.getDn()+")))")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres dans la résidence")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def
    
    @staticmethod
    def getResponsableReseau(brie, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), "(&(objectClass=pacatnetMember)(memberof=cn=responsablereseau,ou=groupes,"+residence.getDn()+"))")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les responsables réseaux ou pas de responsables réseaux dans la résidence")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def

    @staticmethod
    def getAllWithInfos(brie, residence):
        membres = brie.ldapconn().get_childs(brie.PREFIX_MEMBRES_DN + residence.getDn())
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres dans la résidence")
        else:
            output = []
            for membre in membres:
                output.append(Membre(membre))
            #end for
        #end if
        return output
    #end def
    

