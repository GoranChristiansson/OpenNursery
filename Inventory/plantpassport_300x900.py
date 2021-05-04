#!/usr/bin/python3
#
# plantpassport - a python program to generate plant passport .png files for labels
#                           input:  species_string, nursery_string, plantID_string, country_string, isOrganic
#
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 test using Libimagemagick and wand for image creation
#   Dependencies as https://docs.wand-py.org/
#			sudo apt-get install libmagickwand-dev
#			sudo apt-get install python3-wand
#			sudo apt-get install python3-qrcode
#   EU flag 200x132 pixels, Euro-leaf BIO 200x132 pixels
#   QR code 256x256 pixels
#   Label.png is (centered) 3" x 300 pixels wide and 1" x 300 pixels high. 
#   Then we can print this label with the command:  
#   lp -d DYMO_LabelWriter_450 label_20-01234.png 
#
# v1.1 - Updated layout based on input from NAKTuinbouw:
#         "A " instead of "A. "
#         Textblock must be below EU flag instead of on the side
#           todo - look into BIO-flag-location and text.
# v1.2 - 2021-02-02 - check if label is printed - in that case, don't generate new picture.
# v1.3 - 2021-02-07 - change to https and /t/ instead of folder /p/ (we need HTTPS for Geolocation from the browser!)

import wand
import wand.image
import wand.drawing

import qrcode
import os.path

class Plantpassport:
    
    ppimage = wand.image.Image(width=300*3,height=300)
    #ppdrawing = wand.drawing.Drawing(width=300*3,height=300)
    EUflag = wand.image.Image()
    EUleaf = wand.image.Image()
    QR = wand.image.Image()
    
    def load_images(self):
        self.EUflag = wand.image.Image(filename = 'EUflag200.png')
        self.EUleaf = wand.image.Image(filename = 'EUleaf200.png')
        pass
        
    def generate_qr(self, IDcode ):
        qr = qrcode.QRCode( version=1, \
        error_correction=qrcode.constants.ERROR_CORRECT_M,\
        box_size=10,\
        border=4)
        qr.add_data( IDcode )
        qr.make(fit=True)
        pilQR = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        pilQR.save("tempQR.png")
        self.QR = wand.image.Image(filename = 'tempQR.png')
        self.QR.transform( resize="256x256>")
    
    def make_label(self, species_string, cultivar_string, nursery_string, plantID_string, country_string, isOrganic ):
            # 
            #
            #
            self.load_images()
            self.generate_qr("https://kwekerijculinair.nl/t/"+plantID_string)
            ppimage = wand.image.Image(width=300*3,height=300)

            # Assemble the image
            ppimage.composite( self.EUflag, left = 25, top = 10 )
            
              # Euro-leaf if organic
            if( isOrganic ):
                ppimage.composite( self.EUleaf, left = 430, top = 10 )
                
            # add the QR code image
            ppimage.composite( self.QR, left = 625, top = 10 )
           
            
            # create ABCD-text image
            ABCD = wand.image.Image(width = 600, height = 150)

            #ABCD = wand.image.Image()
            lineheight = 42
            textwidth = 385
            
            with wand.drawing.Drawing() as drw:
                drw.font_family = 'Times New Roman, Nimbus Roman No9'
                drw.font_family = 'Arial, Calibri'
                drw.font_size = 35
                drw.font_weight = 800
                drw.text_kerning = -1
                drw.text_kerning = 0
                #drw.text("Plant Passport", left=0, baseline=40)
                #drw.text(x = 0, y = lineheight, body = "Plant Passport" )
                ppimage.annotate("Plant Passport", drw, left = 235, baseline = lineheight)
                #drw.draw(ABCD)
                drw.font_weight = 400
                drw.text(x = 0, y = lineheight*1, body=  "A " + species_string )
                drw.text(x = 0, y = lineheight*2, body=  "    '" + cultivar_string +"'")
                drw.text(x = 0, y = lineheight*3, body=  "B " + nursery_string )
                drw.text(x = textwidth, y = lineheight*1, body=  "C " + plantID_string )
                drw.text(x = textwidth, y = lineheight*2, body=  "D " + country_string )
                #ABCD.text("    " + cultivar_string, drw, left=0, baseline=120)
                #ABCD.text("B. " + nursery_string, drw, left=0, baseline=160)
                #ABCD.text("C. " + plantID_string, drw, left=0, baseline=200)
                #ABCD.text("D. " + country_string, drw, left=0, baseline=240)
                drw.draw(ABCD)
                #drw.clear()
                        
            # scale ABCD-image to perfectly fit between the EU flag and QR code
            ABCD.trim( )
            ABCD.transform( resize='600x300>')
            # add ABCD image to ppimage
            ppimage.composite( ABCD, left = 25, top = 155 )
            
           
            # save the image
            fname = "label_"+plantID_string+".png"
            # If this label has been printed - we do not generate a new label .png file. This helps to keep track of printed/not printed labels. 
            if( os.path.isfile('labels/printed/' + fname ) ):
                pass
            else:
                ppimage.save( filename = "labels/" + fname )
            self.ppimage = ppimage.clone()
            # print the image
            pass
            
    def __init__(self, species_string="", cultivar_string="", nursery_string="", plantID_string="", country_string="", isOrganic=False ):
        #
        if( species_string == ""):
            pass
        else:
            self.make_label(  species_string, cultivar_string, nursery_string, plantID_string, country_string, isOrganic )
         
# Test the class 
if __name__ == "__main__":
    p = Plantpassport()
    p.make_label("Castanea sativa","'Marron de Lyon'","NL-150390416",'20-012345','NL',isOrganic = False)
    
    p2 = Plantpassport("Castanea sativa x cr.","'Maraval'",'NAK123','20-12100','NL',isOrganic = True)
