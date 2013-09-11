# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *
from brie.lib.name_translation_helpers import Translations

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter

from datetime import datetime
import uuid
import re
import ldap


#root = tg.config['application_root_module'].RootController

""" Controller d'edition de details de membres, chambres""" 
class EditController(AuthenticatedBaseController):
    require_group = groups_enum.admin


    """ Controller fils wifi pour gérer le wifi """
    wifi = None

    """ Controller fils room pour gérer les chambres """
    room = None

    """ Controller fils de gestion des machines """
    machine = None

    member = None

    add = None

    cotisation = None

    def __init__(self, new_show):
        self.show = new_show
        self.wifi = WifiRestController(new_show)
        self.machine = MachineController()
        self.room = RoomController(new_show)
        self.member = MemberModificationController(new_show)
        self.add = MemberAddController()
        self.cotisation = CotisationController()

    
    """ Affiche les détails éditables de la chambre """
    @expose("brie.templates.edit.room")
    def room(self, residence, room_id):
        return self.show.room(residence, room_id)
    #end def

#end class

class MemberAddController(AuthenticatedRestController):
	require_group = groups_enum.admin

	""" Fonction de gestion de requete post sur le controller d'ajout """
	@expose()
	def post(self, residence, prenom, nom, mail, go_redirect = True):

		member_uid = Translations.to_uid(prenom, nom)
		member = Member.entry_attr(member_uid, prenom, nom, mail, -1)

		residence_dn = Residences.get_dn_by_name(self.user, residence)

		now = datetime.now()
		year = 0

		if now.month >= 8:
			year = now.year
		else:
			year = now.year - 1 
		#endif

		member_dn = "uid=" + member_uid + ",ou=" + str(year) + "," + ldap_config.username_base_dn + residence_dn
		self.user.ldap_bind.add_entry(member_dn, member)
		

		#preview = member, room
		#index_result["preview"] = preview

                if go_redirect:
                    redirect("/edit/member/" + residence + "/" + member_uid)
                else:
                    return member_uid
                #end if
	#end def
#end class

class MemberModificationController(AuthenticatedRestController):
    require_group = groups_enum.admin

    """ Controller show qu'on réutilise pour gérer l'affichage """
    show = None

    def __init__(self, new_show):
        self.show = new_show
    #end def

    """ Affiche les détails éditables du membre et de la chambre """
    @expose("brie.templates.edit.member")
    def get(self, residence, uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        
        self.show.user = self.user
        show_values = self.show.member(residence, uid)
        
        rooms = Room.get_rooms(self.user, residence_dn)
        if rooms is None:
            raise Exception("unable to retrieve rooms")
        #end if
        rooms = sorted(rooms, key=lambda t:t.cn.first())

        show_values["rooms"] = rooms

        cotisations = show_values["cotisations"]
        month_names = [
            "Janvier",
            "Fevrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Aout",
            "Septembre",
            "Octobre",
            "Novembre",
            "Decembre"
        ]  # SALE FIXME

        # FIXME => mettre dans aurore helper
        paid_months = []
        already_paid = 0
        for cotisation in cotisations:
            paid_months = (
                paid_months + 
                [int(month) for month in cotisation.get("x-validMonth").all()]
            )

            already_paid += int(cotisation.get("x-amountPaid").first())
        #end for

        now = datetime.now()

        available_months = CotisationComputes.get_available_months(now.month, 8, paid_months)

        year_price = 0
        month_price = 0

        try:
            year_price = int(Cotisation.prix_annee(self.user, residence_dn).cn.first())
            month_price = int(Cotisation.prix_mois(self.user, residence_dn).cn.first())
        except:
            pass
        #end try

        available_months_prices = []
        index = 1
        
        for available_month in available_months:
            available_months_prices.append(
                (available_month, month_names[available_month - 1], CotisationComputes.price_to_pay(year_price, month_price, already_paid, index))
            )
            index += 1
        #end for

        show_values["available_months_prices"] = available_months_prices
        
        extras_available = Cotisation.get_all_extras(self.user, residence_dn)
        show_values["extras_available"] = extras_available

        return show_values
    #end def

    @expose()
    def post(self, residence, member_uid, sn, givenName, mail, comment):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)

        # FIXME
        sn = unicode.encode(sn, 'utf-8')
        givenName = unicode.encode(givenName, 'utf-8')
        comment = unicode.encode(comment, 'utf-8')
    
        member.sn.replace(member.sn.first(), sn)

        member.givenName.replace(member.givenName.first(), givenName)
        member.cn.replace(member.cn.first(), givenName + " " + sn)
        member.mail.replace(member.mail.first(), mail)
        if comment != "":
            member.get("x-comment").replace(member.get("x-comment").first(), comment)

        self.user.ldap_bind.save(member)

        redirect("/edit/member/" + residence + "/" + member_uid)
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
    def post(self, residence, member_uid, name, mac, go_redirect = True):
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
        

        # On modifie silencieusement le nom de la machine si il existe déjà
        def try_name(name, number):
            actual_name = name
            if number > 0:
                actual_name = name + "-" + str(number)
            #end if 

            machine = Machine.get_dns_by_name(self.user, residence_dn, actual_name)
            if machine is not None:
                return try_name(name, number + 1)
            else:
                return actual_name
            #end if
        #endif

        name = try_name(name, 0)

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
        
        
        if go_redirect:
            redirect("/edit/member/" + residence + "/" + member_uid)
        #end if
    #end def
#end class
        
class CotisationController(AuthenticatedBaseController):
    require_group = groups_enum.admin

    add  = None
    def __init__(self):
        self.add = CotisationAddController()
#end class

class CotisationAddController(AuthenticatedRestController):
    require_group = groups_enum.admin

    def create_cotisation(self, member, time, current_year, residence, residence_dn, member_uid, next_end):
        print residence
        print member_uid
        print next_end


        now = datetime.now()
        next_month = int(next_end)        

        if not CotisationComputes.is_valid_month(next_month):
            raise Exception("Invalid month") #FIXME
        #end if

        print "current_year " + str(current_year)

        print member.dn
        cotisations_existantes = Cotisation.cotisations_of_member(self.user, member.dn, current_year)
        paid_months = []
        already_paid = 0
        for cotisation in cotisations_existantes:
            paid_months = (
                paid_months + 
                [int(month) for month in cotisation.get("x-validMonth").all()]
            )
            already_paid += int(cotisation.get("x-amountPaid").first())
        #end for

        print paid_months   
       
        available_months = CotisationComputes.get_available_months(now.month, next_month, paid_months)

        if available_months == []:
            return

        year_price = 0
        month_price = 0

        try:
            year_price = int(Cotisation.prix_annee(self.user, residence_dn).cn.first())
            month_price = int(Cotisation.prix_mois(self.user, residence_dn).cn.first())
        except:
            pass
        #end try
        
        price_to_pay = CotisationComputes.price_to_pay(year_price, month_price, already_paid, len(available_months))

        user_info = self.user.attrs.cn.first()
        return Cotisation.entry_attr(time, residence, current_year, self.user.attrs.dn, user_info, price_to_pay, available_months)
    #end def

    def create_extra(self, time, current_year, residence, residence_dn, member_uid, extra_name):
        extra_item = Cotisation.get_extra_by_name(self.user, residence_dn, extra_name)

        prix = extra_item.cn.first()

        user_info = self.user.attrs.cn.first()
        return Cotisation.extra_attr(time, residence, current_year, self.user.attrs.dn, user_info, extra_item.uid.first(), prix)
    #end def
    
    @expose()
    def post(self, residence, member_uid, next_end, extra_name, go_redirect = True):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        time = str(datetime.now())
        current_year = CotisationComputes.current_year()
        member = Member.get_by_uid(self.user, residence_dn, member_uid)

        cotisation = None
        extra = None

        if next_end != "":
            cotisation = self.create_cotisation(member, time, current_year, residence, residence_dn, member_uid, next_end)
        
        if extra_name != "":
            extra = self.create_extra(time, current_year, residence, residence_dn, member_uid, extra_name)
        #end if

        if cotisation is None and extra is None:
            if go_redirect:
                redirect("/edit/member/" + residence + "/" + member_uid)
            else:
                return
            #end if
        #end if
            
        folder_dn = ldap_config.cotisation_member_base_dn + member.dn
        print folder_dn
        year_dn = "cn=" + str(current_year) + "," + folder_dn
   
        try:
            folder = Cotisation.folder_attr()
            self.user.ldap_bind.add_entry(folder_dn, folder)
        except ldap.ALREADY_EXISTS:
            pass # OKAY
        #end try

        try:
            year = Cotisation.year_attr(current_year)
            self.user.ldap_bind.add_entry(year_dn, year)
        except ldap.ALREADY_EXISTS:
            pass # OKAY
        #end try

        
        if cotisation is not None:
            cotisation_dn = "cn=cotisation-" + time + "," + year_dn
            print cotisation
            self.user.ldap_bind.add_entry(cotisation_dn, cotisation)
        #end if        

        if extra is not None:
            extra_dn = "cn=extra-" + time + "," + year_dn
            print extra
            self.user.ldap_bind.add_entry(extra_dn, extra)
        #end if

        if go_redirect:
            redirect("/edit/member/" + residence + "/" + member_uid)
        else:
            return 
        #end if
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
    def post(self, residence, member_uid, room_uid, erase = True, go_redirect = True):
        residence_dn = Residences.get_dn_by_name(self.user, residence)

        # Récupération du membre et de la machine
        # Note : on cherche la machine seulement sur le membre (member.dn)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        room = Room.get_by_uid(self.user, residence_dn, room_uid)

        if room is not None:
            member_in = room.get('x-memberIn').first()
            if  member_in is not None:
                if erase:
                    self.user.ldap_bind.delete_attr(room.dn, { "x-memberIn" : member_in })
                else:
                    raise Exception("chambre de destination non vide")
                #end if
            #end if
            old_room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
            memberIn_attribute = Room.memberIn_attr(str(member.dn))
            if old_room is not None:
                self.user.ldap_bind.delete_attr(old_room.dn, memberIn_attribute)
            #end if
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

        if go_redirect:
            # On redirige sur la page d'édition du membre
            redirect("/edit/member/" + residence + "/" + member_uid)
        #end if
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

        if room.get("x-memberIn") is not None and room.get("x-memberIn").first() != 'None':
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
