# -*- coding: utf-8 -*-

from . import commands
from .epp import EPPObject


class Nameserver(EPPObject):

    def __init__(self, epp, nameserver=False):
        self.nameserver = nameserver
        self.epp = epp

    def __unicode__(self):
        return self.nameserver

    def get_ip(self):
        cmd = commands.nameserver % self.nameserver
        res = self.epp.cmd(cmd)

        return res.resdata.find('host:addr').text
