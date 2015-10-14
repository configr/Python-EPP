# -*- coding: utf-8 -*-

from . import commands
from .contact import Contact
from .epp import EPPObject


class Domain(EPPObject):

    def __init__(self, epp, domain):
        self.domain = domain
        self.epp = epp
        self.roid = ""
        self.status = ""
        # self.ns = Nameserver(epp)

    def __unicode__(self):
        return ("[%(domain)s] status: %(status)s, " +
                "registrant: %(registrant)s, admin: %(admin)s, " +
                "tech: %(tech)s") % self

    def available(self):
        """Checks for domain availability"""

        cmd = commands.available % self.domain
        res = self.epp.cmd(cmd)

        # https://tools.ietf.org/html/rfc5731#section-3.1.1
        # "1" or "true" means that the object can be provisioned.
        # "0" or "false" means that the object can not be provisioned.
        avail = res.resdata.find('domain:name').get('avail')

        return avail == 'true' or avail == '1'

    def create(self, contacts, ns):
        cmd = commands.create % dict({
            'domain': self.domain,
            'ns': ns[0],
            'registrant': contacts['registrant'],
            'admin': contacts['admin'],
            'tech': contacts['tech'],
        })

        return self.epp.cmd(cmd)

    def delete(self, undo=False):
        if undo:
            cmd = commands.canceldelete % self.domain
        else:
            cmd = commands.delete % self.domain

        return self.epp.cmd(cmd)

    def info(self):
        cmd = commands.info % self.domain
        res = self.epp.cmd(cmd).resdata
        self.roid = res.find('domain:roid').text
        self.status = res.find('domain:status').get('s')
        self.registrant = Contact(self.epp, res.find('domain:registrant').text)
        self.admin = Contact(self.epp, res.find('domain:contact',
                                                type='admin').text)
        self.tech = Contact(self.epp, res.find('domain:contact',
                                               type='tech').text)

        return self

    def token(self):
        cmd = commands.info % self.domain
        res = self.epp.cmd(cmd)

        return res.resdata.find('domain:pw').text

    def transfer(self, token):
        cmd = commands.transfer % dict({
            'domain': self.domain,
            'token': token,
        })

        return self.epp.cmd(cmd)
