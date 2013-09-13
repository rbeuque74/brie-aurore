# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.config import ldap_config, groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.plugins import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter

""" Controller d'affichage de details de membres, chambres et interfaces """ 
class ShowController(AuthenticatedBaseController):
    require_group = groups_enum.admin

    @expose("brie.templates.show.error")
    def error_no_entry(self):
        return { "error" : "Entrée non existante" }

    """ Affiche les détails du membre, de la chambre et de l'interface """
    @expose("brie.templates.show.member")
    @plugins("brie.controllers.show.member")
    def member(self, residence, uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    
    
        member = Member.get_by_uid(self.user, residence_dn, uid)

        if member is None:
            return self.error_no_entry()
        
        room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
        
        machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
        groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

        year = CotisationComputes.current_year()
        cotisations = Cotisation.cotisations_of_member(self.user, member.dn, year)
        extras = Cotisation.extras_of_member(self.user, member.dn, year)

        cotisations_mois = []
        already_paid = 0
        for cotisation in cotisations:
            cotisations_mois = (cotisations_mois + 
                [(cotisation, int(month)) for month in cotisation.get("x-validMonth").all()]
            )
            already_paid += int(cotisation.get("x-amountPaid").first())
        #end for

        return { 
            "residence" : residence, 
            "user" : self.user,  
            "member_ldap" : member, 
            "room_ldap" : room, 
            "machines" : machines, 
            "groups" : groups,
            "cotisations" : cotisations,
            "cotisations_mois" : cotisations_mois,
            "extras" : extras,
            "cotisation_paid" : already_paid
        }
    #end def

    @expose("brie.templates.show.room")
    def room(self, residence, room_id):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    

        room = Room.get_by_uid(self.user, residence_dn, room_id)

        if room is None:
            return self.error_no_entry()

        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())
        
        return { 
            "residence" : residence,
            "user" : self.user, 
            "room_ldap" : room, 
            "member_ldap" : member 
        }        
    #end def

#end class
        
