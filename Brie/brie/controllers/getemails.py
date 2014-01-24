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
    def index(self):
        residences = []
        rooms_stats = dict()
        members_stats = dict()
        residences_ldap = Residences.get_residences(self.user)
        for residence_ldap in residences_ldap:
            residence_dn = residence_ldap.uniqueMember.first()
            residence_name = residence_ldap.cn.first()
            residences.append(residence_name)
            members_stats[residence_name] = CotisationComputes.members_status_from_residence(self.user, residence_dn)
            members_stats[residence_name]['number_of_cotisation_paid_members'] = len(members_stats[residence_name]['cotisation_paid_members'])
            members_stats[residence_name]['number_of_cotisation_late_members'] = len(members_stats[residence_name]['cotisation_late_members'])
            members_stats[residence_name]['number_of_no_cotisation_members'] = len(members_stats[residence_name]['no_cotisation_members'])
            members_stats[residence_name]['number_of_old_members'] = len(members_stats[residence_name]['old_members'])
            members_stats[residence_name]['number_of_current_members'] = members_stats[residence_name]['number_of_cotisation_paid_members'] + members_stats[residence_name]['number_of_cotisation_late_members'] + members_stats[residence_name]['number_of_no_cotisation_members']
            rooms_stats[residence_name] = dict()
            rooms_stats[residence_name]['number_of_rooms'] = Room.get_number_of_rooms(self.user, residence_dn)
            rooms_stats[residence_name]['empty_rooms'] = []
            for room in Room.get_rooms(self.user, residence_dn):
                if not room.has("x-memberIn"):
                    rooms_stats[residence_name]['empty_rooms'].append(room)

        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        return { 
            "user" : self.user, 
            "residence" : residence,
            "residences" : residences,
            "rooms_stats" : rooms_stats, 
            "members_stats" : members_stats 
        }
    #end def
#end class

