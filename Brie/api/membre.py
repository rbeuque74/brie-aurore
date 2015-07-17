# -*- coding: utf-8 -*-

import exception
import ldap
import machine
from lib.ldap_helper import LdapEntry, LdapEntryTree
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
            "uidNumber" : str(-1),
            "mobile" : u"",
            "gidNumber" : "10000",
            "homeDirectory" : u"",
            "mail" : u"",
            "loginShell" : "/bin/bash",
        }
        self.o_folder_machine = machine.Machine.folder_attr()
        self.prenom = u""
        self.nom = u""
        self.setPrenom(prenom)
        self.setNom(nom)
        self.setMail(email)
        self.setMobile(mobile)
        self.setUid(to_uid(prenom, nom))
        self.machines = []
    #end def

    def __repr__(self):
        return "<Membre ({0}, {1}, {2}, {3})>".format(self.getPrenom().encode("utf-8"), self.getNom().encode("utf-8"), self.getMail().encode("utf-8"), self.getDn().encode("utf-8"))


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
        membre.setComment(o.get("x-comment").first())
        membre.o = o
        return membre
    #end def

    def save(self, brie):
        if not isinstance(self.o, LdapEntry):
            year = registration_current_year()
            member_dn = "uid={0},ou={1},{2}{3}".format(self.getUid(), str(year), brie.PREFIX_MEMBRES_DN, brie.residence.getDn())
            brie.ldapconn().add_entry(member_dn, self.o)
        else:
            brie.ldapconn().save(self.o)
            member_dn = self.getDn()
        try:
            machine_dn = "{0}{1}".format(brie.PREFIX_MACHINES_MEMBRE_DN, member_dn)
            brie.ldapconn().add_entry(machine_dn, self.o_folder_machine)
        except ldap.ALREADY_EXISTS:
            pass
    #end def

    def getDn(self):
        return self.o.dn
    #end def

    def getPrenom(self):
        return self.prenom
    #end def

    def setPrenom(self, prenom):
        prenom = prenom.encode("utf-8")
        try:
            self.o.givenName.replace(self.o.givenName.first(), prenom)
            self.o.cn.replace(self.o.cn.first(), "{0} {1}".format(prenom, self.nom))
        except:
            self.o['givenName'] = prenom
            self.o['cn'] = "{0} {1}".format(prenom, self.nom)
        self.prenom = prenom
        self.cn = "{0} {1}".format(prenom, self.nom)
    #end def

    def getNom(self):
        return self.nom
    #end def

    def setNom(self, nom):
        nom = nom.encode("utf-8")
        try:
            self.o.sn.replace(self.o.sn.first(), nom)
            self.o.cn.replace(self.o.cn.first(), "{0} {1}".format(self.prenom, nom))
        except:
            self.o['sn'] = nom
            self.o['cn'] = "{0} {1}".format(self.prenom, nom)
        self.nom = nom
        self.cn = "{0} {1}".format(self.prenom, nom)
    #end def

    def getCn(self):
        return self.cn
    #end def

    def setCn(self, cn):
        cn = cn.encode("utf-8")
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

    def getComment(self):
        return self.comment
    #end def

    def setComment(self, comment):
        try:
            self.o.get("x-comment").replace(self.o.get("x-comment").first(), comment)
        except:
            self.o["x-comment"] = comment
        self.comment = comment
    #end def

    def getLoginShell(self):
        return self.o.loginShell.first()
    #end def

    def getChilds(self, brie):
        test = brie.ldapconn().get_childs(self.getDn())
        from pprint import pprint
        pprint(test)
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


    def get_machines(self, brie):
        try:
            self.getDn()
        except:
            raise BrieException("Membre not commited yet!")
        membre = brie.ldapconn().get_childs(self.getDn())
        if membre is None:
            raise BrieException(u"Le membre demandé n'existe pas")
        else:
            self.machines = []
            for machine_name in membre.machines.childs:
                machine_ldap = membre.machines.childs[machine_name]
                if not isinstance(machine_ldap.dns, LdapEntryTree) or not isinstance(machine_ldap.dhcp, LdapEntryTree):
                    continue
                #end if
                machine_obj = machine.Machine.from_ldap_object(self, machine_ldap)
                self.machines.append(machine_obj)
            #end for
        #end if

    @staticmethod
    def getFullByUid(brie, membre_uid, residence):
        m = Membre.getByUid(brie, membre_uid, residence)
        if m is None:
            return None
        membre = brie.ldapconn().get_childs(m.getDn())
        if membre is None:
            raise BrieException(u"Le membre demandé n'existe pas")
        else:
            for machine_name in membre.machines.childs:
                machine_ldap = membre.machines.childs[machine_name]
                if not isinstance(machine_ldap.dns, LdapEntryTree) or not isinstance(machine_ldap.dhcp, LdapEntryTree):
                    continue
                #end if
                machine_obj = machine.Machine.from_ldap_object(m, machine_ldap)
                m.machines.append(machine_obj)
            return m
            #end for
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




