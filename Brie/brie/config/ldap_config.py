# -*- coding: utf-8 -*-

uri = "ldaps://localhost"

username_base_dn = "ou=membres,"
room_base_dn = "ou=chambres,"
group_base_dn = "ou=groupes,"
parametres_base_dn = "ou=parametres,"
machine_base_dn = "cn=machines,"
cotisation_member_base_dn = "cn=cotisations,"
ip_reservation_base_dn = "uid=pool_ip," + parametres_base_dn
plugins_base_dn = "uid=plugins," + parametres_base_dn

cotisation_base_dn = "uid=cotisation," + parametres_base_dn
cotisation_annee_base_dn = "uid=annee," + cotisation_base_dn
cotisation_mois_base_dn = "uid=mois," + cotisation_base_dn

extra_base_dn = "uid=paiements-extras," + parametres_base_dn

aurore_dn = "dc=aurore,dc=u-psud,dc=fr"
parametres_aurore_dn = parametres_base_dn + aurore_dn 

liste_residence_dn = "cn=residences," + parametres_aurore_dn

