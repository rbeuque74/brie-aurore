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

class GetEmailsController(AuthenticatedBaseController):

    @expose("brie.templates.getemails.index")
    def index(self, residence):
        residence_name = residence
        residence_dn = Residences.get_dn_by_name(self.user, residence_name)
        members = Member.get_all(self.user, residence_dn)
        emails = []
        current_year = CotisationComputes.current_year()
        for member in members:
            if len(Cotisation.cotisations_of_member(self.user, member.dn, current_year)) > 0:
                emails.append(member.mail.first())
            #end if
        #end for

        return { 
            "user" : self.user, 
            "residence" : residence_name,
            "emails" : emails 
        }
    #end def
#end class

