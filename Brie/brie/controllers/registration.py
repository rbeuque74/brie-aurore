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

    new_member = None

    quick_last_registrations = []

    def __init__(self, member_edit_controller):
        self.new = NewRegistrationController(member_edit_controller)
    #end def

    @expose("brie.templates.registration.index")
    def index(self):
        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        rooms = Room.get_rooms(self.user, self.user.residence_dn)
        rooms = sorted(rooms, key=lambda t:t.cn.first())

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
            available_months_prices.append(
                (available_month, month_names[available_month - 1], CotisationComputes.price_to_pay(year_price, month_price, already_paid, index))
            )
            index += 1
        #end for


        extras_available = Cotisation.get_all_extras(self.user, self.user.residence_dn)

        return {
            "user" : self.user,
            "residence" : residence,
            "rooms" : rooms,
            "quick_last" : RegistrationController.quick_last_registrations,
            "available_months_prices" : available_months_prices,
            "extras_available" : extras_available
        }

#end class 

class NewRegistrationController(AuthenticatedRestController):
    require_group = groups_enum.admin

    member_edit_controller = None

    def __init__(self, member_edit_controller):
        self.member_edit_controller = member_edit_controller

    @expose()
    def post(self, residence, sn, givenName, mail, 
        room_uid, first_machine_name, first_machine_mac,
        next_end, extra_name
    ):
        # Initialisation des Users des Controllers Existant appellés 
        self.member_edit_controller.add.user = self.user
        self.member_edit_controller.machine.add.user = self.user
        self.member_edit_controller.room.move.user = self.user
        self.member_edit_controller.cotisation.add.user = self.user

        member_uid = self.member_edit_controller.add.post(residence, givenName, sn, mail, go_redirect = False)
        self.member_edit_controller.machine.add.post(residence, member_uid, first_machine_name, first_machine_mac, go_redirect = False)
        self.member_edit_controller.room.move.post(residence, member_uid, room_uid, erase = True, go_redirect = False)
        self.member_edit_controller.cotisation.add.post(residence, member_uid, next_end, extra_name, go_redirect = False)        

        member = Member.get_by_uid(self.user, self.user.residence_dn, member_uid)

        if member is not None:
            RegistrationController.quick_last_registrations.append(member)
        #end if
    
        redirect("/registration/")
    #end def
#end class
