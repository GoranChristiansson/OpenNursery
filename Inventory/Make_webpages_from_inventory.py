#!/usr/bin/python3
#
# make_webpages_from_inventory.py
#   
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 - small test program to read the inventory and then use webpager.py to generate
#   2020-12-29 
#
# v 1.1 - add uploading to the webhost using expect and scp 
#      2021-02-01

import webpager
import inventory


inventory = inventory.Inventory()
inventory.load_inventory_from_csv( "main_inventory_ver_2.csv")
    
# plist = inventory.get_items("Species","triloba")
plist = inventory.plants

wp = webpager.Webpage()

for plant in plist:
    wp.make_webpage( inventory.fields, plant )


import os
os.system('expect securecopy.exp')