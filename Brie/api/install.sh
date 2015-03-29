#!/bin/sh
sudo apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev
virtualenv venv
pip install python-ldap
