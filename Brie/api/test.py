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

