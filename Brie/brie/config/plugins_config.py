from brie.plugins.wifi.controller import *
from brie.plugins.unix.controller import *

mappings = {
    "brie.controllers.show.member" : [
        ("wifi", Wifi.show),
        ("unix", Unix.show)
    ]
}
