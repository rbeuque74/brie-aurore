# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

from operator import itemgetter


class GroupAddMemberController(AuthenticatedRestController):
    
    @expose()
    def post(self, group_cn, user_dn):
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

        redirect("/administration/")
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

        return { "user" : self.user, "groups_ldap" : groups, "all_users" : all_users }
    #end def
#end class

