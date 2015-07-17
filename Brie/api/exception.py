# -*- coding: utf-8 -*-

class BrieException(Exception):
    pass

class BrieLdapConnectionException(BrieException):
    pass

class BrieConnectionException(BrieException):
    pass

class BrieNotFoundException(BrieException):
    pass

