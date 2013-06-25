# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

from brie.lib.base import BaseController
from brie.lib.aurore_helper import *
from brie import model

#from brie.controllers.secure import SecureController
import brie.controllers.auth as auth_handler
from brie.controllers.auth import AuthRestController
from brie.controllers.rooms import RoomsController
from brie.controllers.members import MembersController
from brie.controllers.show import ShowController
from brie.controllers.search import SearchController
from brie.controllers.edit import EditController
from brie.controllers.administration import AdministrationController
from brie.controllers.error import ErrorController


__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the Brie application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
#    admin = Catwalk(model, DBSession)
 
    auth = AuthRestController()
    rooms = RoomsController()
    members = MembersController()
    show = ShowController()
    edit = EditController(show)
    administration = AdministrationController()
    error = ErrorController()
    search = SearchController()
    
    @expose('brie.templates.index')
    def index(self):
        user = auth_handler.current.get_user()
        residence = None
 
        if user is not None:
            residence = Residences.get_name_by_dn(user, user.residence_dn)
        #end if
        
	return { "user" : user, "residence" : residence }
    #end def
#end class
