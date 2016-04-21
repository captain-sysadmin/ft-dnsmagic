#!/usr/bin/env python

import requests

class dynDNS(object):
    '''A class for updating dyn with a dynamic public IP
    on AWS automatically.

    Requires either a valid AD username/password or Konstructor API key
    '''
    def __init__(self):
        self.konstructorPass    = ''
        self.konstructorUser    = ''
        self.publicDNS          = ''
        self.currentIP          = ''


    def getPublicIP(self):
        '''poke the AWS HTTP API to get the current
        public IP
        '''
        ip = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
        print ip.text
