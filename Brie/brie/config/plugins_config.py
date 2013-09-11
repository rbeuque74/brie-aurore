from brie.plugins.wifi.controller import *
from brie.plugins.unix.controller import *
from brie.plugins.macauth.controller import *

mappings = {
    "brie.controllers.show.member" : [
        ("wifi", Wifi.show),
        ("unix", Unix.show)
    ],
    "brie.controllers.edit.machine.post" : [
        ("macauth", Mac_auth.add_machine)
    ]
}
