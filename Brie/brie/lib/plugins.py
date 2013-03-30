# -*- coding: utf-8 -*-
import tg
from brie.config import plugins_config
from decorator import decorator
from tg.decorators import Decoration

from brie.lib.aurore_helper import *
from brie.model.ldap import Plugins


""" Classe permettant d'utiliser les resultats dictionnaires d'un plugin
    comme une classe (à la manière des LdapResult). 
    e.g.
        au lieu de shell_show["uid"] on utilise comme : shell_show.uid
"""
class PluginVars:
    def __init__(self, vars_dict):
        self.__dict__ = vars_dict
    #end def
#end class


""" Decorateur plugin, execute toutes les fonctions du scope donné """
def plugins(scope):
    def plugin(f, *args, **kw):
        results_dict = f(*args, **kw)
        user = args[0].user
        residence_var = "residence"
       
        plugins_templates = list()

        # un plugin est defini pour le scope et residence est defini 
        if scope in plugins_config.mappings and residence_var in results_dict:
            residence_dn = Residences.get_dn_by_name(user, results_dict[residence_var])

            scope_mappings = plugins_config.mappings[scope]
            
            for plugin_name, function in scope_mappings:
                plugin_activated = Plugins.get_by_name(user, residence_dn, plugin_name)

                if plugin_activated is None:
                    continue
                #end if

                template_name = None

                # obtenir le nom du template à partir du decorator "expose"
                deco = Decoration.get_decoration(function)
                try:
                    template_name = deco.engines["text/html"][1]
                except:
                    pass

                if template_name is not None:
                    # transformer le nom de template en chemin fichier
                    template_path = (
                        tg.config['pylons.app_globals']
                          .dotted_filename_finder
                          .get_dotted_filename(template_name, template_extension='.html')
                    )

                    # ajouter dans les plugin templates
                    plugins_templates.append(template_path)
                #end if

                # executer la fonction du plugin
                mapping_results = function(results_dict)

                # constuire le nom de regroupement des variable de ce plugin
                method_name = function.__name__
                plugin_section = str.lower(plugin_name + "_" + method_name)

                # ajout du groupe au dictionnaire de la methode du controlleur
                results_dict[plugin_section] = PluginVars(mapping_results)
            #end for

        #end if

        # ajout des templates dans un champs spécial du dictionnaire pour le rendu
        results_dict["_plugins_templates"] = plugins_templates

        return results_dict
    #end def

    return decorator(plugin)
#end def
