# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter


#root = tg.config['application_root_module'].RootController

""" Controller d'affichage de details de membres, chambres et interfaces """ 
class EditController(AuthenticatedBaseController):
    require_group = groups_enum.admin

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

#end class

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
        
