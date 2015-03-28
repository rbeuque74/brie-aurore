# -*- coding: utf-8 -*-
import unicodedata
from random import randint
from os import urandom
from binascii import b2a_hex
import re

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

    # http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    @staticmethod
    def strip_accents(s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    #end def

    @staticmethod
    def formatName(value):
        """
        Converts to ASCII. Converts spaces to hyphens. Removes characters that
        aren't alphanumerics, underscores, or hyphens. Converts to lowercase.
        Also strips leading and trailing whitespace.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
    #end def

#end class

class Passwords(object):

    @staticmethod
    def generate_password_wifi():

        password = ""

        for i in range(8):
            nb_chosen = randint(0,35)
            if nb_chosen > 25:
                password = password + str(nb_chosen - 26)
            else:
                if randint(0,1) is 1:
                    password = password + chr(ord('A') + nb_chosen)
                else:
                    password = password + chr(ord('a') + nb_chosen)
                #end if
            #end if
        #end for
        return password
    #end def

    @staticmethod
    def generate_password_admin():
        return b2a_hex(urandom(4))

#end class

