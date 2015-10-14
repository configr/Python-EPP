# -*- coding: utf-8 -*-

from . import commands
from .epp import EPPObject


class Contact(EPPObject):

    def __init__(self, epp, handle=False, **kwargs):
        self.epp = epp
        self.handle = handle

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __unicode__(self):
        try:
            self.name != ''
            return ("[%(handle)s] %(name)s, %(street)s, " +
                    "%(pc)s %(city)s (%(cc)s)") % self
        except:
            return self.handle

    def available(self):
        cmd = commands.contact.available % self
        res = self.epp.cmd(cmd)

        return res.resdata.find('contact:id').get('avail') == 'true'

    def create(self):
        cmd = commands.contact.create % self
        res = self.epp.cmd(cmd).resdata

        return res.find('contact:id').text

    def info(self):
        cmd = commands.contact.info % self
        res = self.epp.cmd(cmd).resdata
        self.roid = res.find('contact:roid').text
        self.status = res.find('contact:status').get('s')
        self.name = res.find('contact:name').text

        try:
            self.street = res.find('contact:street').text
        except AttributeError:
            pass

        self.city = res.find('contact:city').text

        try:
            self.pc = res.find('contact:pc').text
        except AttributeError:
            pass

        self.cc = res.find('contact:cc').text
        self.voice = res.find('contact:voice').text
        self.email = res.find('contact:email').text

        return self

    def update(self):
        cmd = commands.contact.update % self

        return self.epp.cmd(cmd)
