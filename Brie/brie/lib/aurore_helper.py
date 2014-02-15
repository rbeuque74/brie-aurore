from brie.config import ldap_config
from brie.model.ldap import *
import datetime

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

class CotisationComputes:
   
    @staticmethod
    def current_year():
       now = datetime.datetime.now()
       if now.month > 8:
           return now.year + 1

       return now.year
    #end def

    @staticmethod
    def get_available_months(start, end, paid_months = []):
        next_months_available = []

        if start > 12 or end > 12:
            raise Exception("invalid start or end")

        if start > 8 and end > 8:
            next_months_available = range(start, end + 1)
        elif start <= 8 and end < 9:
            next_months_available = range(start, end + 1)
        elif start > 8:
            next_months_available =  range(start, 13) + range(1, end + 1 )
        else:
            raise Exception("invalid start and end")
        #end if

        if paid_months == []:
            return next_months_available

        print next_months_available
        available_months = [
            month
            for month in next_months_available
            if month not in paid_months
        ]

        return available_months

    #end def

    @staticmethod
    def is_valid_month(month):
        now = datetime.datetime.now()
        if now.month > 8:
            return (month >= now.month and month < 13) or (month >= 1 and month < 9)
        else:
            return month >= now.month and month < 9
        #end if
    #end def

    @staticmethod
    def price_to_pay(year_price, month_price, already_paid, number_months_to_pay):
        
        months_price = number_months_to_pay * month_price
        print "already paid : " + str(already_paid)
        print "months price : " + str(months_price)
        if already_paid + months_price > year_price:
            months_price = max(0, year_price - already_paid)

        return months_price
    #end def

    @staticmethod
    def anniversary_from_ldap_items(ldap_cotisations):
        result = []
        months = []
        for cotisation in ldap_cotisations:
            anniversary_data = cotisation.get("x-time").first()
            anniversary_datetime = datetime.datetime.strptime(anniversary_data,
                "%Y-%m-%d %H:%M:%S.%f") 
            for month in cotisation.get("x-validMonth").all():
                months.append(int(month)) 
            #end for
            result.append((anniversary_datetime, months))
        #end for

        anniversary = 0
        # tri par ordre d'inscription
        result = sorted(result)

        if result != []:
            anniversary_day = result[0][0].day
            SORT_ORDER = {9: 0, 10: 1, 11: 2, 12: 3, 1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}
            months.sort(key=lambda val: SORT_ORDER[val])
            anniversary_month = months[-1] + 1
            if anniversary_month == 13:
                anniversary_month = 1
            if anniversary_month > 9:
                anniversary_year = result[0][0].year
            else :
                anniversary_year = result[0][0].year + 1
            anniversary = datetime.datetime.strptime(str(anniversary_year) + "-" + str(anniversary_month) + "-1 0:0", "%Y-%m-%d %H:%M") + datetime.timedelta(days=(anniversary_day - 1))
        #end if
        return anniversary
    #end def

    @staticmethod
    # old = SDF or no cotisation this year
    def is_old_member(member, user_session, residence_dn):
        current_year = CotisationComputes.current_year()
        cotisations = Cotisation.cotisations_of_member(user_session, member.dn, current_year)
        return Room.get_by_member_dn(user_session, residence_dn, member.dn) == None or cotisations == []
    #end def

    @staticmethod
    # 7 days grace period
    def is_cotisation_paid(member, user_session, residence_dn):
        if CotisationComputes.is_old_member(member, user_session, residence_dn):
            return False
        current_year = CotisationComputes.current_year()
        now = datetime.datetime.now()

        cotisations = Cotisation.cotisations_of_member(user_session, member.dn, current_year)
        anniversary = CotisationComputes.anniversary_from_ldap_items(cotisations)
        delta = (now - anniversary)
        return delta.days <= 7
    #end def

    @staticmethod
    # less than a month late but more than a week
    def is_cotisation_late(member, user_session, residence_dn):
        if CotisationComputes.is_old_member(member, user_session, residence_dn):
            return False
        current_year = CotisationComputes.current_year()
        now = datetime.datetime.now()

        cotisations = Cotisation.cotisations_of_member(user_session, member.dn, current_year)
        anniversary = CotisationComputes.anniversary_from_ldap_items(cotisations)
        delta = (now - anniversary)
        #print("[DEBUG] cotisation en retard pour l'utilisateur "+ member.dn +" now="+ str(now) +" anniversary="+ str(anniversary) +" delta="+ str(delta))
        return delta.days <= 30 and delta.days > 7
    #end def

    @staticmethod
    # more than a month late
    def is_no_cotisation(member, user_session, residence_dn):
        if CotisationComputes.is_old_member(member, user_session, residence_dn):
            return False
        current_year = CotisationComputes.current_year()
        now = datetime.datetime.now()

        cotisations = Cotisation.cotisations_of_member(user_session, member.dn, current_year)
        anniversary = CotisationComputes.anniversary_from_ldap_items(cotisations)
        delta = (now - anniversary)
        return delta.days > 30
    #end def

    @staticmethod
    def members_status_from_residence(user_session, residence_dn):
        members =  Member.get_all(user_session, residence_dn)

        old_members = []
        cotisation_paid_members = []
        cotisation_late_members = []
        no_cotisation_members = []
        for member in members:
            if CotisationComputes.is_old_member(member, user_session, residence_dn):
                old_members.append(member)
            elif CotisationComputes.is_cotisation_paid(member, user_session, residence_dn):
                cotisation_paid_members.append(member)
            elif CotisationComputes.is_cotisation_late(member, user_session, residence_dn):
                cotisation_late_members.append(member)
                #print("[DEBUG] cotisation en retard pour l'utilisateur "+ member.dn)
            elif CotisationComputes.is_no_cotisation(member, user_session, residence_dn):
                no_cotisation_members.append(member)
            else:
                print "DEBUG : member with weird status !"
            #end if

        #end for
        return dict(old_members=old_members, cotisation_paid_members=cotisation_paid_members, cotisation_late_members=cotisation_late_members, no_cotisation_members=no_cotisation_members)
    #end def

#end class
