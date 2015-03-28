# -*- coding: utf-8 -*-

import uuid
import re
import ldap

class Membre(object):
	"""Classe modelisant les membres"""
	def __init__(self, uid, prenom, nom):
		super(Membre, self).__init__()
		
		