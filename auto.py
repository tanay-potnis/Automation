#!/usr/bin/python

from multiprocessing import Process
import os
import pexpect
import time
import sys
import urllib
import json
##########################
#GLOBAL VARIABLES
#########################

IDRAC_IP_ACTIVE=    "10.9.18.23"
RECOVERY_PASSWD =   "BSN"
HOSTNAME =          "DEVICE"
IPV4_ADD =          "10.9.18.235/23"
DEFAULT_GATEWAY =   "123.234.234.23"
ADMIN_PASSWD =      "ADMIN"
DNS1 =              "10.3.0.4"
DNS2 =              "10.1.5.200"
DNS_DOMAIN =        "QA.BIGSWITCH.COM"
NEW_CLUSTER =       "YES"
ACTIVE_NODE =       "10.9.40.100"
CLUSTER_NAME =      "TEST"
CLUSTER_DESC =      "TEST"
IF_C_NTP =          "NO"
CONSOLE_IP =        "10.1.8.206"
CONSOLE_PORT_A=     "7011"

##########################
##########################
def boo(num):
    print "boo"


def main():

    print("Initiating auto Install")
    #import_config()
    print("Pulling image")
    if(len(sys.argv)>2):
        print("Too many arguments")
        #print(sys.argv)
        sys.exit(1)

    if(len(sys.argv)<2):
        print("Not enough arguments Restart with Jenkins URL")
        sys.exit(1)
    
    
    url = sys.argv[1]
    get_image(url)
    data = import_config()
    
    #access_drac(data)
    #print("System Rebooting....This will take a few minutes")
    #print("...........................")
    
    #time.sleep(420)
    #access_console(data)
    #print("Your Node is set up")

#*****Cluster*****
    '''
    idrac1 = Process(target=access_drac,args=(data,0))
    idrac2 = Process(target=access_drac,args=(data,1))
    idrac3 = Process(target=access_drac,args=(data,2))

    time.sleep(10)

    idrac1.start()
    idrac2.start()
    idrac3.start()

    time.sleep(5)

    idrac1.join()
    idrac2.join()
    idrac3.join()
    
    print "idrac done"
    time.sleep(420)
    #Installation and firstboot of active node only
    access_console(data,0)
    time.sleep(2)
    print "active node done"

    console2 = Process(target=access_console,args=(data,1))
    console3 = Process(target=access_console,args=(data,2))
    
    time.sleep(5)
    console2.start()
    console3.start()
    
    time.sleep(5)
    console2.join()
    console3.join()
    print " all done"
    '''

    #Scaled Cluster formatation
    instance_count = int(data['Nodes'])
    idrac = []
    for i in range(instance_count):
        idrac.append(Process(target=access_drac,args=(data,i)))
    time.sleep(5)

    for j in range(instance_count):
        idrac[j].start()
    time.sleep(5)
    
    for k in range(instance_count):
        idrac[k].join()
    time.sleep(5)
    
    print("Idrac done")

    access_console(data,0)
    time.sleep(2)
    print "active node done"
    
    console = []
    for x in range(instance_count-1):
        console.append(Process(target=access_console,args=(data,x+1)))
    
    print "console is"
    print console
    time.sleep(5)
    for l in range(instance_count-1):
        console[l].start()

    time.sleep(5)
    for m in range(instance_count-1):
        console[m].join()
    time.sleep(5)
    
    print("all done")

    




###############################################################################################
##############################################################################################

def import_config():
    if(os.path.isfile("/home/br/scripts/config.json")==False):
        print("configuration file config.json missing")
        exit(1)
    
    with open('config.json') as f:
        data = json.load(f)

    #IDRAC_IP_ACTIVE = data['IdracIp']
    #print IDRAC_IP
    #RECOVERY_PASSWD =   data['Recovery Password']
    #HOSTNAME =          data['Hostname']
    #IPV4_ADD =          data['IPv4 address/subnet mask']
    #DEFAULT_GATEWAY =   data['Default Gateway']
    #ADMIN_PASSWD =      data['Password']
    #DNS1 =              data['DNS1']
    #DNS2 =              data['DNS2']
    #DNS_DOMAIN =        data['DNS domain']
    #NEW_CLUSTER =       data['New Cluster']
    #ACTIVE_NODE =       data['Active Node']
    #CLUSTER_NAME =      data['Cluster Name']
    #CLUSTER_DESC =      data['Cluster Description']
    #IF_C_NTP =          data['ifCustomeNTP']
    #CONSOLE_IP =        data['ConsoleServer']
    #CONSOLE_PORT_A=     data['ActiveConsolePort']
    
    return data

###############################################################################################
###############################################################################################
def get_image(image):

        if(os.path.isfile("/home/br/images/image1.iso")):
            os.remove("/home/br/images/image1.iso")

        time.sleep(2)
        urllib.urlretrieve(image, filename="/home/br/images/image1.iso")    
        time.sleep(3)

        if(os.path.isfile("/home/br/images/image1.iso")):
            return
        else:
            print("Unable to retrieve Image")
            exit(1)

################################################################################################
################################################################################################
def firstboot(console,data,i):
    
    print("Starting Firstboot")
    try:
        console.expect("analytics login\: ",timeout=300)
        console.sendline("admin")
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Do you accept the EULA for this product\? \(Yes\/No\/View\) \[Yes\] \> ")
        console.sendline("Yes")
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()
    
    time.sleep(2)
    try:
        console.expect("Emergency recovery user password \> ")
        console.sendline(data['Recovery Password'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Emergency recovery user password \(retype to confirm\) \> ")
        console.sendline(data['Recovery Password'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Hostname \> ")
        console.sendline(data['Hostname'][i])
        time.sleep(1)
        console.sendline("1")
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("IPv4 address \[0\.0\.0\.0\/0\] \> ")
        console.sendline(data['IPv4 address/subnet mask'][i])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()
    
    time.sleep(2)
    try:
        console.expect("IPv4 gateway \(Optional\) \> ")
        console.sendline(data['Default Gateway'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("DNS server 1 \(Optional\) \> ")
        console.sendline(data['DNS1'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("DNS server 2 \(Optional\) \> ")
        console.sendline(data['DNS2'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("DNS search domain \(Optional\) \> ")
        console.sendline(data['DNS domain'])
        time.sleep(1)

        if(i>0):
            console.sendline("2")
        else:
            console.sendline("1")
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()


    if(i>0):
        try:
            console.expect("Existing Analytics Node address \> ")
            console.sendline(data['Active Node'])
        except pexpect.TIMEOUT:
            print("FIRSTBOOT ERROR --Go interact")
            console.interact()

        time.sleep(2)
        try:
            console.expect("Cluster administrator password \>")
            console.sendline(data['Password'])
        except pexpect.TIMEOUT:
            print("FIRSTBOOT ERROR --Go interact")
            console.interact()

        time.sleep(2)
        try:
            console.expect("Cluster administrator password \(retype to confirm\) \> ")
            console.sendline(data['Password'])
            time.sleep(1)
            console.sendline("1")
        except pexpect.TIMEOUT:
            print("FIRSTBOOT ERROR --Go interact")
            console.interact()
        
        time.sleep(5)
        try:
            console.expect("Press enter to continue \> ")
            console.sendline()
        except pexpect.TIMEOUT:
            print("FIRSTBOOT ERROR --Go interact")
            console.interact()
        return

        
    time.sleep(2)
    try:
        console.expect("Cluster name \> ")
        console.sendline(data['Cluster Name'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Cluster description \(Optional\) \> ")
        console.sendline(data['Cluster Description'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Cluster administrator password \> ")
        console.sendline(data['Password'])
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(2)
    try:
        console.expect("Cluster administrator password \(retype to confirm\) \> ")
        console.sendline(data['Password'])
        time.sleep(1)
        console.sendline("1")
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()

    time.sleep(1)
    console.sendline("1")

    print("System Reconfiguring")
    try:
        console.expect("Press enter to continue \> ",timeout=60)
        console.sendline()
    except pexpect.TIMEOUT:
        print("FIRSTBOOT ERROR --Go interact")
        console.interact()


    print("Done")
    
    


################################################################################################
################################################################################################
def access_console(data,i):
    print("............................")
    print("Starting console access")

    if(i==0):
        time.sleep(420)
    else:
        time.sleep(60)

    #time.sleep(420)
    url = "telnet " + data['ConsoleServer'] + " " + data['ActiveConsolePort'][i]
    print url
    console = pexpect.spawn(url)
    time.sleep(7)
    console.sendline()
    
    ret = 90
    try:
        ret = console.expect(["Reboot\? \(Yes\/No\) \> ","Start installation\? \(Yes\/No\) \> "],timeout=30)
        print "Prompt reached"

        if(ret == 0):
            print " ret is 0"
            console.sendline("No")
            console.expect("Start installation\? \(Yes\/No\) \> ")
            time.sleep(3)
            console.sendline("Yes")

        if(ret==1):
            print "ret is 1"
            console.sendline("Yes")

        if(ret!=1 and ret!=0):
            print " ret is not 0 or 1"
            #print console.before
            #print console.buffer
    except pexpect.TIMEOUT:
       print("Telnet Session unsuccessful")
       print console.before
       print ret
       #print console.buffer
       sys.exit()

    time.sleep(250)
    try:
        console.expect("Press Enter to confirm \> ",timeout=100)
        console.sendline()
        print("Installation Initialized")

    except pexpect.TIMEOUT:
        print("Staging took too long")



    #console.sendline("No")
    #print("start instalation yes no")
    #try:
    #    console.expect("Start installation? (Yes/No) > ",timeout=420)
    #    print("Installation prompt reached")
    #except pexpect.TIMEOUT:
    #    print("Check IDRAC console...somethin wrong")
    
    #print console.before
    #console.sendline("Yes")
    print("Staging image")

   # try:
    #    console.expect("Press Enter to confirm >")
    #print("Enter key push")
   # except pexpect.TIMEOUT:
   #     print("Check IDRAC console...something wrong at enter to condirm")

    print("Installing. This will take several minutes.")
    try:
        #console.interact()
        console.expect("Please remove the installation media and press Enter to reboot \> ",timeout=5200)
        print "we are in please remove"
        time.sleep(3)
        console.sendline()
    except pexpect.TIMEOUT:
        print("Installation Unsucessful")
        console.interact()
    
    print("Installation complete")
    print("Rebooting from Hard Drive....May take a few minutes")

    print("Starting Firstboot")
    time.sleep(150)
    firstboot(console,data,i)
########################################################################################################
########################################################################################################

def access_drac(data,i):
    print "Starting Racadm session"
    print i

    url = "ssh -o \"StrictHostKeyChecking=no\" root@" + data['IdracIp'][i]
    racadm = pexpect.spawn(url)
    #racadm = pexpect.spawn("ssh -o \"StrictHostKeyChecking=no\" root@10.9.18.235")
    time.sleep(3)
    print "bobobobobobobobobobobobo" 
    prompt1 = "root@" + data['IdracIp'][i] +"\'s password: "
    prompt2 = "Password: "
    login_prompt = [prompt1,prompt2]
    print prompt1
    try:
        racadm.expect([prompt1,prompt2],timeout=30)
        #racadm.expect("root@10.9.18.235's password: ",timeout=30)

    except pexpect.TIMEOUT:
        print("Timeout reached durin SSH session to IDRAC")
        print("Exiting out")
        racadm.close()
        sys.exit()

    print("Logging in")
    racadm.sendline("calvin")
    print "after password"
    time.sleep(3)
    prompt = ["/admin1-> ","racadm>> "]

    try:
        #racadm.expect("/admin1-> ",timeout=30)
        racadm.expect(["/admin1-> ","racadm>>"],timeout=30)

    except pexpect.TIMEOUT:
        print("Login Unsucessful")
        print("Going to interact mode")
        #racadm.interact()
        
    time.sleep(2)
    racadm.sendline("racadm")
    #racadm.expect("racadm>>")
    time.sleep(3)
    racadm.sendline("remoteimage -d")
    time.sleep(4)

    racadm.sendline("remoteimage -s")
    time.sleep(4)
    try:
        racadm.expect("Remote File Share is Disabled")
        time.sleep(2)
        print("No FIle Share mounted")

    except pexpect.TIMEOUT:
        print("Mounting remote file system not possible")
        racadm.interact()
        sys.exit(1)

    racadm.sendline("remoteimage -c -u br -p adminadmin -l '10.106.10.223:/home/br/images/image1.iso'")
    try:
        racadm.expect("Remote Image is now Configured")
        print("Remote image configured successfully")

    except pexpect.TIMEOUT:
        print("Remote Image not configured")
        sys.exit(3)

    
    time.sleep(3)
    racadm.sendline("set iDRAC.VirtualMedia.BootOnce 1")
    try:
        racadm.expect("[Key=iDRAC.Embedded.1#VirtualMedia.1]")
        print("iDRAC.VirtualMedia.BootOnce successfully set")

    except pexpect.TIMEOUT:
        print("iDRAC.VirtualMedia.BootOnce not successfully set")
        racadm.interact()

    racadm.sendline("set iDRAC.ServerBoot.FirstBootDevice VCD-DVD")
    try:
        racadm.expect("[Key=iDRAC.Embedded.1#ServerBoot.1]")
        print("Boot location changed to virtual CD/DVD")
    except pexpect.TIMEOUT:
        print("iDRAC.ServerBoot.FirstBootDevice  not successfully set")

    
    racadm.sendline("racadm serveraction powercycle")
    try:
        racadm.expect("Server power operation initiated successfully")
        print("Rebooting")
    except pexpect.TIMEOUT:
        print("Server not rebooted")
        racadm.interact()

######################################################################################################
#####################################################################################################
'''
def main():

    print("Initiating auto Install")
    import_config()
    print("Pulling image")
    if(len(sys.argv)>2):
        print("Too many arguments")
        #print(sys.argv)
        sys.exit(1)

    if(len(sys.argv)<2):
        print("Not enough arguments Restart with Jenkins URL")
        sys.exit(1)


    url = sys.argv[1]
    get_image(url)
    data = import_config()

    #access_drac(data)
    print("System Rebooting....This will take a few minutes")
    print("...........................")

    #time.sleep(420)
    #access_console(data)
    print("Your Node is set up")

#*****Cluster*****
tup1 = (data,0)
idrac1 = Process(target=access_drac,args=tup1)
idrac2 = Process(target=access_drac,args=(data,1))
idrac3 = Process(target=access_drac,args=(data,1))

time.sleep(10)

idrac1.start()
idrac2.start()
idrac3.start()

time.sleep(5)

idrac1.join()
idrac2.join()
idrac3.join()
'''
#####################################################################################################
####################################################################################################
if __name__ == "__main__":
    main()

