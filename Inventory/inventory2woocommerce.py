#!/usr/bin/python3
#
# inventory2woocommerce.py
#  - Generate a complete inventory for the webshop based on the Inventory file.    
#  - woocommerce needs 2 files: one for "simple product" and "parent for variation" 
#    and another file for the variations themselves. (i.e. pot sizes)
#
# For each cultivar - make a list of available pot sizes with stock & price
# For those without cultivar - make similar list
#
#
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 -  adapted from make_labels_from_inventory
# 2021-05-15, 
# v 1.1 - added an export of inventory for ordering for External Shops  (Species, Pot size, Price, Order volume
# 2021-05-30 

import inventory as inventory_module

print("inventory2woocommerce.py - Generate a file for woocommerce import")

inventory = inventory_module.Inventory()
inventory.load_inventory_from_csv( "main_inventory_ver_2.csv")

# load generic information texts about the trees from a separate file:
shopdata = inventory_module.Inventory()
shopdata.load_inventory_from_csv( "woo-import-info.csv")

#labelinfo = labeldata.get_items_multiple(["Genus","Species"],["Castanea","mollissima"])

#print( labelinfo[0]) 
#print( labelinfo[0][1]) 
    

plist = inventory.plants

# Last elemenst of plist:
print( plist[-1:] )
plant_data = {}
 
# Sort the plant list first on Genus, then species, then cultivar then pot size:
from operator import itemgetter
plist.sort( key = itemgetter(1,2,3,15))

# I want to make a list where I have one row for each "product":
#
# Castanea sativa, ''
# Castanea sativa 'Marron de Lyon'
# Castanea sativa 'Glabra'
#
# Then I need to get for each of these "products" a count of the separate pot sizes and stock per size:
#
# Castanea sativa 'Marron de Lyon':
#    - C3, 10
#    - C7, 23
#    - W, 644
#    - x, 3 ( skipped - dead trees )
#
# for those with more than 1 pot size, make a variable product, for those with 1 pot size - simple product.
#
# One list with complete product information for woo-commerce import, and one list with just stock and price. 
#
#


# now that we have a sorted list - remove all other cruft, just keep genus, species, cultivar, DUTCH NAME, potsize, price
cleanlist = []
for p in plist: 
    if(len(p[12]) == 0): # If the sold-date is empty, add to the list.
        if(len(p[13]) > 0): # If the price has a value
            if( p[15] != 'x'):
                cleanlist.append( (p[1], p[2],p[3], p[4], p[15] ) )

# Count elements of each: 
from collections import Counter
stockcounter=Counter(cleanlist)
#print(stockcounter)
    
#print( stockcounter['Castanea','sativa','Marron de Lyon','Tamme kastanje','W'])

# convert the counter dictionary to a list:
assortmentlist = list(stockcounter)

# Make a list of all cultivars that we have, including a blank one for seedlings
productlist = []
for a in assortmentlist:
    #product = (a[0],a[1],a[2], a[3], a[4],a[5])
    product = (a[0],a[1],a[2], a[3])
    if product in productlist:
        pass
    else:
        productlist.append( product )
#print(productlist)

# importing datetime module for now() - to put in the filename
import datetime 
 
now = datetime.datetime.now() 
filename_date = str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + ""     
# Printing attributes of now(). 
print ("The attributes of now() are : ") 
    

# Now we check each product - how many pot sizes are there? 
pot_strings = ('C1','C3','C7','W')  # not "x" or blank

id_nr = 1
# Save the outfile as 
import codecs
parent_filename = "woo-import_" + filename_date + ".csv"
with codecs.open(parent_filename, 'w', 'utf-8') as outfile:
    stock_filename = "woo-import-stock" + filename_date + ".csv"
    with codecs.open(stock_filename, 'w', 'utf-8') as outfile_stock:

        order_filename = "bestellijst_planten_" + filename_date + ".csv"
        with codecs.open(order_filename, 'w', 'utf-8') as outfile_order:
        
            print('Type,Artikelnummer,Naam,Gepubliceerd,Uitgelicht?,"Zichtbaarheid in catalogus","Korte omschrijving",Beschrijving,"Startdatum actieprijs","Einddatum actieprijs","Btw status",Belastingklasse,"Op voorraad?",Voorraad,"Lage voorraad","Nabestellingen toestaan?","Wordt individueel verkocht?","Gewicht (kg)","Lengte (cm)","Breedte (cm)","Hoogte (cm)","Klantbeoordelingen toestaan?",Aankoopnotitie,Actieprijs,"Reguliere prijs",Categorieën,Tags,Verzendklasse,Afbeeldingen,Downloadlimiet,"Dagen vervaltijd download",Hoofd,"Gegroepeerde producten",Upsells,Cross-sells,"Externe URL","Knop tekst",Positie,"Naam eigenschap 1","Waarde eigenschap 1","Zichtbare eigenschap 1","Globale eigenschap 1","Standaardeigenschap 1"')
            outfile.write('Type,Artikelnummer,Naam,Gepubliceerd,Uitgelicht?,"Zichtbaarheid in catalogus","Korte omschrijving",Beschrijving,"Startdatum actieprijs","Einddatum actieprijs","Btw status",Belastingklasse,"Op voorraad?",Voorraad,"Lage voorraad","Nabestellingen toestaan?","Wordt individueel verkocht?","Gewicht (kg)","Lengte (cm)","Breedte (cm)","Hoogte (cm)","Klantbeoordelingen toestaan?",Aankoopnotitie,Actieprijs,"Reguliere prijs",Categorieën,Tags,Verzendklasse,Afbeeldingen,Downloadlimiet,"Dagen vervaltijd download",Hoofd,"Gegroepeerde producten",Upsells,Cross-sells,"Externe URL","Knop tekst",Positie,"Naam eigenschap 1","Waarde eigenschap 1","Zichtbare eigenschap 1","Globale eigenschap 1","Standaardeigenschap 1"  \n')
            outfile_stock.write('Artikelnummer,Voorraad,"Reguliere prijs"  \n')
            outfile_order.write('Soort, ,Cultivar,Pot,Voorraad, "Reguliere prijs", "Bestelling aantal"\n')
            
            for p in productlist:
                print(p)
                num_sizes = 0
                pot_sizes = []
                pot_stock = []
                out_string = []
                pot_sizes_string = '"'
                #price = p[5]
                #price = "10"
                for pot in pot_strings:
                    i = stockcounter[p[0],p[1],p[2],p[3], pot]   # Empty field of date-sold means that there is still stock
                    
                    # calculate what to show here: 
                    if i > 0:
                        num_sizes += 1
                        pot_sizes.append( pot )
                        pot_stock.append( i )
                        pot_sizes_string = pot_sizes_string + pot +','
                
                            
                pot_sizes_string = pot_sizes_string[:-1] + '"'
                #print(p[0]+p[1]+p[2]+p[3])
                #print( pot_sizes_string )
                
                if(num_sizes == 1):
                    #print("Product with one size - simple product")
                    #print(p)
                    
                    id_nr += 1
                    #out_string = str(id_nr) + ", simple, " # remove ID
                    out_string =  "simple, "
                    SKU = (p[0]+"-"+p[1]+"-"+p[2]+"-"+pot_sizes[0] ).replace(" ","_")
                    # lookup the price information:
                    print(SKU)
                    shopinfo = shopdata.get_items_multiple(["Artikelnummer"],[SKU])
                    price = shopinfo[0][6]
                    category = shopinfo[0][7]
                    
                    stock = int(pot_stock[0])
                    stock = max(0, int((stock-3)*0.7))
                    
                    out_string = out_string +  SKU +" ," 
                    if( len(p[2])<1):
                        out_string = out_string + '"' + p[3] +  '",' # Product name / seedling
                    else:
                        out_string = out_string + '"' + p[3] + " '"+ p[2]+ "' " + '",' # Product name / cultivar
                    
                    #out_string = out_string + '"' + p[3] + " '"+ p[2]+ "'" + '",' # Product name
                    out_string = out_string + '1,0,visible,,"product description - simple product",,,taxable,reduced-rate,1,'
                    out_string = out_string + str(stock) + ',,0,0,,,,,1,,,' + str( price) + ',' + category + ',,,,,,,,,,,,0,,,,,'
                    print(out_string)
                    outfile.write(out_string + "\n" )
                    outfile_stock.write(SKU+","+  str(stock) + "," +str( price) + "\n")
                    if( pot != 'W'and safestock > 0):
                        outfile_order.write( p[0] + "," + p[1]+","+p[2]+","+pot+ ","+  str(safestock)+ "," +str( price) + ", \n")

                else:
                    #print("Product with multiple sizes - variable product")
                    #print(p)
                    #print(pot_sizes)
                    
                    # One row for main product, one row for each of the pot-sizes: 
                    id_nr += 1
                    #out_string = str(id_nr) + ", variable, "
                    out_string =  "variable, "
                    SKU_parent = (p[0]+"-"+p[1]+"-"+p[2] ).replace(" ","_")
                    # lookup the price information:
                    shopinfo = shopdata.get_items_multiple(["Artikelnummer"],[SKU_parent])
                    price = shopinfo[0][6]
                    category = shopinfo[0][7]
                    
                    out_string = out_string + SKU_parent +" ,"  # SKU for the "parent" 
                    #out_string = out_string + " ," 
                    if( len(p[2])<1):
                        out_string = out_string + '"' + p[3] +  '",' # Product name / seedling
                    else:
                        out_string = out_string + '"' + p[3] + " '"+ p[2]+ "' " +  '",' # Product name / cultivar
        
        
                    out_string = out_string + '1,0,visible,,"Product description / main tree",,,taxable,reduced-rate,1,,,0,0,,,,,1,,,' + str( price) + ',' + category + ',,,,,,,,,,,,0,'
                    out_string = out_string + '"Pot of wortelgoed",' + pot_sizes_string + ',1,1,' + pot_sizes[0] # name of the "eigenschap" in Woocommerce
                    
                    #print(out_string)
                    outfile.write(out_string + "\n" )

                    #parent_id = id_nr # for reference in the variation product below
                    
             
                    for pot,stock in zip( pot_sizes, pot_stock):
                        id_nr += 1
                        #out_string = str(id_nr) + ", variation, "
                        out_string = "variation, "
                        SKU = (p[0]+"-"+p[1]+"-"+p[2]+"-"+pot ).replace(" ","_")
                        # lookup the price information:
                        shopinfo = shopdata.get_items_multiple(["Artikelnummer"],[SKU])
                        price = shopinfo[0][6]
                        category = shopinfo[0][7]
        
                        out_string = out_string +  SKU +" ," 
                        # for the seedlings, common name, for cultivars include 'p[2]'
                        if( len(p[2])<1):
                            out_string = out_string + '"' + p[3] + "  - " + pot + '",' # Product name / seedling
                        else:
                            out_string = out_string + '"' + p[3] + " '"+ p[2]+ "' - " + pot + '",' # Product name / cultivar
        
                        out_string = out_string + '1,0,visible,,"Product description / pot variant ",,,taxable,reduced-rate,1,'
                        
                        print(stock)
                        safestock = int(stock)
                        safestock = max(0, int((safestock-3)*0.7))
                        print(safestock)
                        out_string = out_string + str(safestock) + ',,0,0,,,,,1,,,' + str( price) + ',' + category + ',,,,,,' 
                        out_string = out_string + SKU_parent + ',,,,,,0,'
                     
                        out_string = out_string + '"Pot of wortelgoed",' + pot + ' ,,1,'# name of the "eigenschap" in Woocommerce
                        print(out_string)
                        outfile.write(out_string + "\n" )
                        outfile_stock.write(SKU+","+  str(safestock)+ "," +str( price) + "\n")
                        if( pot != 'W' and safestock > 0):
                            outfile_order.write(p[0]+","+p[1]+","+p[2]+","+pot +  ","+  str(safestock)+ "," +str( price) + ", \n")


    
# I generate a csv file. If I import all of it at once, I cannot see any variants, only the main trees and simple trees. 
# When I import the first ten items, the import is perfect. Strange!    
        