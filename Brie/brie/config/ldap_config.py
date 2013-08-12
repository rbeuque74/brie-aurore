# -*- coding: utf-8 -*-

uri = "ldaps://172.17.31.4"

username_base_dn = "ou=membres,"
room_base_dn = "ou=chambres,"
group_base_dn = "ou=groupes,"
parametres_base_dn = "ou=parametres,"
machine_base_dn = "cn=machines,"
ip_reservation_base_dn = "uid=pool_ip," + parametres_base_dn
plugins_base_dn = "uid=plugins," + parametres_base_dn

aurore_dn = "dc=aurore,dc=u-psud,dc=fr"
parametres_aurore_dn = parametres_base_dn + aurore_dn 

liste_residence_dn = "cn=residences," + parametres_aurore_dn

