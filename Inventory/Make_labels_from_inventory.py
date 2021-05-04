#!/usr/bin/python3
#
# make_label_from_inventory.py
#   
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 - small test program to read the inventory and then use plantpassport to print
#   2020-12-29 
# v 1.1 update inventory format to include common English and Dutch name. Use python dictionary for fields.
#   2020-12-30
# 2021-03-05 update the label so that the cultivar has '' around. 'Marigoule'
  
import plantpassport
import inventory as inventory_module

print("make_labels_from_inventory.py - Read the .csv file with all trees and add the information from labelinfo.csv to generate one .png label for each tree")

inventory = inventory_module.Inventory()
inventory.load_inventory_from_csv( "main_inventory_ver_2.csv")

labeldata = inventory_module.Inventory()
labeldata.load_inventory_from_csv( "labelinfo.csv")

labelinfo = labeldata.get_items_multiple(["Genus","Species"],["Castanea","mollissima"])

print( labelinfo[0]) 
print( labelinfo[0][1]) 
    

#plist = inventory.get_items("Species","triloba")
plist = inventory.plants

# Last elemenst of plist:
print( plist[-1:] )
plant_data = {}
 

for plant in plist:
    for f,ps in zip(inventory.fields,plant):
        plant_data[f] = ps
    
    #species_string = plant[1]+" "+plant[2]
    species_string = plant_data['Genus'] + " " + plant_data['Species']
    #cultivar_string = plant[3]
    cultivar_string = plant_data['Cultivar'] 
    #ID_string = plant[0]
    ID_string = plant_data['IDNr']
    if str( plant_data['Price'] ) == "":
        price_string = " "
    else:
        price_string = "\u20ac " + str( plant_data['Price'
        
        ] )
    print(species_string + " " + price_string)
    
    # Label info
    labelinfo = labeldata.get_items_multiple(["Genus","Species"],[plant_data['Genus'],plant_data['Species']])
    if(len(labelinfo) == 0):
        print(" Attention! This species is not yet in the labelinfo list: " + species_string )
        print( plant_data ) 
    species_nl = plant_data['Dutch']
    label1 = labelinfo[0][3]
    label2 = labelinfo[0][4]
    label3 = labelinfo[0][5]
    label4 = labelinfo[0][6]
    label5 = labelinfo[0][7]
    #plantpassport.Plantpassport(species_string, cultivar_string, "NL-150390416", ID_string,"NL",isOrganic = False)
    plantpassport.Plantpassport(species_string, cultivar_string, "NL-150390416", ID_string,"NL",False, species_nl, label1, label2, label3, label4, label5, overwrite = False, price=price_string)
    # If you want to regenerate all old labels, use overwrite = True
    # plantpassport.Plantpassport(species_string, cultivar_string, "NL-150390416", ID_string,"NL",False, species_nl, label1, label2, label3, label4, label5, overwrite = True)

# Call the label_4pack script!
print("Now we call the 4-packer")
import label_4pack