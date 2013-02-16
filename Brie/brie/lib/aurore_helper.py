from brie.config import ldap_config

class Residences:
    
    @staticmethod
    def get_dn_by_name(user_session, name):
        result = user_session.ldap_bind.search_first(ldap_config.liste_residence_dn, "(cn=" + name + ")")

        if result is None:
            return None
        #end if

        return result.uniqueMember.first()
    #end def

    @staticmethod
    def get_name_by_dn(user_session, dn):
        result = user_session.ldap_bind.search_first(ldap_config.liste_residence_dn, "(uniqueMember=" + dn + ")")

        if result is None:
            return None
        #end if
        
        return result.cn.first()
    #end def
    
    @staticmethod
    def get_residences(user_session):
        return user_session.ldap_bind.search(ldap_config.liste_residence_dn, "(objectClass=groupOfUniqueNames)")
    #end def
#end class
        
