#!/usr/bin/python3
#
# label4pack - bundel alle plantenlabels in 4-pack voor de Citizen-labelprinter
#
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 test using Libimagemagick and wand for image composition
#   Dependencies as https://docs.wand-py.org/
#	
#  De labels worden gepakt uit folder "labels" en de nieuwe labels zijn in de folder "labels4pack"
#  De oude labels gaan naar folder "packed" 
#  2021-03-28, Goran Christiansson


import wand
import wand.image
import wand.drawing
import wand.color

import qrcode
import os.path, glob, os


# Generate new 4-packs for new labels (True) or regenerate all 4packs (False)
ONLY_NEW = True


if __name__ == "__main__":
    print("label4pack.py - Take all labels from folder <labels> and make 4-pack-printable pngs into folder <labels/4pack>")
    # print(f"Arguments count: {len(sys.argv)}")
    if( ONLY_NEW):
        print( "Only generating new 4pack labels, not overwriting old labels")
    else:
        print("Generating new 4pack labels of all labels, overwriting existing labels.")
    filelist = sorted( glob.glob( "labels/*.png" ) )
    
    filelist.append(" ")
    filelist.append(" ")
    filelist.append(" ")
    filelist.append(" ")
    
    #print(filelist)
    
    #printImage = wand.image.Image( width = 203*4, height = 2030, background = wand.color.Color('white'))
    
    for packnr in range(0,len(filelist)-4, 4 ):
    #for packnr in range(0, 5, 4 ):
        # Make the image blank before we add the four pictures - to avoid the "Bouche de Bettizac" problem! 21-1337 instead of 21-1340
        printImage = wand.image.Image( width = 203*4, height = 2030, background = wand.color.Color('white'))
        f1 = filelist[ packnr  ]
        f2 = filelist[ packnr +1 ]
        f3 = filelist[ packnr +2 ]
        f4 = filelist[ packnr +3 ]
        
        #printFilename = "labels/4pack/4pack_"+ os.path.basename(f1)
        #printedFilename = "labels/4pack/printed/4pack_"+ os.path.basename(f1)
        # - changed 2021-05-03 - less folder depth

        printFilename = "4pack/4pack_"+ os.path.basename(f1)
        printedFilename = "4pack/printed/4pack_"+ os.path.basename(f1)
        if( os.path.exists( printFilename) and ONLY_NEW):
            print("skipping existing: " + printFilename )
            pass # - don't make a new 4-pack if the file exists
        elif( os.path.exists( printedFilename) and ONLY_NEW):
            print("skipping existing printed 4packlabel: " + printedFilename )
            pass # - don't make a new 4-pack if the file exists and was printed
        else:
            print("Filenames: " + f1 +" " + f2+" " + f3+" "+ f4+" ")
        
            p1 = wand.image.Image(filename = f1)
            if( os.path.isfile( f2)):
                p2 = wand.image.Image(filename = f2)
            else:
                p2 = wand.image.Image( width = 2030, height = 203)
            if( os.path.isfile( f3)):
                p3 = wand.image.Image(filename = f3)
            else:
                p3 = wand.image.Image( width = 2030, height = 203)
            if( os.path.isfile( f4)):
                p4 = wand.image.Image(filename = f4)
            else:
                p4 = wand.image.Image( width = 2030, height = 203)
            
            # Now that the pictures are loaded - rotate all 90 deg.
            p1.rotate(90)
            p2.rotate(90)
            p3.rotate(90)
            p4.rotate(90)
            
            # Composite the pictures onto the printImage:
            printImage.composite( p1, left = -17+0, top = -130 )
            printImage.composite( p2, left = -17+202, top = -130 )
            printImage.composite( p3, left = -17+202*2, top = -130 )
            printImage.composite( p4, left = -17+202*3, top = -130 )
            
            printImage.save(filename = printFilename)
            # print( p1 )
        #endif
    #end for packnr
    
