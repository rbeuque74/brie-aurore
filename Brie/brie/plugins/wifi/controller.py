from tg.decorators import expose


class Wifi:
    
    @staticmethod
    @expose("brie.plugins.wifi.show")
    def show(models):
        return {
            "name" : "wifi"
        }
    #end def

#end class
