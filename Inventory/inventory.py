#!/usr/bin/python3
#
# inventory.py - main class containing the inventory
#   
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 - small test program to read the inventory from a .csv file and have it available for searching etc.
#   2020-12-29 

import csv


class Inventory:
    
    #plants = []
    #fields = []
    
    def load_inventory_from_csv( self, filename ):
            csvfile = open(filename )
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.fields = next(reader)
            self.plants = []
            # Check file as empty
            if self.fields != None:
                for row in reader:
                    # TODO - add string.rstrip() for all elements in the row, to eliminate trailing spaces.
                    self.plants.append( row )
            csvfile.close()
            #print("loaded file with fields: ")
            #print( self.fields )
            #for p in self.plants:
             #   print( p )
             

    def save_inventory_to_csv( self, filename ):
            csvfile = open(filename , "w")
            writer = csv.writer(csvfile,  delimiter=',', quotechar='"', lineterminator="\n")
            writer.writerows([self.fields])
            writer.writerows(self.plants)
            csvfile.close()
             
                
    def get_items( self, field, text):
        # Get a list of items with the "field" matching "text"
        plantlist = []
        if field in self.fields:
            fieldindex = self.fields.index( field )
            for p in self.plants:
                if p[fieldindex] == text:
                    plantlist.append(p)
        return(plantlist)

    def get_items_multiple( self, fields, texts ):
        # look in several fields, and match corresponding texts, 
        # e.g. get_items_multiple( ["Genus","Source"],["Castanea","Route9"]
        plantlist = []
        
        for f in fields:
            if f not in self.fields:
                print("Error! " + f + " is not a field name" );
                return([])
        
        
        for p in self.plants:
            add_this_plant = True
            for f,t in zip(fields, texts):
                fieldindex = self.fields.index( f ) 
                if p[fieldindex] != t:
                    add_this_plant = False
            if add_this_plant:
                plantlist.append(p)
        return(plantlist)
    
if __name__ == "__main__":
    inventory = Inventory()
    inventory.load_inventory_from_csv( "main_inventory_ver_2.csv")
    
    #plist = inventory.get_items("Species","triloba")
    #for p in plist:
    #    print(p)
    plist = inventory.get_items("IDNr","21-0010")
    for p in plist:
        print(p)
        
    #plist = inventory.get_items_multiple(["Genus","Species"],["Castanea","mollissima"])
    #for p in plist:
    #    print(p)
    
    