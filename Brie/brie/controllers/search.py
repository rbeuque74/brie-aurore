# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.plugins import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController
from brie.controllers.members import MembersController

from operator import itemgetter

""" Controller de recherche """ 
class SearchController(AuthenticatedBaseController):

    @expose("brie.templates.search.error")
    def error_no_entry(self):
        return { "error" : "Entrée non existante" }

    """ Affiche les résultats """
    @expose("brie.templates.search.member")
    @plugins("brie.controllers.search.member")
    def member(self, residence, name):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    
        members = Member.get_by_name(self.user, residence_dn, name)

        if members is None:
            return self.error_no_entry()
        
    #    room = Room.get_by_member_dn(self.user, residence_dn, member.dn)
        
    #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
    #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

        return { 
            "residence" : residence, 
            "user" : self.user,  
            "member_ldap" : members, 
            "sort_name" : MembersController.sort_name 
    #        "room_ldap" : room, 
    #        "machines" : machines, 
    #        "groups" : groups
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
        
