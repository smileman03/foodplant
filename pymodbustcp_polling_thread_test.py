#!/usr/bin/env python
# -*- coding: utf-8 -*-

# modbus_thread
# start a thread for polling a set of registers, display result on console
# exit with ctrl+c
import win_inet_pton
import time
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

SERVER_HOST = "10.0.6.10"
SERVER_PORT = 502

# set global
regs = []
c=ModbusClient(host=SERVER_HOST, port=SERVER_PORT)
# init a thread lock
regs_lock = Lock()
if not c.is_open():
    if not c.open():
        print("unable to connect to " + SERVER_HOST + ":" + str(SERVER_PORT))
# modbus polling thread
def polling_thread():
    global regs
    # global c = ModbusClient(host=SERVER_HOST, port=SERVER_PORT)
    global c
    # if not c.is_open():
    #     if not c.open():
    #         print("unable to connect to " + SERVER_HOST + ":" + str(SERVER_PORT))
    # polling loop
    while True:
        # keep TCP open
        # read 10 registers at address 0, store result in regs list
        regs = c.read_holding_registers(0, 1)
        # if success display registers
        print("cmd: " + str(regs[0]))
        regs = c.read_holding_registers(1, 1)
        print("ret: " + str(regs[0]))
        time.sleep(1)

    # modbus polling thread
def polling_thread2():
    global c
    # polling loop
    while True:
        time.sleep(1)
        mystr = raw_input()
        c.write_single_register(0, int(mystr))
# start polling thread
tp = Thread(target=polling_thread)
# set daemon: polling thread will exit if main thread exit
tp.daemon = True
# tp.start()

tp2=  Thread(target=polling_thread2)
tp2.daemon = True
tp2.start()
# display loop (in main thread)
while True:
    # print regs list (with thread lock synchronization)
    # with regs_lock:
    #     print(regs)
    # 1s before next print
    time.sleep(1)