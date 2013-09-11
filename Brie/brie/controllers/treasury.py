# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.plugins import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController
from brie.controllers.members import MembersController

from operator import itemgetter

""" Controller de recherche """ 
class TreasuryController(AuthenticatedBaseController):
    require_group = groups_enum.tresorier

    validate = None
    
    def __init__(self):
        self.validate = ValidatePaymentController()
    #end if

    """ Affiche les résultats """
    @expose("brie.templates.treasury.index")
    def index(self):
        residence_dn = self.user.residence_dn
        residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)

        year = CotisationComputes.current_year()
        pending_payments = Cotisation.get_all_pending_payments(self.user, residence_dn, year)

        admin_totals = dict()
        admin_payments_received = dict()
        for pending_payment in pending_payments:
            admin_member = Member.get_by_dn(self.user, pending_payment.get("x-action-user").first())
            admin_name = pending_payment.get("x-action-user-info").first()
            if admin_member is not None:
                admin_name = admin_member.cn.first()
                        

            dn_prefix = "cn=" + pending_payment.cn.first() + ",cn=" + str(year) + ",cn=cotisations,"

            print dn_prefix
            member_dn = pending_payment.dn[len(dn_prefix):]
            print member_dn
            member = Member.get_by_dn(self.user, member_dn)
    
            amount_paid = int(pending_payment.get("x-amountPaid").first())

            if admin_name in admin_totals:
                admin_totals[admin_name] += amount_paid
            else:
                admin_totals[admin_name] = amount_paid
            #end if

            if admin_name in admin_payments_received:
                admin_payments_received[admin_name].append((member, pending_payment))
            else:
                admin_payments_received[admin_name] = [(member, pending_payment)]
            #end if            
        #end for

        admin_payments_received_ordered = sorted(admin_payments_received.iteritems(), key=lambda t:t[0])

        return { 
            "residence" : residence, 
            "user" : self.user,  
            "admin_totals" : admin_totals,
            "admin_payments_received" : admin_payments_received_ordered
        }
    #end def

#end class


class ValidatePaymentController(AuthenticatedRestController):
    
    @expose()
    def post(self, residence, member_uid, payment_cn, year):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)

        cotisation_dn = "cn=" + payment_cn + ",cn=" + str(year) + ",cn=cotisations," + member.dn
        cashed_attr = Cotisation.cashed_payment_attr()        
        cotisation = self.user.ldap_bind.search_dn(cotisation_dn)
        cotisation.add("x-paymentCashed", "TRUE")
        self.user.ldap_bind.save(cotisation)

        redirect("/treasury/")
    #end def
#end class
