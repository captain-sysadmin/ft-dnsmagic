#!/usr/bin/env python

import sys
import socket
import requests

class dynDNS(object):#pylint: disable=too-many-instance-attributes
    '''A class for updating dyn with a dynamic public IP
    on AWS automatically.

    Requires either a valid AD username/password or Konstructor API key
    '''
    def __init__(self):
        self.konstructorPass    = ''
        self.konstructorUser    = ''
        self.konstructorKey     = ''
        self.currentIP          = ''
        self.certName           = ''
        self.domainSuffix       = 'ft.com'
        self.headers            = {
            'Accept':       'application/json',
            'User-Agent':   'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
            }
        if self.konstructorKey:
            print "using API Key"
            self.konstructorURL     = 'https://konstructor.ft.com'
        elif self.konstructorPass and self.konstructorUser:
            print "using basic auth"
            self.konstructorURL     = 'http://konstructor.svc.ft.com'
        else:
            print "no credentials provided"
            sys.exit(2)




    def getPublicIP(self):
        '''poke the AWS HTTP API to get the current
        public IP
        '''
        ip = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
        if ip.status_code == requests.codes.ok: #pylint: disable=no-member
            self.currentIP = ip.text
            return ip.text
        else:
            return False

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
                    # loose the space at the start
                    self.certName = self.certName.lstrip()
        if self.certName == '':
            # then we haven't managed to get the puppet cert name....
            return False
        else:
            return True
    def isCurrentIPCorrect(self):
        '''check to see if the current IP for the proposed address
        matches whats actually in the DNS
        '''
        try:
            ip = socket.gethostbyname('{0}.{1}'.format(self.certName,self.domainSuffix))
        except socket.gaierror:
            return False
        if ip:
            if ip == self.currentIP:
                return True
            else:
                return False
        else:
            # we shouldn't get here, if we do, then the IP aint there...
            return False

    def deleteOldDNSRecord(self):
        '''Use konstructor to delete the old DNS record
        '''
        headers = self.headers
        if not self.konstructorKey:
            # then use that as the auth mechanism
            delete = requests.delete('{0}/v1/dns/delete?zone=ft.com&name={1}.{2}'.format(self.konstructorURL,self.certName,self.domainSuffix), auth=(self.konstructorUser, self.konstructorPass), headers=headers)
        else:
            headers.update({'Authorization': self.konstructorKey})
            delete = requests.delete(self.konstructorURL, headers=headers)

        if delete.status_code == requests.codes.ok:#pylint: disable=no-member
            return True
        else:
            return False
    def createNewDNSRecord(self):
        '''Use konstructor to create a new A record
        under in the form of 'certname.domainSuffix'
        '''
        headers = self.headers
        if not self.konstructorKey:
            create = requests.post('{0}/v1/dns/create?zone=ft.com&name={1}.{2}'.format( self.konstructorURL, self.certName, self.domainSuffix), auth=(self.konstructorUser, self.konstructorPass), headers=headers)
        else:
            headers.update({'Authorization': self.konstructorKey})
            create = requests.post('{0}:{1}@{2}/v1/dns/create?zone=ft.com&name={3}.{4}'.format(self.konstructorUser,self.konstructorPass, self.konstructorURL, self.certName, self.domainSuffix),headers=headers)
        if create.status_code == requests.codes.ok:#pylint: disable=no-member
            return True
        else:
            return False

if __name__ == '__main__':
    update = dynDNS()
    update.getPublicIP()
    update.getPuppetCertName()
    if update.isCurrentIPCorrect():
        sys.exit()
    else:
        update.deleteOldDNSRecord()
        update.createNewDNSRecord()










