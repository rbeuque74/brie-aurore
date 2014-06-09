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


class GroupAddMemberController(AuthenticatedRestController):
    
    @expose()
    def post(self, group_cn, user_dn, go_redirect = True):
        groups_of_user = Groupes.get_by_user_dn(self.user, self.user.residence_dn, user_dn)

        if group_cn in groups_of_user:
            redirect("/administration/")
        #end if

        target_group = Groupes.get_by_cn(self.user, self.user.residence_dn, group_cn)

        if target_group is None:
            redirect("/administration/")
        #end if

        attr = Groupes.unique_member_attr(user_dn)
        self.user.ldap_bind.add_attr(target_group.dn, attr)

        if go_redirect:
            redirect("/administration/")
        #end if
    #end def

#end class

class GroupController(AuthenticatedBaseController):
    add_member = GroupAddMemberController()

    @expose()
    def delete_member(self, group_cn, user_dn):
        groups_of_user = Groupes.get_by_user_dn(self.user, self.user.residence_dn, user_dn)

        if group_cn in groups_of_user:
            target_group = Groupes.get_by_cn(self.user, self.user.residence_dn, group_cn)
            
            attr = Groupes.unique_member_attr(user_dn)
            self.user.ldap_bind.delete_attr(target_group.dn, attr)
        #end if

        redirect("/administration/")
    #end def

    @expose()
    def grace_cotisation(self, group_cn):
        group = Groupes.get_by_cn(self.user, self.user.residence_dn, group_cn)

        print("[LOG] start grace du groupe "+ group.dn + " par l'admin "+ self.user.attrs.dn)

        for user_dn in group.get('uniqueMember').all():
            current_year = CotisationComputes.current_year()
            cotisations = Cotisation.cotisations_of_member(self.user, user_dn, current_year)
            for cotisation in cotisations:
                if cotisation.has('x-paymentCashed') and cotisation.get('x-paymentCashed').first() == 'TRUE':
                    print("[LOG] impossible de gracier une cotisation encaissee pour l'utilisateur "+ user_dn + " par l'admin "+ self.user.attrs.dn)
                else:
                    old_montant = cotisation.get("x-amountPaid").first()
                    cotisation.get("x-amountPaid").replace(cotisation.get("x-amountPaid").first(), 0)
                    self.user.ldap_bind.save(cotisation)
                    print("[LOG] cotisation graciee (" + old_montant + "EUR) pour l'utilisateur "+ user_dn + " par l'admin "+ self.user.attrs.dn)
                #end if
            #end for(cotisation)
        #end for(users)

        print("[LOG] fin du grace_bulk_action du groupe "+ group.dn + " par l'admin "+ self.user.attrs.dn)

        redirect("/administration/")
    #end def

#end class
        

class AdministrationController(AuthenticatedBaseController):
    groups = GroupController()

    @expose("brie.templates.show.error")
    def error_no_entry(self):
        return { "error" : "Entrée non existante" }

    @expose("brie.templates.administration.index")
    def index(self):
        groups = Groupes.get_all(self.user, self.user.residence_dn)
        all_users = sorted(Member.get_all(self.user, self.user.residence_dn), key=lambda u: u.cn.first())

        residence = None
        if self.user is not None:
            residence = Residences.get_name_by_dn(self.user, self.user.residence_dn)
        #end if

        return { 
            "user" : self.user, 
            "residence" : residence,
            "groups_ldap" : groups, 
            "all_users" : all_users 
        }
    #end def
#end class

