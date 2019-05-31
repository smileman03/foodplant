#!/usr/bin/env python
# -*- coding: utf-8 -*-

# read_register
# read 10 registers and print result on stdout

# you can use the tiny modbus server "mbserverd" to test this code
# mbserverd is here: https://github.com/sourceperl/mbserverd

# the command line modbus client mbtget can also be useful
# mbtget is here: https://github.com/sourceperl/mbtget

from pyModbusTCP.client import ModbusClient
import time
import win_inet_pton
SERVER_HOST = "10.0.6.10"
SERVER_PORT = 502
c = ModbusClient()

# uncomment this line to see debug message
#c.debug(True)

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

while True:
    # open or reconnect TCP to server
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        else:
            print "ok"

    # if open() is ok, read register (modbus function 0x03)
    if c.is_open():
        while True:
            # read 10 registers at address 0, store result in regs list
            try:
                regs = c.read_holding_registers(0, 1)
                # if success display registers
                print("cmd: "+str(regs[0]))
            except all as E:
                print E
            # regs = c.read_holding_registers(1, 1)
            # print("ret: " + str(regs[0]))
            mystr=raw_input()
            c.write_single_register(0,int(mystr))
        # c.write_single_register(0,100)
        #
        # c.write_single_register(0,101)
        # c.write_single_register(0,1)
        # c.write_single_register(0,102)
        # c.write_single_register(0, 103)
    # sleep 2s before next polling
    time.sleep(200)