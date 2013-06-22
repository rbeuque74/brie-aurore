# -*- coding: utf-8 -*-
import unicodedata


class Translations(object):
    
    @staticmethod
    def to_uid(name, surname):
        clean_name =  Translations.strip_accents(name.replace(" ", "")).lower()[:15]
        clean_surname = Translations.strip_accents(surname.replace(" ", "")).lower()[:15]

        return clean_name + "." + clean_surname
    #end def

    @staticmethod
    def floor_of_room(room):
        return room / 100
    #end def

    @staticmethod
    def area_of_room(room):
        if Translations.floor_of_room(room) == 5:
            return "crous"
    
        floor_number = room % 100
        
        if floor_number <= 33: 
            return "sud"
        else:
            return "nord"
        #end if
    #end def

#end class
        
        

    # http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    @staticmethod
    def strip_accents(s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    #end def
