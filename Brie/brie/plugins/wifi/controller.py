# -*- coding: utf-8 -*-
from tg.decorators import expose
from tg.controllers import redirect

from brie.config import ldap_config, groups_enum
from brie.lib.ldap_helper import *
from brie.lib.aurore_helper import *
from brie.lib.name_translation_helpers import Passwords
from brie.model.ldap import *

from brie.model.ldap import Wifi as WifiModel

from brie.controllers import auth
from brie.controllers.auth import AuthenticatedBaseController, AuthenticatedRestController
import smtplib


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

        sender = "noreply@fede-aurore.net"
        receivers = [member.mail.first()]
        
        message = """From: Federation Aurore <noreply@fede-aurore.net>
To: """ + member.cn.first().decode("utf-8").encode("ascii", "ignore") + """ <""" + member.mail.first().decode("utf-8").encode("ascii", "ignore") + """> 
Subject: Votre mot de passe WiFi : residence universitaire

        Bienvenue dans votre residence etudiante de Paris Sud

        Votre nom de connexion est : """ + member_uid + """
        Votre mot de passe WiFi est : """ + password

        message = message.encode("utf-8")

        try:
           smtpObj = smtplib.SMTP('smtp.u-psud.fr')
           smtpObj.sendmail(sender, receivers, message)         
           print "Successfully sent email"
        except SMTPException:
           print "Error: unable to send email"

        redirect("/show/member/" + residence + "/" + member_uid)
    #end def
#end class
