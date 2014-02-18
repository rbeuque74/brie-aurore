# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.plugins import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController
from brie.controllers.members import MembersController

from operator import itemgetter

""" Controller de recherche """ 
class SearchController(AuthenticatedBaseController):

    @expose("brie.templates.search.error")
    def error_no_entry(self):
        return { "error" : "Entrée non existante" }

    """ Affiche les résultats """
    @expose("brie.templates.search.member")
    def member(self, residence, name):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    
        members = Member.get_by_name(self.user, residence_dn, name)

        if members is None:
            return self.error_no_entry()
        
        members = MembersController.sort_name(members)

        members_rooms = [
            (member, Room.get_by_member_dn(self.user, residence_dn, member.dn))
            for member in members
        ]

    #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
    #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)

        return { 
            "residence" : residence, 
            "user" : self.user,  
            "members_rooms" : members_rooms
        }
    #end def


    @expose("brie.templates.search.member")
    def email(self, residence, email):
        residence_dn = Residences.get_dn_by_name(self.user, residence) 
        members = Member.get_by_email(self.user, residence_dn, email)

        if members is None:
            return self.error_no_entry()
        
        members = MembersController.sort_name(members)

        members_rooms = [
            (member, Room.get_by_member_dn(self.user, residence_dn, member.dn))
            for member in members
        ]

    #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
    #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)
        return { 
            "residence" : residence, 
            "user" : self.user,  
            "members_rooms" : members_rooms
        }
    #end def


    @expose("brie.templates.search.member")
    def mac(self, residence, mac):
        residence_dn = Residences.get_dn_by_name(self.user, residence) 
        machine = Machine.get_dhcp_by_mac(self.user, residence_dn, mac)

        if machine is None:
            return self.error_no_entry()
        
        machine = machine.dn.split(',')

        i = 0
        member_dn = ""
        for sub in machine:
            if i >= 3:
                if member_dn != "":
                    member_dn += ","
                #end if
                member_dn += sub
            #end if
            i += 1
        #end for

        member = Member.get_by_dn(self.user, member_dn)

        if member is None:
            return self.error_no_entry()
        #end if

        redirect("/show/member/"+ residence +"/" + member.uid.first())
    #end def


    @expose("brie.templates.search.ip")
    def ip(self, residence, ip):
        residence_dn = Residences.get_dn_by_name(self.user, residence) 
        machines = Machine.get_dns_by_ip(self.user, residence_dn, ip)

        if len(machines) == 0:
            return self.error_no_entry()
        
        results = []

        for machine in machines:
            membre_dn = machine.dn.split(',')

            i = 0
            member_dn = ""
            for sub in membre_dn:
                if i >= 3:
                    if member_dn != "":
                        member_dn += ","
                    #end if
                    member_dn += sub
                #end if
                i += 1
            #end for

            member = Member.get_by_dn(self.user, member_dn)
            if member is None:
                return self.error_no_entry()
            #end if

            if len(machines) == 1:
                redirect("/show/member/"+ residence +"/"+ member.uid.first())
            #end if

            results.append((member, machine))
        #end for

        return { 
            "residence" : residence,
            "user" : self.user,  
            "results" : results
        }
    #end def


    @expose("brie.templates.search.member_global")
    def member_global(self, myresidence, name):
        residences = Residences.get_residences(self.user)
        members = []
        for residence in residences:
            residence_dn = Residences.get_dn_by_name(self.user, residence.cn.first())
            members_res = Member.get_by_name(self.user, residence_dn, name)
            for member in members_res:
                members.append((member, residence_dn))
            #end for
        #end for

        if members is None:
            return self.error_no_entry()
        
#        members = MembersController.sort_name(members)

        members_rooms = [
            (member, Room.get_by_member_dn(self.user, residence_dn, member.dn), Residences.get_name_by_dn(self.user, residence_dn))
            for member, residence_dn in members
        ]

    #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
    #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)
        return { 
            "residence" : myresidence,
            "user" : self.user,  
            "members_rooms" : members_rooms
        }
    #end def


    @expose("brie.templates.search.member_global")
    def email_global(self, myresidence, email):
        residences = Residences.get_residences(self.user)
        members = []
        for residence in residences:
            residence_dn = Residences.get_dn_by_name(self.user, residence.cn.first())
            members_res = Member.get_by_email(self.user, residence_dn, email)
            for member in members_res:
                members.append((member, residence_dn))
            #end for
        #end for

        if members is None:
            return self.error_no_entry()
        
#        members = MembersController.sort_name(members)

        members_rooms = [
            (member, Room.get_by_member_dn(self.user, residence_dn, member.dn), Residences.get_name_by_dn(self.user, residence_dn))
            for member, residence_dn in members
        ]

    #    machines = Machine.get_machine_tuples_of_member(self.user, member.dn)
    
    #    groups = Groupes.get_by_user_dn(self.user, residence_dn, member.dn)
        return { 
            "residence" : myresidence,
            "user" : self.user,  
            "members_rooms" : members_rooms
        }
    #end def


    @expose("brie.templates.show.room")
    def room(self, residence, room_id):
        residence_dn = Residences.get_dn_by_name(self.user, residence)    

        room = Room.get_by_uid(self.user, residence_dn, room_id)

        if room is None:
            return self.error_no_entry()

        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())
        
        return { 
            "residence" : residence,
            "user" : self.user, 
            "room_ldap" : room, 
            "member_ldap" : member 
        }        
    #end def

#end class
        
