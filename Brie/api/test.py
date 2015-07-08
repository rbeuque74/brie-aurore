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
print(rb.getDn(), rb.getPrenom(), rb.getNom(), rb.getMail())

membres = Membre.getAll(brie, eminet)
print(membres)
print(rb.toLdapObject())
print(membres[-1].toLdapObject())

import time
rb.setMobile(int(time.time()))
rb.save(brie)
print("ok")
