import brie.lib.plugins_loader as plugins_loader

plugins = plugins_loader.load()

mappings = {
    "brie.controllers.show.member" : [
        plugins.wifi.Wifi.show,
        plugins.unix.Unix.show
    ],
    "brie.controllers.edit.machine.post" : [
        plugins.macauth.Macauth.add_machine
    ]
}
