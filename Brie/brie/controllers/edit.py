# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter

from datetime import datetime
import uuid
import re

#root = tg.config['application_root_module'].RootController

""" Controller d'edition de details de membres, chambres""" 
class EditController(AuthenticatedBaseController):
    require_group = groups_enum.admin

    """ Controller show qu'on réutilise pour gérer l'affichage """
    show = None

    """ Controller fils wifi pour gérer le wifi """
    wifi = None

    """ Controller fils room pour gérer les chambres """
    room = None

    """ Controller fils de gestion des machines """
    machine = None

    member = None

    def __init__(self, new_show):
        self.show = new_show
        self.wifi = WifiRestController(new_show)
        self.machine = MachineController()
        self.room = RoomController(new_show)
        self.member = MemberModificationController()

    
    """ Affiche les détails éditables de la chambre """
    @expose("brie.templates.edit.room")
    def room(self, residence, room_id):
        return self.show.room(residence, room_id)
    #end def

#end class

class MemberModificationController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Affiche les détails éditables du membre et de la chambre """
    @expose("brie.templates.edit.member")
    def get(self, residence, uid):
        
        residence_dn = Residences.get_dn_by_name(self.user, residence)    
        if residence_dn is None:
            raise Exception("unknown residence")
        #end if
    
        member = Member.get_by_uid(self.user, residence_dn, uid)

        if member is None:
            return self.error_no_entry()
        
        room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
        
        machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
        groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

        rooms = Room.get_rooms(self.user, residence_dn)
        if rooms is None:
            raise Exception("unable to retrieve rooms")
        #end if
        rooms = sorted(rooms, key=lambda t:t.cn.first())
        return { 
            "residence" : residence, 
            "user" : self.user,  
            "member_ldap" : member, 
            "room_ldap" : room, 
            "machines" : machines, 
            "groups" : groups,
            "rooms" : rooms
        }
    #end def

    @expose()
    def post(self, residence, member_uid, sn, givenName, mail, comment):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
    
        member.sn.replace(member.sn.first(), sn)

        member.givenName.replace(member.givenName.first(), givenName)
        member.mail.replace(member.mail.first(), mail)
        member.get("x-comment").replace(member.get("x-comment").first(), comment)

        self.user.ldap_bind.save(member)
    #end def

""" Controller de gestion des machines """
class MachineController(AuthenticatedBaseController):
    require_group = groups_enum.admin

    """ Controller fils d'ajout de machine """
    add  = None
    """ Controller fils de suppression de machine """
    delete = None
    def __init__(self):
        self.add = MachineAddController()
        self.delete = MachineDeleteController()

#end class

""" Controller de gestion des ajouts de machines.
    Il est de type REST, i.e. il gère séparement les requêtes
    get, post, put, delete
"""
class MachineAddController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Fonction de gestion de requete post sur le controller d'ajout """
    @expose()
    def post(self, residence, member_uid, name, mac):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        #Vérification que l'adresse mac soit correcte
        mac_match = re.match('^([0-9A-Fa-f]{2}[:-]?){5}([0-9A-Fa-f]{2})$', mac)
        if mac_match is None:
            #TODO : changer l'exception en une page d'erreur
            raise Exception("mac non valide")
        #endif

        #Remplacement de l'adresse mac non séparée
        mac_match = re.match('^([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})$', mac)
        if mac_match is not None:
            mac = mac_match.group(1) + ":" + mac_match.group(2) + ":" + mac_match.group(3) + ":" + mac_match.group(4) + ":" + mac_match.group(5) + ":" + mac_match.group(6)
        #endif
        
        #Remplacement de l'adresse mac séparée par des tirets
        mac_match = re.match('^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})$', mac)
        if mac_match is not None:
            mac = mac_match.group(1) + ":" + mac_match.group(2) + ":" + mac_match.group(3) + ":" + mac_match.group(4) + ":" + mac_match.group(5) + ":" + mac_match.group(6)
        #endif

        #Passage au format lowercase
        mac = mac.lower()


        # Vérification que le membre existe
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        if member is None:
            #TODO : membre inexistant
            pass
        #endif


        # Vérification que l'adresse mac de la machine n'existe pas déjà
        # Note : on cherche sur toute la résidence (residence_dn)
        machine = Machine.get_dhcp_by_mac(self.user, residence_dn, mac)
        if machine is not None:
            #TODO : gérer l'exception
            raise Exception("mac address already exist")
        #endif

        # Vérification que le nom de machine n'existe pas déjà
        # Note : on cherche sur toute la résidence (residence_dn)
        machine = Machine.get_dns_by_name(self.user, residence_dn, name)
        if machine is not None:
            #TODO : gérer l'exception
            raise Exception("dns name already exist")
        #endif

        # Génération de l'id de la machine et recherche d'une ip libre
        ip = IpReservation.get_first_free(self.user, residence_dn)

        # Rendre l'ip prise 
        taken_attribute = IpReservation.taken_attr(str(datetime.today()))
        self.user.ldap_bind.add_attr(ip.dn, taken_attribute)

        machine_folder = Machine.folder_attr()
        machine_folder_dn = ldap_config.machine_base_dn + member.dn
        try:
            self.user.ldap_bind.add_entry(machine_folder_dn, machine_folder)
        except ldap.ALREADY_EXISTS:
            pass # OKAY
        #end try

        # Attributs ldap de l'objet machine (regroupant dns et dhcp)
        machine_top = Machine.entry_attr(name)

        # Attributs ldap des objets dhcp et dns, fils de l'objet machine
        machine_dhcp = Machine.dhcp_attr(name, mac)
        machine_dns = Machine.dns_attr(name, ip.cn.first())
        
        # Construction du dn et ajout de l'objet machine 
        # en fils du membre (membre.dn)
        machine_dn = "cn=" + name + "," + ldap_config.machine_base_dn + member.dn
        self.user.ldap_bind.add_entry(machine_dn, machine_top)

        # Construction du dn et ajout de l'objet dhcp 
        # en fils de la machine (machine_dn)
        dhcp_dn = "cn=" + name + "," + machine_dn
        self.user.ldap_bind.add_entry(dhcp_dn, machine_dhcp)

        # Construction du dn et ajout de l'objet dns 
        dns_dn = "dlzHostName=" + name + "," + machine_dn
        self.user.ldap_bind.add_entry(dns_dn, machine_dns)
        
        

        redirect("/edit/member/" + residence + "/" + member_uid)
    #end def
#end class
        

""" Controller REST de gestion des ajouts de machines. """
class MachineDeleteController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Gestion des requêtes post sur ce controller """
    @expose()
    def post(self, residence, member_uid, machine_id):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        # Récupération du membre et de la machine
        # Note : on cherche la machine seulement sur le membre (member.dn)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        machine = Machine.get_machine_by_id(self.user, member.dn, machine_id)
        dns = Machine.get_dns_by_id(self.user, machine.dn)
        ip = IpReservation.get_ip(self.user, residence_dn, dns.dlzData.first())

        # Si la machine existe effectivement, on la supprime
        if machine is not None:

            self.user.ldap_bind.delete_entry_subtree(machine.dn)

            taken_attribute = IpReservation.taken_attr(ip.get("x-taken").first())
            self.user.ldap_bind.delete_attr(ip.dn, taken_attribute)
        #end if

        # On redirige sur la page d'édition du membre
        redirect("/edit/member/" + residence + "/" + member_uid)
    #end def
#end def


class WifiRestController(AuthenticatedRestController):
    require_group = groups_enum.respsalleinfo

    show = None

    def __init__(self, new_show):
        self.show = new_show
    
    @expose("brie.templates.edit.wifi")
    def get(self, uid):
        member = Member.get_by_uid(self.user, self.user.residence_dn, uid)     

        if member is None:
            self.show.error_no_entry()

        return { "member_ldap" : member }
    #end def
        

    @expose("brie.templates.edit.wifi")
    def post(self, uid, password):
    
        member = Member.get_by_uid(self.user, self.user.residence_dn, uid)
    
        if member is None:
            self.show.error_no_entry()
        
        wifi = Wifi.get_by_dn(self.user, member.dn)    
        
        if wifi is None:
            wifi_dn = "cn=wifi," + member.dn
            self.user.ldap_bind.add_entry(wifi_dn, Wifi.entry_attr(password))
        else:
            attr = Wifi.password_attr(password)
            self.user.ldap_bind.replace_attr(wifi.dn, attr)
        #end if

        redirect("/show/member/" + uid)
    #end def
#end class
        
""" Controller de gestion des rooms """
class RoomController(AuthenticatedBaseController):
    require_group = groups_enum.admin

    """ Controller fils d'ajout de machine """
    move  = None
    show = None
    change_member = None
    def __init__(self, show):
        self.move = RoomMoveController()
        self.show = show
        self.change_member = RoomChangeMemberController()


    """ Affiche les détails éditables de la chambre """
    @expose("brie.templates.edit.room")
    def index(self, residence, room_id):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    

        room = Room.get_by_uid(self.user, residence_dn, room_id)

        if room is None:
            raise Exception("no room")

        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())

        members = Member.get_all(self.user, residence_dn)
        
        return { 
            "residence" : residence,
            "user" : self.user, 
            "room_ldap" : room, 
            "member_ldap" : member,
            "members" : members
        }        
        #se Exception("tait toi")
    #end def

#end class

""" Controller REST de gestion des ajouts de machines. """
class RoomMoveController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Gestion des requêtes post sur ce controller """
    @expose()
    def post(self, residence, member_uid, room_uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        # Récupération du membre et de la machine
        # Note : on cherche la machine seulement sur le membre (member.dn)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        room = Room.get_by_uid(self.user, residence_dn, room_uid)

        # Si la machine existe effectivement, on la supprime
        if room is not None:
            if room.get("x-memberIn") is not None:
                raise Exception("chambre de destination non vide")
                #TODO passer sur une page d'erreur au lieu d'une exception
            else:
                old_room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
                memberIn_attribute = Room.memberIn_attr(str(member.dn))
                self.user.ldap_bind.delete_attr(old_room.dn, memberIn_attribute)
                self.user.ldap_bind.add_attr(room.dn, memberIn_attribute)
            #end if
        else:
            old_room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
            memberIn_attribute = Room.memberIn_attr(str(member.dn))
            self.user.ldap_bind.delete_attr(old_room.dn, memberIn_attribute)
        #end if
            
            #self.user.ldap_bind.delete_entry_subtree(machine.dn)

            #taken_attribute = IpReservation.taken_attr(ip.get("x-taken").first())
            #self.user.ldap_bind.delete_attr(ip.dn, taken_attribute)
        #end if

        # On redirige sur la page d'édition du membre
        redirect("/edit/member/" + residence + "/" + member_uid)
    #end def
#end def


""" Controller REST de gestion des ajouts de machines. """
class RoomChangeMemberController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Gestion des requêtes post sur ce controller """
    @expose()
    def post(self, residence, member_uid, room_uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        # Récupération du membre et de la machine
        # Note : on cherche la machine seulement sur le membre (member.dn)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        room = Room.get_by_uid(self.user, residence_dn, room_uid)

        if member is None and member_uid != "":
            raise Exception("member not found")
        #end if

        if member is not None:
            old_room_member = Room.get_by_member_dn(self.user, residence_dn, member.dn)
    
            # Si la machine existe effectivement, on la supprime
            if old_room_member is not None:
                raise Exception("le nouveau membre possèdait déjà une chambre. conflit")
            #end if
        #end if

        if room is None:
            raise Exception("room inconnue")

        if room.get("x-memberIn") is not None:
            memberIn_attribute = Room.memberIn_attr(str(room.get("x-memberIn").first()))
            self.user.ldap_bind.delete_attr(room.dn, memberIn_attribute)
        #end if

        if member is not None:
            memberIn_attribute = Room.memberIn_attr(str(member.dn))
            self.user.ldap_bind.add_attr(room.dn, memberIn_attribute)
        #end if    

        # On redirige sur la page d'édition du membre
        redirect("/edit/room/index/" + residence + "/" + room_uid)
    #end def
#end def
