# -*- coding: utf-8 -*-

uri = "ldaps://172.17.31.4"

base_dn = "dc=pacaterie,dc=u-psud,dc=fr"

username_base_dn = "ou=membres," + base_dn

room_base_dn = "ou=chambres," + base_dn

group_base_dn = "ou=groupes," + base_dn

area_filter = "(objectClass=pacateriearea)"
floor_filter = "(objectClass=pacateriefloor)"
room_filter = "(objectClass=pacaterieRoom)"
