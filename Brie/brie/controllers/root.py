# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

from brie.lib.base import BaseController
from brie.model import DBSession, metadata
from brie import model
#from brie.controllers.secure import SecureController
import brie.controllers.auth as auth_handler
from brie.controllers.auth import AuthRestController
from brie.controllers.rooms import RoomsController
from brie.controllers.show import ShowController
from brie.controllers.edit import EditController

from brie.model.camembert import Materiel

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
    show = ShowController()
    edit = EditController(show)
    
    @expose('brie.templates.index')
    def index(self):
        """Handle the front-page."""
	materiel = DBSession.query(Materiel)
        user = auth_handler.current.get_user()
        
	return { "user" : user, "materiel" : materiel }
    
    @expose()
    def foobar(self):
        redirect("http://172.17.22.10:9000/toto")
    #end def

#    @expose('brie.templates.index')
#    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
#    def manage_permission_only(self, **kw):
#        """Illustrate how a page for managers only works."""
#        return dict(page='managers stuff')
