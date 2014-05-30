from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.lib.base import BaseController

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.model.ldap import *

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController

class RoomsController(AuthenticatedBaseController):
    require_group = groups_enum.admin


    __default_color = "ok_color"
    __error_colors = {
        "PAS PAYE" : "non_paye_color",
        "CERTIF" : "non_certif_color",
        "VIDE" : "vide_color"
    }
    
    
    def color_picker(self, description):
        for color in self.__error_colors.iteritems():
            if color[0] in description:
                return color[1]
            #end if
        #end for

        return self.__default_color
    #end def

    def reverse_sort_name(self, name_items):
        return sorted(name_items, key=lambda t:t[0].cn.first(), reverse=True)

    def sort_name(self, name_items):
        return sorted(name_items, key=lambda t:t[0].cn.first())        

    @expose("brie.templates.rooms.index")
    def index(self, residence_name):
        status = dict()
        areas = dict()
        print str(datetime.datetime.now()) + "RoomsIndex0"
        residence_dn = Residences.get_dn_by_name(self.user, residence_name)
        if residence_dn is None:
            raise Exception("unknown residence")
        #end if

        current_year = CotisationComputes.current_year()
        cotisations_year = Cotisation.get_all_cotisation_by_year(self.user, residence_dn, current_year)
        print str(datetime.datetime.now()) + "RoomsIndex1 - cotis"
        stats = CotisationComputes.members_status_from_list_cotisations(self.user, residence_dn, cotisations_year)
        print str(datetime.datetime.now()) + "RoomsIndex2 - cotisComput"
        members = dict()
        members_entries = Member.get_all(self.user, residence_dn)
        print str(datetime.datetime.now()) + "RoomsIndex3 - members"
        members_entries_dict = dict()
        for member in members_entries:
            members_entries_dict[member.dn] = member
        #end for
        for label in stats:
            liste = []
            for member_dn in stats[label]:
                members[member_dn] = label
                liste.append(member_dn)
            #end for member
            for item in liste:
                stats[label].remove(item)
                stats[label].append(members_entries_dict[item])
            #end for item liste
        #end for stats
            

        stats['number_of_rooms'] = Room.get_number_of_rooms(self.user, residence_dn)
        stats['empty_rooms'] = []

        print str(datetime.datetime.now()) + "RoomsIndex4"

        myResidence = self.user.ldap_bind.get_childs(ldap_config.room_base_dn + residence_dn);
        for batKey, bat in myResidence.childs.iteritems():
            if 'pacateriearea' in bat.objectClass.all() or 'pacaterieArea' in bat.objectClass.all():
                areas[bat.value] = dict()

                for floorKey, floor in bat.childs.iteritems():
                    if 'pacateriefloor' in floor.objectClass.all() or 'pacaterieFloor' in floor.objectClass.all():
                        areas[bat.value][floor.value] = list()

                        for roomKey, room in floor.childs.iteritems():
                            if 'pacaterieroom' in room.objectClass.all() or 'pacaterieRoom' in room.objectClass.all():
                                if not room.has("x-memberIn"):
                                    stats['empty_rooms'].append(room)
                                    room.add('status', "empty_room")
                                elif room.get("x-memberIn").first() in members:
                                    room.add('status', members[room.get("x-memberIn").first()])
                                #endif

                                areas[bat.value][floor.value].append(room)

                                color = self.color_picker("foobar")
                                if color in status:
                                    status[color] = status[color] + 1
                                else:
                                    status[color] = 0
                                #end if
                            #end if room
                        #end for room
                    #end if floor
                #end for floor
            #end if area
        #end for area

        return {
            "user" : self.user,
            "areas" : areas, 
            "color_picker" : self.color_picker, 
            "reverse_sorted_name" : self.reverse_sort_name, 
            "sorted_name" : self.sort_name, 
            "stats" : stats, 
            "status" : status, 
            "residence" : residence_name
        }
    #end def        

    @expose("brie.templates.rooms.index")
    def preview(self, residence, number):
        if not number.isdigit(): redirect("/rooms/" + residence)
    
        index_result = self.index(residence) 

        residence_dn = Residences.get_dn_by_name(self.user, residence)
        room = Room.get_by_uid(self.user, residence_dn, number)


        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())
        

        preview = member, room
        index_result["preview"] = preview
    
        return index_result
    #end def
