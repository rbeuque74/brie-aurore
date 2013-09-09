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
	
	@expose("brie.templates.members.index")
	def index(self, residence_name):
		members = list();

		residence_dn = Residences.get_dn_by_name(self.user, residence_name)
		if residence_dn is None:
			raise Exception("unknown residence")
		#end if

		for member in Member.get_all(self.user, residence_dn):
			members.append(member);

		rooms = Room.get_rooms(self.user, residence_dn)
		if rooms is None:
			raise Exception("unable to retrieve rooms")
		#end if
		rooms = sorted(rooms, key=lambda t:t.uid.first())

		for m in members:
			for r in rooms:
				if r.has("x-memberIn"):
					if r.get("x-memberIn").first() == m.dn:
						m.room = r


		return {
                        "user" : self.user,
			"members" : members, 
			"residence" : residence_name,
                        "sort_name" : MembersController.sort_name
		}
	#end def

#        @expose("brie.templates.members.index")
#        def search(self, residence_name, query)
#            responses = index(self, residence_name)

#            retu
                


