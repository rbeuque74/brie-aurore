from brie.plugins.wifi.controller import *
from brie.plugins.shell.controller import *

mappings = {
    "brie.controllers.show.member" : [
        ("wifi", Wifi.show),
        ("shell", Shell.show)
    ]
}
