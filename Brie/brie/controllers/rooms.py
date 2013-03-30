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

from operator import itemgetter


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
        return sorted(name_items, key=itemgetter(0), reverse=True)

    def sort_name(self, name_items):
        return sorted(name_items, key=itemgetter(0))

    @expose("brie.templates.rooms.index")
    def index(self, residence_name):
        stats = dict()
        areas = dict()
        
        residence_dn = Residences.get_dn_by_name(self.user, residence_name)
        if residence_dn is None:
            raise Exception("unknown residence")
        #end if

        for area in Room.get_areas(self.user, residence_dn):
            areas[area] = list()

            for floor in Room.get_floors(self.user, area.dn):
                areas[area][floor] = list()

                for room in Room.get_rooms_of_floor(self.user, floor.dn):
                    areas[area][floor].append(room)


                    color = self.color_picker("foobar")
                    if color in stats:
                        stats[color] = stats[color] + 1
                    else:
                        stats[color] = 0
                    #end if

                #end for room
                areas[area][floor] = sorted(areas[area][floor], key=lambda r:r.cn.first())
            #end for floor
            areas[area] = sorted(areas[area].items(), key=lambda t:t[0])
        #end for area

        return {
            "areas" : areas, 
            "color_picker" : self.color_picker, 
            "reverse_sorted_name" : self.reverse_sort_name, 
            "sorted_name" : self.sort_name, 
            "stats" : stats, 
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
