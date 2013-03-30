from tg.decorators import expose


class Wifi:
    
    @staticmethod
    @expose("brie.plugins.wifi.show")
    def show(models):
        return {
            "activated" : str("Todo")
        }
    #end def

#end class
