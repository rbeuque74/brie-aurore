import brie, getpass
password = getpass.getpass()
brie = brie.Brie("romain.beuque", password, "test-Pac@Net")
from residence import Residence
eminet = Residence.getResidenceByName(brie, "test-Pac@Net")
import machine, membre
from pprint import pprint, pformat

input=raw_input()
while input != "":
    try:
        exec(input)
    except Exception as e:
        print(e)
    input = raw_input()
