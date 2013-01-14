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


class ErrorController(AuthenticatedBaseController):

    @expose("brie.templates.error.permission_denied")
    def permission_denied(self):
        return {}
    #end def

#end class

