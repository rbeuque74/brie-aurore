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

class RegistrationController(AuthenticatedBaseController):
    require_group = groups_enum.admin    

    member_edit_controller = None
    administration_controller = None

    quick_last_registrations = dict()

    def __init__(self, member_edit_controller, administration_controller):
        self.new = NewRegistrationController(member_edit_controller, administration_controller)
        self.recover = ErrorRecoveryRegistrationController(member_edit_controller)
        self.member_edit_controller = member_edit_controller
        self.administration_controller = administration_controller
    #end def

    @expose("brie.templates.registration.index")
    def index(self):
        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        rooms = Room.get_rooms(self.user, self.user.residence_dn)
        rooms = sorted(rooms, key=lambda t:t.cn.first())
        
        areas = Room.get_areas(self.user, self.user.residence_dn)
        for room in rooms:
            for area in areas:
                if area.dn in room.dn:
                    room.area = area
                    break
                #end if
            #end for
        #end for

        now = datetime.now()

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

        available_months = CotisationComputes.get_available_months(now.month, 8, [])

        year_price = 0
        month_price = 0

        try:
            year_price = int(Cotisation.prix_annee(self.user, self.user.residence_dn).cn.first())
            month_price = int(Cotisation.prix_mois(self.user, self.user.residence_dn).cn.first())
        except:
            pass
        #end try

        available_months_prices = []
        index = 1

        already_paid = 0        
        for available_month in available_months:
            if available_month == 8:
                available_months_prices.append(
                    (available_month, "fin de l'année ".decode("utf-8"), CotisationComputes.price_to_pay(year_price, month_price, already_paid, index))
                )
            else: 
                available_months_prices.append(
                    (available_month, str(now.day) + " " + month_names[available_month % 12], CotisationComputes.price_to_pay(year_price, month_price, already_paid, index))
                )
            #end if
            index += 1
        #end for


        extras_available = Cotisation.get_all_extras(self.user, self.user.residence_dn)

        if residence in RegistrationController.quick_last_registrations:
            quick_last = RegistrationController.quick_last_registrations[residence]
        else:
            quick_last = []
        #end if

        groupes = Groupes.get_all(self.user, self.user.residence_dn)

        return {
            "user" : self.user,
            "residence" : residence,
            "rooms" : rooms,
            "quick_last" : quick_last,
            "available_months_prices" : available_months_prices,
            "extras_available" : extras_available,
            "groupes" : groupes
        }
    #end class


    @expose("brie.templates.registration.error")
    def error(self, member_uid):
        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        self.member_edit_controller.member.user = self.user
        
        edit_get_values = self.member_edit_controller.member.get(residence, member_uid)

        
        rooms = Room.get_rooms(self.user, self.user.residence_dn)
        rooms = sorted(rooms, key=lambda t:t.cn.first())

        

        return edit_get_values
    #end def 
        
        
#end class 

class NewRegistrationController(AuthenticatedRestController):
    require_group = groups_enum.admin

    member_edit_controller = None
    administration_controller = None

    def __init__(self, member_edit_controller, administration_controller):
        self.member_edit_controller = member_edit_controller
        self.administration_controller = administration_controller

    @expose()
    def post(self, residence, sn, givenName, mail, phone, 
        room_uid, first_machine_name, first_machine_mac,
        next_end, extra_name, group_cn, 
        second_machine_name = "", second_machine_mac = "",
        third_machine_name = "", third_machine_mac = "",
        fourth_machine_name = "", fourth_machine_mac = "", 
    ):
        # Initialisation des Users des Controllers Existant appellés 
        self.member_edit_controller.add.user = self.user
        self.member_edit_controller.machine.add.user = self.user
        self.member_edit_controller.room.move.user = self.user
        self.member_edit_controller.cotisation.add.user = self.user
        self.administration_controller.groups.add_member.user = self.user

        if phone == '':
            phone = ' '
        #end if

        # On ne permet pas a des simples aides membres d'ajouter a des groupes
        groupsPredefinis = [groups_enum.responsablereseau, groups_enum.admin, groups_enum.membreca, groups_enum.tresorier, groups_enum.respsalleinfo, groups_enum.exemptdecoglobale]
        if group_cn != "" and group_cn in groupsPredefinis and groups_enum.responsablereseau not in self.user.groups.list():
            group_cn = ""
        #end if

        member_uid = self.member_edit_controller.add.post(residence, givenName, sn, mail, phone, go_redirect = False)
        member = Member.get_by_uid(self.user, self.user.residence_dn, member_uid)

        if member is not None:
            if residence not in RegistrationController.quick_last_registrations:
                RegistrationController.quick_last_registrations[residence] = []
            #end if
            RegistrationController.quick_last_registrations[residence].append(member)
        #end if

        if room_uid != "":
            self.member_edit_controller.room.move.post(residence, member_uid, room_uid, erase = True, go_redirect = False)
        #end if

        try:
            if first_machine_name != "" and first_machine_mac != "":
                self.member_edit_controller.machine.add.post(residence, member_uid, first_machine_name, first_machine_mac, go_redirect = False)
            #end if
            if second_machine_name != "" and second_machine_mac != "":
                self.member_edit_controller.machine.add.post(residence, member_uid, second_machine_name, second_machine_mac, go_redirect = False)
            #end if
            if third_machine_name != "" and third_machine_mac != "":
                self.member_edit_controller.machine.add.post(residence, member_uid, third_machine_name, third_machine_mac, go_redirect = False)
            #end if
            if fourth_machine_name != "" and fourth_machine_mac != "":
                self.member_edit_controller.machine.add.post(residence, member_uid, fourth_machine_name, fourth_machine_mac, go_redirect = False)
            #end if

            if next_end != "" or extra_name != "":
                self.member_edit_controller.cotisation.add.post(residence, member_uid, next_end, extra_name, go_redirect = False)
            #end if

            if group_cn != "":
                self.administration_controller.groups.add_member.post(group_cn, member.dn, go_redirect = False)
            #end if
        except:
            redirect("/registration/error/" + member_uid) 
        #end trycatch
    
        redirect("/registration/")
    #end def
#end class

class ErrorRecoveryRegistrationController(AuthenticatedRestController):
    require_group = groups_enum.admin

    member_edit_controller = None

    def __init__(self, member_edit_controller):
        self.member_edit_controller = member_edit_controller

    @expose()
    def post(self, residence, member_uid, room_uid, 
            first_machine_name, first_machine_mac, 
            next_end, extra_name, group_cn):
        member = Member.get_by_uid(self.user, self.user.residence_dn, member_uid)
        
        if member is None:
            raise Exception("Invalid member uid")

        
        self.member_edit_controller.add.user = self.user
        self.member_edit_controller.machine.add.user = self.user
        self.member_edit_controller.room.move.user = self.user
        self.member_edit_controller.cotisation.add.user = self.user

        if room_uid != "":
            self.member_edit_controller.room.move.post(residence, member_uid, room_uid, erase = True, go_redirect = False)

        try:
            if first_machine_mac != "":
                self.member_edit_controller.machine.add.post(residence, member_uid, first_machine_name, first_machine_mac, go_redirect = False)


            if next_end != "":
                self.member_edit_controller.cotisation.add.post(residence, member_uid, next_end, extra_name, go_redirect = False)

            # On ne permet pas a des simples aides membres d'ajouter a des groupes
            groupsPredefinis = [groups_enum.responsablereseau, groups_enum.admin, groups_enum.membreca, groups_enum.tresorier, groups_enum.respsalleinfo, groups_enum.exemptdecoglobale]
            if group_cn != "" and group_cn in groupsPredefinis and groups_enum.responsablereseau not in self.user.groups.list():
                group_cn = ""
            #end if

            if group_cn != "":
                self.administration_controller.groups.add_member.post(group_cn, member.dn, go_redirect = False)
            #end if
        except:
            redirect("/registration/error/" + member_uid)
        #end try

        redirect("/registration")
    #end def
#end class

        
