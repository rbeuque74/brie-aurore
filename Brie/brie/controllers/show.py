# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter

""" Controller d'affichage de details de membres, chambres et interfaces """ 
class ShowController(AuthenticatedBaseController):

    @expose("brie.templates.show.error")
    def error_no_entry(self):
        return { "error" : "Entrée non existante" }

    """ Affiche les détails du membre, de la chambre et de l'interface """
    @expose("brie.templates.show.member")
    def member(self, residence, uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    
    
        member = Member.get_by_uid(self.user, residence_dn, uid)

        if member is None:
            return self.error_no_entry()
        
        room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
        
        machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
        groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

        return { 
            "residence" : residence, 
            "user" : self.user,  
            "member_ldap" : member, 
            "room_ldap" : room, 
            "machines" : machines, 
            "groups" : groups
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
        
