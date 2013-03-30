from tg.decorators import expose

class Unix:

    @staticmethod
    @expose("brie.plugins.unix.show")
    def show(models):
        return {
        }
    #end def
#end class
