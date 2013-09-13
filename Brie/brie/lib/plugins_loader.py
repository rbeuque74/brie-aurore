
class PluginsPackage:
    def __init__(self, controllers_dict):
        self.__dict__ = controllers_dict
#end class

def load():
    plugins_import = __import__("brie.plugins")

    controllers_dict = dict()
    for sub_package in plugins_import.plugins.__all__:
        controller_import = __import__("brie.plugins." + sub_package + ".controller")
        controllers_dict[sub_package] = controller_import.plugins.__dict__[sub_package].controller
    #end for

    return PluginsPackage(controllers_dict)
#end def
