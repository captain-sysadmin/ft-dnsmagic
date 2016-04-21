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
        if ip.status_code == requests.codes.ok: #pylint: disable=no-member
            return ip.text
        else:
            raise IOError

    def getPuppetCertName(self):
        '''Dive into the puppet.conf and pull out the cert name
        This is going to be used as the hostname
        '''
        with open('/etc/puppet/puppet.conf', 'r') as puppetConf:
            for line in puppetConf:
                if 'certname' in line:
                    print line
