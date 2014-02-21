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
       
        print "here 1"
 
        residence_dn = Residences.get_dn_by_name(self.user, residence_name)
        if residence_dn is None:
            raise Exception("unknown residence")
        #end if

        print "here 1 bis"

        stats = CotisationComputes.members_status_from_residence(self.user, residence_dn)
        print "here 2"
      
        members = dict()
        for label in stats:
            for member in stats[label]:
                members[member.dn] = label
            #end for member
        #end for stats

        print "here 3"

        stats['number_of_rooms'] = Room.get_number_of_rooms(self.user, residence_dn)
        stats['empty_rooms'] = []

        print "here 4"

        for area in Room.get_areas(self.user, residence_dn):
            areas[area] = dict()

            for floor in Room.get_floors(self.user, area.dn):
                areas[area][floor] = list()

                for room in Room.get_rooms_of_floor(self.user, floor.dn):
                    if not room.has("x-memberIn"):
                        stats['empty_rooms'].append(room)
                        room.add('status', "empty_room")
                    elif room.get("x-memberIn").first() in members:
                        room.add('status', members[room.get("x-memberIn").first()])
                    #endif

                    areas[area][floor].append(room)


                    color = self.color_picker("foobar")
                    if color in status:
                        status[color] = status[color] + 1
                    else:
                        status[color] = 0
                    #end if

                #end for room
            #end for floor
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
