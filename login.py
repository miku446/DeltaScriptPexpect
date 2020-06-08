#!/usr/bin/python
'''
Created on 02-May-2020

@author: mmahapat
'''
import getopt
import getpass
import sys
import time

from pexpect import pxssh

from delta import delta
from parse import parse


def login(argv):
    cmds = ''
    hostname = ''
    interval = 1
    out1 = []
    out2 = []
    res_1 = []
    res_2 = []
    try:
        opts, args = getopt.getopt(argv, "hc:i:n:", ["command=", "interval=", "node="])
    except getopt.GetoptError:
        print 'login.py -n <node> -i <interval in secs> -c <command>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'login.py -n <node> -i <interval in secs> -c <command>'
            sys.exit()
        elif opt in ("-i", "--interval"):
            interval = int(arg)
        elif opt in ("-c", "--command"):
            cmds = arg
        elif opt in ("-n", "--node"):
            hostname = arg
    s = pxssh.pxssh()
    # hostname = raw_input('hostname: ')
    username = raw_input('username: ')
    password = getpass.getpass('password: ')
    if username == "":
        username = "mike"
    if password == "":
        password = "test123"
    # if not s.login(hostname, username, password, auto_prompt_reset=False):
    if not s.login(hostname, username, password, auto_prompt_reset=False):
        print("SSH session failed on login.")
        print(str(s))
    else:
        # s.sync_original_prompt()
        print("SSH session login successful")
        s.PROMPT = "#"
        s.sendline()
        s.prompt()
        print(s.before.split("\n")[1])
        node_str = s.before.split("\n")[1]
        if len(node_str.split("*")) == 2:
            s.PROMPT = node_str.split("*")[1] + "#"
        else:
            s.PROMPT = node_str.split("*")[0] + "#"
        print("The prompt is " + s.PROMPT)
        s.sendline('environment time-stamp')
        s.prompt()
        s.sendline('environment no more')
        s.prompt()
        for cmd in cmds.split(";"):
            s.sendline(cmd)
            s.prompt()  # match the prompt
            out1.append(s.before)
            # print out1[-1]
        # print(s.before)    # print everything before the prompt.
        # s.prompt ()
        # s.sendline ('sleep ' + str(interval))
        time.sleep(interval)
        # s.prompt ()         # match the prompt
        for cmd in cmds.split(";"):
            s.sendline(cmd)
            s.prompt()  # match the prompt
            out2.append(s.before)
            # print len(out2)
        # print(s.before)    # print everything before the prompt.
        print("The prompt is " + s.PROMPT)
        s.sendline('logout')
        s.close()
        # print (out1)
        # print (out2)
        for (aOut1, aOut2) in zip(out1, out2):
            print aOut1.decode('utf-8').split("\r")[-2]
            print aOut2.decode('utf-8').split("\r")[-2]
            res_1.append(parse(aOut1.decode('utf-8').split("\r")))
            res_2.append(parse(aOut2.decode('utf-8').split("\r")))
        # print (res_1)
        # print (res_2)
        for (aRes_1, aRes_2) in zip(res_1, res_2):
            delta(aRes_1, aRes_2, interval)


if __name__ == "__main__":
    login(sys.argv[1:])
