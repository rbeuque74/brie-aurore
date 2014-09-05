# -*- coding: utf-8 -*-
from tg.decorators import expose
from tg.controllers import redirect

from brie.config import ldap_config, groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.name_translation_helpers import Passwords
from brie.lib.smtp_helper import SmtpHelper
from brie.model.ldap import *

from brie.model.ldap import Wifi as WifiModel

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController


class Wifi:
    
    @staticmethod
    @expose("brie.plugins.wifi.show")
    def show(models):
        member = models["member_ldap"]
        user = models["user"]

        wifi = WifiModel.get_by_member_dn(user, member.dn)

        return {
            "activated" : str(wifi is not None)
        }
    #end def

#end class

class DirectController(AuthenticatedRestController):
    require_group = groups_enum.respsalleinfo

    @expose("brie.plugins.wifi.edit")
    def get(self, residence, member_uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        if member is None:
            raise Exception("invalid member uid")
        
        return {
            "user" : self.user,
            "residence" : residence,
            "member_ldap" : member
        } 

    #end def


    @expose("")
    def post(self, residence, member_uid):
        residence_dn = Residences.get_dn_by_name(self.user, residence)
        member = Member.get_by_uid(self.user, residence_dn, member_uid)
        if member is None:
            raise Exception("invalid member uid")
        

        wifi = WifiModel.get_by_member_dn(self.user, member.dn)
        password = Passwords.generate_password_wifi()

        if wifi is None:
            wifi_dn = "cn=wifi," + member.dn
            wifi_attr = WifiModel.entry_attr(password)
            self.user.ldap_bind.add_entry(wifi_dn, wifi_attr) 
        else:
            wifi.userPassword.replace(wifi.userPassword.first(), password)
            self.user.ldap_bind.save(wifi)
        #end

        # Envoi du mail
        from_address = [u'Fédération Aurore', 'noreply@fede-aurore.net']
        recipient = [member.cn.first(), member.mail.first()]
        subject = u'['+ residence +'] votre mot de passe WiFi'
        text = u'Bonjour,\n\nVous venez de vous inscrire au sein d\'une résidence de la fédération Aurore\nUn mot de passe pour utiliser la connexion WiFi de la résidence vous a été assigné.\n\nUtilisateur: '+ member_uid +'\nMot de passe: '+ password +u'\n\nCordialement,\nla fédération Aurore'
        
        SmtpHelper.send_email(from_address, recipient, subject, text)

        redirect("/show/member/" + residence + "/" + member_uid)
    #end def
#end class
