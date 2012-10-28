# -*- coding: utf-8 -*-

from tg import session
from tg.controllers import RestController, redirect
from tg.decorators import expose, validate

from brie.lib.base import BaseController
from brie.config import ldap_config
from brie.lib.ldap_helper import *
from brie.model.ldap import Groupes

class Groups(object):
    __groups = list()

    def __init__(self, groups):
        self.__groups = groups
    #end def

    def __getattr__(self, name):
        return name in self.__groups
    #end def

    def list(self):
        return list(self.__groups)
    #end def
 
#end class

class User(object):
    ldap_bind = None
    attrs = None
    groups =  None
    
    def __init__(self, ldap_bind, attrs):
        self.ldap_bind = ldap_bind
        self.attrs = attrs

        groups = Groupes.get_by_user_dn(self, self.attrs.dn)

        self.groups = Groups(groups)
    #end def
#end class

class AuthHandler(object):
    __users = dict()
    __user_session_name = "user"
    __anon_bind = None

    def get_anon_bind(self):
        if self.__anon_bind is not None:
            return self.__anon_bind
        else:
            self.__anon_bind = Ldap.connect("", "")
            return self.__anon_bind
        #end if
    #end def        
    
    def login(self, username, password):
        if self.get_anon_bind() is None:
            return False

        actual_user = self.get_anon_bind().search_first(ldap_config.username_base_dn, "(uid=" + username + ")")

        if actual_user is None:
            return False

        username_dn = actual_user.dn
        bind = Ldap.connect(username_dn, password)

        if bind is None: 
            return False

        attributes = bind.search_first(username_dn, "(uid=" + username + ")")

        user = User(bind, attributes)
        
        AuthHandler.__users[username] = user

        session[AuthHandler.__user_session_name] = username
        session.save() 

        return True
    #end def

    def logout(self):
        user = session[AuthHandler.__user_session_name]
        if user in AuthHandler.__users:
            stored_user = AuthHandler.__users[user]
            stored_user.ldap_bind.close()
            del AuthHandler.__users[user]
        #end if
        session[AuthHandler.__user_session_name] = None
        session.save()
    #end def

    def get_user(self):
        if not AuthHandler.__user_session_name in session:
            return None

        user = session[AuthHandler.__user_session_name]
        if user in AuthHandler.__users:
            return AuthHandler.__users[user]
        
        return None 
    #end def

    def get_user_or_redirect(self):
        maybe_user = self.get_user() 
        if maybe_user is None:
            redirect("/auth/login/") # TODO from config
        #end if
       
        return maybe_user
    #end def 

#end class

class AuthenticatedRestController(RestController):
    user = None

    def __before__(self, *args, **kwargs):
        self.user = current.get_user_or_redirect()
    #end def
#end def

class AuthenticatedBaseController(BaseController):
    user = None
    
    def __before__(self, *args, **kwargs):
        self.user = current.get_user_or_redirect()
    #end def
#end def

current = AuthHandler()

class LoginRestController(RestController):

    @expose("brie.templates.auth.login")
    def get(self):
        return dict(login = "", error = "")

    @expose("brie.templates.auth.login")
    def post(self, username, password):
        success = current.login(username, password)

        if success:
            redirect("/")
        #end if 

        return dict(login = username, error = "erreur de connexion")
    #end def
    

class AuthRestController(BaseController):
    login = LoginRestController() 

    @expose()
    def logout(self):
        current.logout()
        redirect("/")
#end class

    
        
         
