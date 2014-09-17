from apscheduler.scheduler import Scheduler

from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.log_helper import BrieLogging
from brie.model.ldap import *
import sys
import datetime
import brie.config.credentials as credentials


def admin_user():
    bind = Ldap.connect(credentials.scheduler_user, credentials.scheduler_pass)
    dn = "dc=aurore,dc=u-psud,dc=fr"

    user = User(bind,None, dn)
    result = Member.get_by_dn(user, "uid=admin,ou=Administrators,ou=TopologyManagement,o=netscaperoot")
    user.attrs = result

    return user
#end def

sched = Scheduler()

def disconnect_members_from_residence(admin_user, residence_dn):
    members =  Member.get_all_non_admin(admin_user, residence_dn)
    BrieLogging.get().debug(CotisationComputes.current_year())
    date_actuelle = datetime.datetime.now()

    for member in members:
        
        machines_tuples = Machine.get_machine_tuples_of_member(admin_user, member.dn)
        if machines_tuples != []:
            
            if not CotisationComputes.is_cotisation_paid(member.dn, admin_user, residence_dn):
                dhcps = Machine.get_dhcps(admin_user, member.dn)
                machine_membre_tag = "machine_membre" # FIXME move to config

                for dhcp_item in dhcps:
                    if dhcp_item.uid.first() == machine_membre_tag:
                        BrieLogging.get().info("scheduler disable machine " + dhcp_item.get("dhcpHWAddress").values[0] + " pour l'utilisateur "+ member.dn + " -- "+ dhcp_item.dn)
                        dhcp_item.uid.replace(machine_membre_tag, machine_membre_tag + "_disabled")
                        admin_user.ldap_bind.save(dhcp_item)
                    #end if
                #end for
            #end if
            
        #end if
        if CotisationComputes.is_member_to_delete(member, admin_user, residence_dn):
            # supprime les machines mais pas le membre (il pourrait avoir besoin du compte ex : Yohan, le LDAP d'Aurores, etc)
            # alors test a ajouter pour ne supprimer que si membre d'aucun groupe
            # duplication de code avec class MachineDeleteController
            machine_dn = ldap_config.machine_base_dn + member.dn
            machines = admin_user.ldap_bind.search(machine_dn, "(objectClass=organizationalRole)", scope = ldap.SCOPE_ONELEVEL)
            for machine in machines:
                    dns = Machine.get_dns_by_id(admin_user, machine.dn)
                    if dns is None:
                        BrieLogging.get().info("Suppression machine erreur (dns is None): " + machine.dn)
                        continue
                    #end if
                    ip = IpReservation.get_ip(admin_user, residence_dn, dns.dlzData.first())
                    BrieLogging.get().info("suppression machine " + Machine.get_dhcps(admin_user, machine.dn)[0].get("dhcpHWAddress").values[0] + " pour l'utilisateur "+ member.dn + " par le scheduler")
                    #sys.stdout.flush()
                    admin_user.ldap_bind.delete_entry_subtree(machine.dn)
                    if ip is not None:
                        taken_attribute = ip.get("x-taken").first()
                        if taken_attribute is not None:
                            BrieLogging.get().debug("deleting taken_attribute for this IP address")
                            admin_user.ldap_bind.delete_attr(ip.dn, IpReservation.taken_attr(taken_attribute))
                        #end if
                    #end if
            #end for
        #end if

    #end for
            
#end def

@sched.interval_schedule(days=1, start_date="2013-09-30 22:14:37")
#@sched.interval_schedule(minutes=1, start_date="2013-09-30 22:14:37")
def disconnect_members_job():
    user = admin_user()
     
    residences = Residences.get_residences(user)

    for residence in residences:
        BrieLogging.get().info("Disconnect job on : " + residence.uniqueMember.first())
        try:
            disconnect_members_from_residence(user, residence.uniqueMember.first())
        except Exception as inst:
            BrieLogging.get().info("Exception sur le scheduler ("+ residence.uniqueMember.first() +")")
            BrieLogging.get().debug(type(inst))
    #end for

#    user.ldap_bind.disconnect()
#end def

