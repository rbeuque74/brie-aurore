# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.lib.camembert_helpers import *

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.model import DBSession
from brie.model.camembert import Interface
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
    def member(self, uid):
        member = Member.get_by_uid(self.user, uid)

        if member is None:
            return self.error_no_entry()
        
        room = Room.get_by_member_dn(self.user, member.dn)
        interface = (
            DBSession.query(Interface)
                .filter(Interface.idinterface == room.get("x-switchInterface").first())
                .first()
        )

        return { "member_ldap" : member, "interface" : interface, "room_ldap" : room }
    #end def

    @expose("brie.templates.show.room")
    def room(self, room_id):
        room = Room.get_by_uid(self.user, room_id)

        if room is None:
            return self.error_no_entry()

        interface = (
            DBSession.query(Interface)
                .filter(Interface.idinterface == room.get("x-switchInterface").first())
                .first()
        )

        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())
        
        return { "interface" : interface, "room_ldap" : room, "member_ldap" : member }        
    #end def

    @expose("brie.templates.show.interface")
    def interface(self, interface_id):
        interface = (
            DBSession.query(Interface)
                .filter(Interface.idinterface == interface_id)
                .first()
        )

        if interface is None:
            return self.error_no_entry()

        room = Room.get_by_interface(self.user, interface.idinterface)
    
        return { "interface" : interface, "room_ldap" : room }
    #end def
#end class
        
