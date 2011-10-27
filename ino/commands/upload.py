# -*- coding: utf-8; -*-

from __future__ import absolute_import

import os.path
import subprocess

from time import sleep
from serial import Serial
from serial.serialutil import SerialException

from ino.commands.base import Command
from ino.exc import Abort


class Upload(Command):

    name = 'upload'

    def setup_arg_parser(self, parser):
        parser.add_argument('-p', '--serial-port', metavar='PORT', default='/dev/ttyACM0', 
                            help='Serial port to upload firmware to')

    def discover(self):
        self.e.find_tool('stty', ['stty'])
        self.e.find_arduino_tool('avrdude', ['hardware', 'tools'], ['avrdude'])
        self.e.find_arduino_file('avrdude.conf', ['hardware', 'tools'], ['avrdude.conf'])
    
    def run(self, args):
        self.discover()
        port = args.serial_port

        if not os.path.exists(port):
            raise Abort("%s doesn't exist. Is Arduino connected?" % port)

        ret = subprocess.call([self.e['stty'], '-F', port, 'hupcl'])
        if ret:
            raise Abort("stty failed")

        # pulse on dtr
        try:
            s = Serial(port, 115200)
        except SerialException as e:
            raise Abort(str(e))

        s.setDTR(False)
        sleep(0.1)
        s.setDTR(True)

        subprocess.call([
            self.e['avrdude'],
            '-C', self.e['avrdude.conf'],
            '-p', 'atmega328p',
            '-P', port,
            '-c', 'stk500v1',
            '-b', '115200',
            '-D',
            '-U', 'flash:w:%s:i' % self.e['hex_path'],
        ])