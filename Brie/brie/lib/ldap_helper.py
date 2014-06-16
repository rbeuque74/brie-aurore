# -*- coding: utf-8 -*-
import ldap
#import ldap.modlist as modlist

from brie.config import ldap_config
from brie.model.ldap import Groupes


class Groups(object):
    __groups = list()

    def __init__(self, groups):
        self.__groups = groups
    #end def

    def __getattr__(self, name):
        return name in self.__groups
    #end def

    def list(self):
        return list(self.__groups)
    #end def
 
#end class

class User(object):
    ldap_bind = None
    attrs = None
    groups =  None
    residence_dn = None
    
    def __init__(self, ldap_bind, attrs, residence_dn = None):
        self.ldap_bind = ldap_bind
        self.attrs = attrs
        self.residence_dn = residence_dn

        if attrs is not None:
            groups = Groupes.get_by_user_dn(self, residence_dn, self.attrs.dn)

            self.groups = Groups(groups)
        #end if
    #end def
#end class

""" Classe de manipulation de la base ldap """
class Ldap(object):
    __connection = None

    """ Connexion à la base """
    def __init__(self, connection):
        self.__connection = connection
    #end def
    
    """ Methode de connexion à la base de donnée
        dn : dn de connexion
        password : mot de passe
    """
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

    """ Recherche sur la base
        dn : base de recherche
        filter : filtre ldap de recherche
        scope : portée de recherche (SCOPE_SUBTREE, SCOPE_BASE, SCOPE_ONELEVEL)
    """
    def search(self, dn, filter, scope = ldap.SCOPE_SUBTREE):
        dn = Ldap.str_attribute(dn)
        filter = Ldap.str_attribute(filter)

        try:
            results = self.__connection.search_s(dn, scope, filter)
        except ldap.NO_SUCH_OBJECT:
            return []
        #end try

        ldap_results = []
        
        for result in results:
            result_dn = result[0]
            attributes = result[1]
            val_dict = dict()

            for attribute in attributes.iteritems():
                name = attribute[0]
                values = attribute[1]
                ldap_value = LdapAttribute(name, values)
                val_dict[name] = ldap_value
            #end for
            
            ldap_result = LdapEntry(result_dn, val_dict)
            ldap_results.append(ldap_result)
        #end for

        return ldap_results
    #end def

    def get_childs(self, dn, filter = "(objectClass=*)"):
        results = self.search(dn, filter)
        tree = [None, dict()]

        for result in results:
            if result.dn == dn:
                tree[0] = result
            else:
                result_dn = result.dn.replace(dn, "").split(",")
                tree_c = tree
                result_dn.reverse()
                for dn_split in result_dn:
                    if dn_split != "":
                        if not dn_split in tree_c[1]:
                            tree_c[1][dn_split] = [None, dict()]
                            tree_c = tree_c[1][dn_split]
                        else:
                            tree_c = tree_c[1][dn_split]
                        #end if
                    #end if
                #end for
                tree_c[0] = result
            #end if 
        #end for
        return LdapEntryTree(tree[0], tree[1])
    #end def 

    """ Recherche le premier resultat sur la base
        appel la methode "search" en interne
    """
    def search_first(self, dn, filter, scope = ldap.SCOPE_SUBTREE):
        results = self.search(dn, filter, scope)
        if results is None: return None

        for result in results:
            return result
        #end for

        return None
    #end def

    """ Recherche seulement l'element décrit par le dn donnée """
    def search_dn(self, dn):
        return self.search_first(dn, "(objectClass=*)", ldap.SCOPE_BASE)


    @staticmethod
    def str_attributes(attributes):
        def str_value(value):
            if isinstance(value, list):
                return [Ldap.str_attribute(subval) for subval in value]
            #end if

            return Ldap.str_attribute(value)
        #end def

        return dict([ 
            (keyval[0], str_value(keyval[1]))
            for keyval in attributes.iteritems() 
        ])
    #end def

    @staticmethod
    def str_attributes_list(attributes):
        def str_value(value):
            if isinstance(value, list):
                return [Ldap.str_attribute(subval) for subval in value]
            elif isinstance(value, LdapAttribute):
                return [Ldap.str_attribute(subval) for subval in value.all()]
            #end if

            return Ldap.str_attribute(value)
        #end def

        return dict([ 
            (keyval, str_value(attributes[keyval]))
            for keyval in attributes 
        ])
    #end def

    @staticmethod
    def str_attribute(value):
        if isinstance(value, str):
            return value
        elif isinstance(value, unicode):
            return unicode.encode(value, "utf-8")
        #end if
        
        return str(value)
    #end def
        

    """ Remplace les attributs d'un dn donné
        dn : adresse de l'élément
        attributes : dictionnaire d'attributs 
    """
    def replace_attr(self, dn, attributes):
        attributes = Ldap.str_attributes(attributes)

        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_REPLACE, attribute[0], attribute[1]))
        #end for
        self.__connection.modify_s(dn, modlist)
    #end def

    """ Ajouter les attributs d'un dn donné
        dn : addresse de l'élément
        attributes : dictionnaire des nouveaux attributs
    """
    def add_attr(self, dn, attributes):
        attributes = Ldap.str_attributes(attributes)

        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_ADD, attribute[0], attribute[1]))
        #end for
        try:
            self.__connection.modify_s(dn, modlist)
        except ldap.TYPE_OR_VALUE_EXISTS:
            pass
    #end def

    """ Supprime les attributs d'un dn donné 
        dn : adresse de l'élément
        attributes : dictionnaire des attributs à supprimer
    """
    def delete_attr(self, dn, attributes):
        attributes = Ldap.str_attributes(attributes)

        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((ldap.MOD_DELETE, attribute[0], attribute[1]))
        #end for
        #try:
        self.__connection.modify_s(dn, modlist)
        #except:
        #    pass
    #end def

    """ Ajoute un nouvelle élément 
        dn : adresse du nouvelle élément
        attributes : dictionnaire des attributes de l'élément
    """
    def add_entry(self, dn, attributes):
        attributes = Ldap.str_attributes(attributes)

        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((attribute[0], attribute[1]))
        #end for
        
        ##try:
        self.__connection.add_s(dn, modlist)
        ##except:
        ##    pass
    #end def

    """ Clone un élément 
        dn : adresse du nouvelle élément
        attributes : l'élément à cloner
    """
    def clone_entry(self, dn, ldap_entry):
        attributes = Ldap.str_attributes_list(ldap_entry.__dict__)
        del attributes['dn']

        modlist = []
        for attribute in attributes.iteritems():
            modlist.append((attribute[0], attribute[1]))
        #end for
        
        ##try:
        self.__connection.add_s(dn, modlist)
        ##except:
        ##    pass
    #end def

    """ Supprime un élement donné """
    def delete_entry(self, dn):
        #try:
        self.__connection.delete_s(dn)
        #except:
        #    pass
    #end def

    """ Supprime récursivement un élément et ses fils """
    def delete_entry_subtree(self, dn):
        entries = self.search(dn, "(objectClass=*)")
        for entry in reversed(entries):
            self.delete_entry(entry.dn)
        #end for
    #end def

    """ Renomme un élément """
    def rename_entry(self, dn, newdn, superior):
        self.__connection.rename_s(dn, newdn, newsuperior= superior)

    """ Sauvegarde en base une valeur l'élément donné """
    def save(self, ldap_entry):
        modlist = []

        for global_deletion in ldap_entry._deletions:
            modlist.append((ldap.MOD_DELETE, global_deletion, None))
        #end for
        ldap_entry._deletions = []

        ldap_attributes = (
            attribute 
            for attribute in ldap_entry.__dict__.itervalues()
            if isinstance(attribute, LdapAttribute)
        )

        for ldap_attribute in ldap_attributes:
            print "name : " + ldap_attribute.name
            print "values : " + str(ldap_attribute.values)
            print "deletions : " + str(ldap_attribute._deletions)
            print "additions : " + str(ldap_attribute._additions)
            print  "modified : " + str(ldap_attribute._modified)
            
            if ldap_attribute._deletions != []:
                str_values = [str(value) for value in ldap_attribute._deletions]
                modlist.append((ldap.MOD_DELETE, ldap_attribute.name, str_values))
                ldap_attribute._deletions = []
            #end if

            if ldap_attribute._additions != []:
                str_values = [str(value) for value in ldap_attribute._additions]
                modlist.append((ldap.MOD_ADD, ldap_attribute.name, str_values))
                ldap_attribute._additions = []
            #end if

            if ldap_attribute._modified:
                str_values = [str(value) for value in ldap_attribute.values]
                modlist.append((ldap.MOD_REPLACE, ldap_attribute.name, str_values))
                ldap_attribute._modified = False
            #end for


        #end for

        print "dn : " +  ldap_entry.dn
        print "modlist : " + str(modlist)
        if modlist != []:
            self.__connection.modify_s(ldap_entry.dn, modlist)

        # On recharge l'entrée après la sauvegarde
        entry_reloaded = self.search_dn(ldap_entry.dn)
        ldap_entry.__dict__ = entry_reloaded.__dict__
    #end def

    """ Ferme la connexion à la base """
    def close(self):
        self.__connection.unbind()
            
#end class

""" Classe représentant un élément ldap """
class LdapEntry(object):
    dn = None    

    _deletions = []

    def __init__(self, dn, var_dict):
        self.__dict__ = var_dict
        self.dn = dn.decode("utf-8")
    #end def

    """ Retourne si un attribut existe sur cette élément """
    def has(self, attribute_name):
        return attribute_name in self.__dict__
    #end def

    """ Retourne la valeur d'un attribut donné """
    def get(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self.__getattr__(name)
        #end if
    #end def

    def __getattr__(self, name):
        attr = LdapAttribute(name, [])
        self.__dict__[name] = attr
        
        return attr
    #end def

    """ Ajoute un attribut """
    def add(self, name, value = None):
        if self.has(name):
            if value is not None:
                value = self.get(name)
                value.add(value)
            #end if
        else:
            values = []
            if value is not None:
                values = [value]
            #end if

            
            self.__dict__[name] = LdapAttribute(name, values)
            self.__dict__[name]._additions = values
        #end if
    #end def

    """ Supprime un attribut """
    def delete(self, name, value = None):
        if self.has(name):
            if value is not None:
                value = self.get(name)
                value.delete(value)
            else:
                del self.__dict__[name]
                self._deletions.append(name)
            #end if
        #end if
    #end def

#end class


""" Classe représentant la valeur d'un attribut """
class LdapAttribute(object):
    name = None
    values = None

    _deletions = None
    _additions = None
    _modified = False

    def __init__(self, name, values):
        self.values = [value.decode("utf-8") for value in values]
        self.name = name

        self._deletions = list()
        self._additions = list()
    #end def

    """ Retourne la première valeur de cet attribut """
    def first(self, default = None):
        for value in self.values:
            return unicode(value)
        #end for
        
        if default is None:
            return None        

        return unicode(default)
    #end def

    """ Retourne toutes les valeurs de cet attribut """
    def all(self):
        return self.values
    #end def

    """ Ajoute une valeur à cet attribut
        Note : la valeur ne sera pas ajouté si elle existe déjà 
    """
    def add(self, value):
        if not value in self.values:
            self.values.append(value)
            self._additions.append(value)
        #end if
    #end def 

    """ Supprime une valeur de cet attribut """
    def delete(self, value):    
        if value in self.values:
            self.values = [old for old in self.values if old != value]

            # Si il vient d'être ajouté, on l'enleve simplement 
            # de la queue d'ajout
            # sinon on l'ajoute dans la queue de suppression
            if value in self._additions:
                self._additions = [old for old in self._additions if old != value]
            else:
                self._deletions.append(value)
            #end if
        #end if
    #end def

    """ Modifie une valeur de cet attribut
        si la valeur est nulle, modifie la première valeur
    """
    def replace(self, old, new):
        if old == new:
            return
    
        # Fonction usuelle de remplacement
        def replace(current):
            if current == old:
                return new
            #end if

            return current
        #end def

        # Si la valeur modifié existe déjà
        # l'ancienne valeur n'est que supprimée
        if new in self.values:
            self.delete(old)
        elif self.values == []:
            self.add(new)
        else:
            self.values = [replace(value) for value in self.values]

            # Si la valeur modifié vient d'être ajouté, 
            # elle est modifié dans la queue d'addition
            self._additions = [replace(value) for value in self._additions]
        
            self._modified = True
        #end if

    #end def

#end class
   
class LdapEntryTree(LdapEntry):
    childs = None
    val = None

    def __init__(self, val, childs):
        self.val = val
        self.__dict__ = val.__dict__
        self.__dict__['value'] = val
        self.childs = dict()
        if len(childs) > 0:
            for key,child in childs.iteritems():
                key = key.split("=")[1]
                self.childs[key] = LdapEntryTree(child[0], child[1])
                self.__dict__[key] = self.childs[key]
            #end for
        #end if
    #end def

    def __getattr__(self, name):
        attr = LdapAttribute(name, [])
        self.__dict__[name] = attr
        
        return attr
    #end def

#end class 
