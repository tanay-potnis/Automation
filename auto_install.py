#!/usr/bin/python

import pexpect
import time

IDRAC_IP = "10.9.18.235"
IDRAC_USER = "root"
IDRAC_PASS = "calvin"
PROMPT = ["\admin1-> ","racadm>> "]




def main():
    print("1")
    racadm()
    access_console()

def access_console():
    print "console function"
    console = pexpect.spawn("telnet 10.1.8.206 7011")
    console.expect("Start installation? (Yes/No) > ",timeout=500)
    print "we are here3"
    console.sendline("Yes")
    console.expect("Press Enter to confirm >")
    console.sendline("\r\n")
    print "we are herere"
    console.expect("Please remove the installation media and press Enter to reboot >*")
    console.sendline("\r\n")
    


def racadm():
    child = pexpect.spawn("ssh -o \"StrictHostKeyChecking=no\" root@10.9.18.235")
    time.sleep(3)
    child.expect("root@10.9.18.235's password: ")
    time.sleep(3)
    print child.after
    child.sendline("calvin")
    time.sleep(3)
    print child.after
    print "boo"
    child.expect("/admin1-> ")
    time.sleep(3)
    print child.after
    child.sendline("racadm")
    time.sleep(3)
    print "racadm is next"
    child.expect("racadm>>")
    time.sleep(3)
    print child.after
    child.sendline("remoteimage -c -u br -p adminadmin -l \'10.9.18.223:/home/br/images/analytics-7.0.0.iso\'")
    time.sleep(3)
    child.sendline("set iDRAC.VirtualMedia.BootOnce 1")
    time.sleep(3)
    child.sendline("set iDRAC.ServerBoot.FirstBootDevice VCD-DVD")
    time.sleep(3)
    child.sendline("serveraction powercycle")
    time.sleep(3)
    print "end of function"
#    child.close()






if __name__=="__main__":
    main()
