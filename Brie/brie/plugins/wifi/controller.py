from tg.decorators import expose
from tg.controllers import redirect

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController



class Wifi:
    
    @staticmethod
    @expose("brie.plugins.wifi.show")
    def show(models):
        return {
            "activated" : str("Todo")
        }
    #end def

#end class

class DirectController(AuthenticatedRestController):
    @expose("")
    def get(self, residence, member_uid):
        redirect("/show/member/" + residence + "/" + member_uid)
    #end def
    
    @expose("")
    def post(self, residence, member_uid):
        redirect("/show/member/" + residence + "/" + member_uid)
    #end def
#end class
