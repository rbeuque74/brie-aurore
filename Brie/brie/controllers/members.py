from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.lib.base import BaseController

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *

import datetime

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

class MembersController(AuthenticatedBaseController):
	require_group = groups_enum.admin

        @staticmethod
	def sort_name(name_items):
		return sorted(name_items, key=lambda t:t.sn.first())        
	
	@expose("brie.templates.search.member")
	def index(self, residence_name):
		residence_dn = Residences.get_dn_by_name(self.user, residence_name)
		if residence_dn is None:
			raise Exception("unknown residence")
		#end if

		members = Member.get_all(self.user, residence_dn)
                members = MembersController.sort_name(members)

                members_rooms = [
                        (member, Room.get_by_member_dn(self.user, residence_dn, member.dn))
                        for member in members
                ]

                #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
                #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

                return { 
                    "residence" : residence_name, 
                    "user" : self.user,  
                    "members_rooms" : members_rooms
                }

	#end def

#        @expose("brie.templates.members.index")
#        def search(self, residence_name, query)
#            responses = index(self, residence_name)

#            retu
                


