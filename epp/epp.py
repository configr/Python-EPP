# -*- coding: utf-8 -*-

import socket
import ssl
import struct

from BeautifulSoup import BeautifulStoneSoup

from . import commands


class EPP:

    def __init__(self, **kwargs):
        self.config = kwargs
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.config['host'], self.config['port']))

        try:
            self.ssl = ssl.wrap_socket(self.socket,
                                       certfile=self.config.get('cert'))
        except socket.error:
            raise socket.error(
                'ERROR: Could not setup a secure connection. \n'
                'Check whether your IP is allowed to connect to the host, '
                'or if you have a valid certificate.'
            )

        self.format_32 = self.format_32()
        self.login()

    def __del__(self):
        try:
            self.logout()
            self.socket.close()
        except TypeError:
            """ Will occur when not properly connected """
            pass

    # http://www.bortzmeyer.org/4934.html
    def format_32(self):
        # Get the size of C integers. We need 32 bits unsigned.
        format_32 = ">I"

        if struct.calcsize(format_32) < 4:
            format_32 = ">L"

            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        elif struct.calcsize(format_32) > 4:
            format_32 = ">H"

            if struct.calcsize(format_32) != 4:
                raise Exception("Cannot find a 32 bits integer")
        else:
            pass

        return format_32

    def int_from_net(self, data):
        return struct.unpack(self.format_32, data)[0]

    def int_to_net(self, value):
        return struct.pack(self.format_32, value)

    def cmd(self, cmd, silent=False):
        self.write(cmd)

        raw_response = self.read()
        if not raw_response:
            raise Exception('ERROR: Empty response')

        soup = BeautifulStoneSoup(raw_response)
        response = soup.find('response')
        result = soup.find('result')

        try:
            code = int(result.get('code'))
        except AttributeError:
            raise AttributeError("ERROR: Could not get result code.")

        if not silent or code not in (1000, 1300, 1500):
            print("- [%d] %s" % (code, result.msg.text))
        if code == 2308:
            return False
        if code == 2502:
            return False

        return response

    def read(self):
        length = self.ssl.read(4)

        if length:
            i = self.int_from_net(length) - 4

            return self.ssl.read(i)

    def write(self, xml):
        epp_as_string = xml
        # +4 for the length field itself (section 4 mandates that)
        # +2 for the CRLF at the end
        length = self.int_to_net(len(epp_as_string) + 4 + 2)

        self.ssl.send(length)

        return self.ssl.send(epp_as_string + "\r\n")

    def login(self):
        """ Read greeting """
        greeting = self.read()
        soup = BeautifulStoneSoup(greeting)
        svid = soup.find('svid')
        version = soup.find('version')
        print("Connected to %s (v%s)\n" % (svid.text, version.text))

        """ Login """
        xml = commands.login % self.config

        if not self.cmd(xml, silent=True):
            raise Exception('Error: Unable to login')

    def logout(self):
        cmd = commands.logout

        return self.cmd(cmd, silent=True)

    def poll(self):
        cmd = commands.poll

        return self.cmd(cmd)


class EPPObject:

    def __init__(self, epp):
        self.epp = epp

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            pass
