# -*- coding: utf-8 -*-
import brie, getpass
from pprint import pprint
password = getpass.getpass()
brie = brie.Brie("romain.beuque", password, "Eminet")
pprint(brie)
from residence import Residence
eminet = Residence.getResidenceByName(brie, "Eminet")
pprint(eminet)
from membre import Membre
rb = Membre.getByUid(brie, "romain.beuque", eminet)
pprint(rb)
print(rb.getDn(), rb.getPrenom(), rb.getNom(), rb.getMail(), rb.getComment())

#membres = Membre.getAll(brie, eminet)
#print(membres)

import time
rb.setMobile(int(time.time()))
rb = Membre.getByUid(brie, "romain.beuque", eminet)
rb.save(brie)
print("ok")
print(Membre.getByUid(brie, "romain.beuque", eminet).getMobile())
#rb.getChilds(brie)
from machine import Machine
pprint(Machine.get_machine_tuples_of_member(brie, rb))
#pprint(machine.Machine.get_machine_from_mac(brie, "c8:f7:33:cd:8a:66", eminet))
#pprint(machine.Machine.get_machine_from_ip(brie, "172.17.12.93", eminet))
#pprint(machine.Machine.get_machine_from_ip(brie, "172.17.13.118", eminet))
#pprint(machine.Machine.get_machine_from_ip(brie, "172.17.14.20", eminet))
#pprint(machine.Machine.get_machine_from_ip(brie, "172.17.14.254", eminet))
