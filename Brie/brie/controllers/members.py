from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.lib.base import BaseController

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *
from brie.lib.name_translation_helpers import Translations

from datetime import datetime

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

class MembersController(AuthenticatedBaseController):
	require_group = groups_enum.admin

	member_edit_controller = None

	def __init__(self, member_edit_controller):
		self.member_edit_controller = member_edit_controller

	@staticmethod
	def sort_name(name_items):
		return sorted(name_items, key=lambda t:t.sn.first())
	#end if

	@expose("brie.templates.search.member")
	def index(self, residence_name):
		residence_dn = Residences.get_dn_by_name(self.user, residence_name)
		if residence_dn is None:
			raise Exception("unknown residence")
		#end if

		members = Member.get_all(self.user, residence_dn)
		members = MembersController.sort_name(members)
                
                rooms = Room.get_rooms(self.user, residence_dn)
                rooms_dict = dict()
                for room in rooms:
                    if room.get("x-memberIn").first() is not None:
                        rooms_dict[room.get("x-memberIn").first()] = room
                    #end if
                #end for

                #raise Exception("ee")
                members_rooms = []
		for member in members:
                    if member.dn in rooms_dict:
                        members_rooms.append((member, rooms_dict[member.dn]))
                    else:
                        members_rooms.append((member, None))
                    #end if
                #end for

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


	@expose()
	def demenageResidence(self, member_dn):
		# Initialisation des Users des Controllers Existant appelles 
		self.member_edit_controller.machine.add.user = self.user
		self.member_edit_controller.add.user = self.user
		self.member_edit_controller.cotisation.add.user = self.user

		residence_dn = self.user.residence_dn
		residence_name = Residences.get_name_by_dn(self.user, residence_dn)

		member = Member.get_by_dn(self.user, member_dn)

		machines = Machine.get_machine_tuples_of_member(self.user, member_dn)

		current_year = CotisationComputes.current_year()
		cotisations = Cotisation.cotisations_of_member(self.user, member_dn, current_year)

		now = datetime.now()
		registration_year = CotisationComputes.registration_current_year()

		member_dn = "uid=" + member.uid.first() + ",ou=" + str(registration_year) + "," + ldap_config.username_base_dn + residence_dn
		#phone = ' '
		#if member.has('mobile'):
		#	phone = member.mobile.first()
		#member_uid = self.member_edit_controller.add.post(residence_name, member.givenName.first(), member.sn.first(), member.mail.first(), phone, False)
                
                member_new_res = Member.get_by_dn(self.user, member_dn)
                member_uid_origin = member.uid.first()
                new_member_uid = member.uid.first()
                number = 1
                while member_new_res is not None:
                    member.uid.values.remove(new_member_uid)
                    new_member_uid = member_uid_origin + number
                    member_dn = "uid=" + new_member_uid + ",ou=" + str(registration_year) + "," + ldap_config.username_base_dn + residence_dn
                    number = number + 1
                    member.uid.values.append(new_member_uid)
                    member_new_res = Member.get_by_dn(self.user, member_dn)
                #end while
 
		self.user.ldap_bind.clone_entry(member_dn, member)
		member = Member.get_by_uid(self.user, self.user.residence_dn, member.uid.first())

		folder_dn = ldap_config.cotisation_member_base_dn + member.dn
		year_dn = "cn=" + str(current_year) + "," + folder_dn

		try:
			folder = Cotisation.folder_attr()
			self.user.ldap_bind.add_entry(folder_dn, folder)
		except ldap.ALREADY_EXISTS:
			pass # OKAY
		#end try

		try:
			year = Cotisation.year_attr(current_year)
			self.user.ldap_bind.add_entry(year_dn, year)
		except ldap.ALREADY_EXISTS:
			pass # OKAY
		#end try

		for cotisation in cotisations:
			cotisation_dn = ""
			if cotisation.has("description") and cotisation.description.first() == "cotisation":
				cotisation_dn = "cn=cotisation-" 
			else:
				cotisation_dn = "cn=extra-" 
			#end if

			cotisation_dn = cotisation_dn + cotisation.get("x-time").first() + "," + year_dn
			self.user.ldap_bind.clone_entry(cotisation_dn, cotisation)
		#end for

		for machine_name, machine_mac, machine_ip, machine_disabled in machines:
			self.member_edit_controller.machine.add.post(residence_name, member.uid.first(), machine_name, machine_mac, go_redirect = False)
		#end for


		redirect("/show/member/" + residence_name + "/" + member.uid.first()) 

	#end def
#end class
