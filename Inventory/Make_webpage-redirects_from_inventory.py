#!/usr/bin/python3
#
# make_label_from_inventory.py
#   
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 - make_webpage-redirects_from_inventory
#   2021-02-07 Redirect to https! /p/ to /t/
# <meta http-equiv="refresh" content="0; URL=https://www.kwekerijculinair.nl/t/19-0002" />


#import webpager
import inventory
import os


inventory = inventory.Inventory()
inventory.load_inventory_from_csv( "main_inventory_ver_2.csv")
    
# plist = inventory.get_items("Species","triloba")
plist = inventory.plants

#wp = webpager.Webpage()

def safe_makedir( foldername ):
    try:
        os.mkdir( foldername )  
    except:
        print("warning- folder maybe already exists")


filename = "index.html"

for plant in plist:
    print(plant)
    plantID = plant[0]
    filecontent = '<meta http-equiv="refresh" content="0; URL=https://www.kwekerijculinair.nl/t/' +  plantID+ '" />'
    foldername = 'p/' + plantID
    safe_makedir( foldername ) 
    fname = 'p/'+ plantID + '/' + filename 
    print( fname )
    f = open(fname, 'w')
    f.write( filecontent )
    f.close()

os.system('expect securecopy.exp')