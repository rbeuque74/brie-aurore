# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.lib.camembert_helpers import *

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.model import DBSession
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController
from brie.controllers.import_actions import *

from operator import itemgetter


#root = tg.config['application_root_module'].RootController

""" Controller d'affichage de details de membres, chambres et interfaces """ 
class EditController(AuthenticatedBaseController):
    show = None
    wifi = None

    def __init__(self, new_show):
        self.show = new_show
        self.wifi = WifiRestController(new_show)

    """ Affiche les détails du membre, de la chambre et de l'interface """
    @expose("brie.templates.edit.member")
    def member(self, uid):
        return self.show.member(uid)
    #end def

    @expose("brie.templates.edit.room")
    def room(self, room_number):
        return self.show.room(room_number)
    #end def

    @expose("brie.templates.edit.interface")
    def interface(self, interface_id):
        return self.show.interface(interface_id)
    #end def

    @expose("brie.templates.edit.import_from")
    def import_from(self, room_number):
        success = True
        message = ""

#        try:
        Migration.import_all(self.user.ldap_bind, room_number)
#        except Exception as ex:
#            success = False
#            message = str(ex)
        #end try
    
        return {"room_number" : room_number,  "success" : success, "message" : message } 
    #end def
#end class

class WifiRestController(AuthenticatedRestController):
    show = None

    def __init__(self, new_show):
        self.show = new_show
    
    @expose("brie.templates.edit.wifi")
    def get(self, uid):
        member = Member.get_by_uid(self.user, uid)     

        if member is None:
            self.show.error_no_entry()
        

    def post(self, uid, password):
        member = Member.get_by_uid(self.user, uid)
    
        if member is None:
            self.show.error_no_entry()
        
        wifi = Wifi.get_by_dn(self.user, member.dn)    
        
        if wifi is None:
            wifi_dn = "cn=wifi," + member.dn
            self.user.ldap_bind.add_entry(wifi_dn, Wifi.entry_attr(password))
        else:
            attr = {
                "userPassword" : password
            }
            self.user.ldap_bind.replace_attr(wifi.dn, attr)
        #end if

        redirect("/show/member/" + uid)
    #end def
#end class
        
