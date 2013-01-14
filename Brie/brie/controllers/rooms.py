from tg import session
from tg.controllers import redirect
from tg.decorators import expose, validate
from brie.lib.base import BaseController

from brie.lib.camembert_helpers import *

from brie.config import ldap_config
from brie.config import groups_enum
from brie.lib.ldap_helper import *
from brie.model import DBSession
from brie.model.camembert import *
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
    def index(self):
        result = DBSession.query(Interface)
        
        interfaces_dict = dict()
        for interface in result:
            interfaces_dict[str(interface.idinterface)] = interface

        stats = dict()
        areas = dict()

        rooms = self.user.ldap_bind.search(ldap_config.room_base_dn, ldap_config.room_filter)

        rooms = sorted(rooms, key = lambda a: a.cn.first())
        for room in rooms:
            interface = interfaces_dict[room.get("x-switchInterface").first()]

            color = self.color_picker(interface.ifdescription)
            if color in stats:
                stats[color] = stats[color] + 1
            else:
                stats[color] = 0
            #end if

            room_id = int(room.uid.first())
            floor = Translations.floor_of_room(room_id)
            area = Translations.area_of_room(room_id)

            if area not in areas:
                areas[area] = dict()
            #end if
        
            if floor not in areas[area]:
                areas[area][floor] = []
            #end if

            areas[area][floor].append((room, interface))
        #end for

        return { "areas" : areas, "color_picker" : self.color_picker, "reverse_sorted_name" : self.reverse_sort_name, "sorted_name" : self.sort_name, "stats" : stats}
    #end def        

    @expose("brie.templates.rooms.index")
    def preview(self, number):
        if not number.isdigit(): redirect("/rooms/")
    
        index_result = self.index() 

        room = Room.get_by_uid(self.user, number)


        member = None
        if room.has("x-memberIn"):
            member = Member.get_by_dn(self.user, room.get("x-memberIn").first())
        

        interface = (
            DBSession.query(Interface)
                .filter(Interface.idinterface == room.get("x-switchInterface").first())
                .first()
        )

        preview = member, room, interface       
        index_result["preview"] = preview
    
        return index_result
    #end def
