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

class StatsController(AuthenticatedBaseController):

    @expose("brie.templates.stats.index")
    def index(self):
        residences = []
        rooms_stats = dict()
        members_stats = dict()
        total_earned = dict()
        average_cotisation = dict()
        global_average_cotisation = 0
        global_total_earned = 0
        global_current_members = 0
        residences_ldap = Residences.get_residences(self.user)
        year = CotisationComputes.current_year()                                                                                    
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
            # FIXME : Vérifier si on compte les "extras" (vente de câbles). Il ne faudrait pas les compter.
            all_payments = Cotisation.get_all_payment_by_year(self.user, residence_dn, year)
            total_earned[residence_name] = 0
            for onepayment in all_payments:
                total_earned[residence_name] += float(onepayment.get('x-amountPaid').first())
            #end for
            if(members_stats[residence_name]['number_of_current_members'] != 0):
                average_cotisation[residence_name] = float(total_earned[residence_name])/float(members_stats[residence_name]['number_of_current_members'])
            else:
                average_cotisation[residence_name] = 0
            global_total_earned += total_earned[residence_name]
            global_current_members += members_stats[residence_name]['number_of_current_members']
        
        if(global_current_members != 0):
            global_average_cotisation = global_total_earned/global_current_members
        else:
            global_average_cotisation = 0

        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        return { 
            "user" : self.user, 
            "residence" : residence,
            "residences" : residences,
            "rooms_stats" : rooms_stats, 
            "members_stats" : members_stats,
            "total_earned" : total_earned,
            "average_cotisation" : average_cotisation,
            "global_total_earned" : global_total_earned,
            "global_current_members" : global_current_members,
            "global_average_cotisation" : global_average_cotisation 
        }
    #end def
#end class

