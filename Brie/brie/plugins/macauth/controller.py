from tg.decorators import expose

from brie.model.ldap import Machine

class Macauth:

    @staticmethod
    @expose("")
    def add_machine(user, residence, models):
        print user
        print residence
        print models

        machine_dn = models["machine_dn"]
        mac = models["mac"].replace(":", "")
        name = models["name"]

        mac_dn = "cn=mac_auth," + machine_dn
        mac_attr = Machine.auth_attr(mac)
        user.ldap_bind.add_entry(mac_dn, mac_attr)

        return {}
    #end def
#end class
