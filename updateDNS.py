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
        self.certName           = ''


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
                    # remove the carriage return
                    line = line.rstrip()
                    # now let start pulling it apart to get just the PDS name
                    # remove the 'certname =' part
                    certParts = line.split('=')
                    # now lets get rid of the rest of the PDS domain
                    certParts = certParts[1]
                    self.certName = certParts.split('.')[0]
        if self.certName == '':
            # then we haven't managed to get the puppet cert name....
            raise IOError
        else:
            return True

