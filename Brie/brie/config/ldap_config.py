# -*- coding: utf-8 -*-

uri = "ldaps://172.17.31.4"

username_base_dn = "ou=membres,"
room_base_dn = "ou=chambres,"
group_base_dn = "ou=groupes,"

aurore_dn = "dc=aurore,dc=u-psud,dc=fr"
parametres_aurore_dn = "ou=parametres," + aurore_dn 
liste_residence_dn = "cn=residences," + parametres_aurore_dn
