# -*- coding: utf-8 -*-

import exception
from lib.ldap_helper import LdapEntry
from lib.brie_helper import registration_current_year, to_uid

class Membre(object):
    """Classe modelisant les membres"""

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
        self.setPrenom(prenom)
        self.setNom(nom)
        self.setMail(email)
        self.setMobile(mobile)
        self.setUid(to_uid(prenom, nom))
    #end def

    def __repr__(self):
        return "<Membre ({0}, {1}, {2}, {3})>".format(self.getPrenom().encode("utf-8"), self.getNom().encode("utf-8"), self.getMail().encode("utf-8"), self.getDn().encode("utf-8"))

    def toLdapObject(self):
        return  {
            "objectClass" : ["top", "person", "organizationalPerson", "inetOrgPerson", "pacatnetMember", "pykotaAccount", "posixAccount"],
            "uid" : self.uid.encode("utf-8"),
            "cn" : (self.prenom + " " + self.nom.upper()).encode("utf-8"),
            "sn" : (self.nom.upper()).encode("utf-8"),
            "givenName" : (self.prenom).encode("utf-8"),
            "uidNumber" : u"",
            "mobile" : str(self.mobile),
            "gidNumber" : "10000",
            "homeDirectory" : ("/net/home/" + self.uid).encode("utf-8"),
            "mail" : self.mail.encode("utf-8"),
            "loginShell" : "/usr/bin/zsh".encode("utf-8")
        }
    #end def

    @classmethod
    def fromLdapObject(cls, o):
        if o is None:
            raise BrieException(u"L'objet LDAP ne peut pas être nul")
        #end if
        if not isinstance(o, LdapEntry):
            raise BrieException(u"L'objet fourni n'est pas un objet LDAP")
        #end if

        membre = cls(o.givenName.first(), o.sn.first(), o.mail.first(), o.mobile.first())
        membre.setUid(o.uid.first())
        membre.o = o
        return membre
    #end def

    def save(self, brie):
        if not isinstance(self.o, LdapEntry):
            year = registration_current_year()
            member_dn = "uid={0},ou={1},{2}{3}".format(self.getUid(), str(year), brie.PREFIX_MEMBRES_DN, residence.getDn())
            brie.ldapconn().add_entry(member_dn, self.toLdapObject())
        else:
            brie.ldapconn().save(self.o)
    #end def

    def getDn(self):
        return self.o.dn
    #end def

    def getPrenom(self):
        return self.prenom
    #end def

    def setPrenom(self, prenom):
        try:
            self.o.givenName.replace(self.o.givenName.first(), prenom)
        except:
            self.o['givenName'] = prenom
        self.prenom = prenom
    #end def

    def getNom(self):
        return self.nom
    #end def

    def setNom(self, nom):
        try:
            self.o.sn.replace(self.o.sn.first(), nom)
        except:
            self.o['sn'] = nom
        self.nom = nom
    #end def

    def getCn(self):
        return self.cn
    #end def

    def setCn(self, cn):
        try:
            self.o.cn.replace(self.o.cn.first(), cn)
        except:
            self.o['cn'] = cn
        self.cn = cn
    #end def

    def getUid(self):
        return self.uid
    #end def

    def setUid(self, uid):
        try:
            self.o.uid.replace(self.o.uid.first(), uid)
        except:
            self.o['uid'] = uid
        self.uid = uid
    #end def

    def getUidNumber(self):
        return self.o.uidNumber.first()
    #end def

    def getMobile(self):
        return self.mobile
    #end def

    def setMobile(self, mobile):
        try:
            self.o.mobile.replace(self.o.mobile.first(), mobile)
        except:
            self.o['mobile'] = mobile
        self.mobile = mobile
    #end def

    def getGidNumber(self):
        return self.o.gidNumber.first()
    #end def

    def getHomeDirectory(self):
        return self.o.homeDirectory.first()
    #end def

    def getMail(self):
        return self.mail
    #end def

    def setMail(self, mail):
        try:
            self.o.mail.replace(self.o.mail.first(), mail)
        except:
            self.o['mail'] = mail
        self.mail = mail
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
            return Membre.fromLdapObject(membre)
        #end if
    #end def

    @staticmethod
    def getByUid(brie, membre_uid, residence):
        membre = brie.ldapconn().search_first(brie.PREFIX_MEMBRES_DN + residence.getDn(), u"(uid=" + membre_uid + u")")
        if membre is None:
            raise BrieException(u"Le membre demandé n'existe pas")
        else:
            return Membre.fromLdapObject(membre)
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
                output.append(Membre.fromLdapObject(membre))
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
                output.append(Membre.fromLdapObject(membre))
            #end for
        #end if
        return output
    #end def

    @staticmethod
    def getAll(brie, residence):
        membres = brie.ldapconn().search(brie.PREFIX_MEMBRES_DN + residence.getDn(), u"(objectClass=pacatnetMember)")
        if membres is None:
            raise BrieException(u"Impossible de récupérer les membres ou pas de membres dans la résidence")
        else:
            output = []
            for membre in membres:
                output.append(Membre.fromLdapObject(membre))
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
                output.append(Membre.fromLdapObject(membre))
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
                output.append(Membre.fromLdapObject(membre))
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
                output.append(Membre.fromLdapObject(membre))
            #end for
        #end if
        return output
    #end def


