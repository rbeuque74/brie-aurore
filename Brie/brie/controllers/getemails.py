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
        for member in members:
            if not CotisationComputes.is_old_member(member.dn, self.user, residence_dn):
                emails.append(member.mail.first())
            #end if
        #end for

        return { 
            "user" : self.user, 
            "residence" : residence_name,
            "emails" : emails 
        }
    #end def

    @expose("brie.templates.getemails.cotisation_paid")
    def cotisation_paid(self, residence):
        residence_name = residence
        residence_dn = Residences.get_dn_by_name(self.user, residence_name)
        members = Member.get_all(self.user, residence_dn)
        emails = []
        for member in members:
            if CotisationComputes.is_cotisation_paid(member.dn, self.user, residence_dn):
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

