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
#
# v 2.0 2021-03-24 - complete redesign based on new labelprinter Citizen CL-s621
#       New label 200 pixels high (203 dpi) and quite a lot wider. 
#       Opportunity for more text and information
#       The labels will later be bundled in packs of 4 and printed.
# v 2.1 2021-04-21 - Add price! 
# 
# v 2.2. 2021-05-03 Running on NUC lilleputt computer - need to upgrade Wand to 0.6:
# python3 -m pip install  --upgrade wand


import wand
import wand.image
import wand.drawing

import qrcode
import os.path

WIDTH = 10*203  # 10 inch x 203 dpi
HEIGHT = 203      # 1 inch x 203 dpi

class Plantpassport:
    
    ppimage = wand.image.Image(width=WIDTH,height=HEIGHT)
    #ppdrawing = wand.drawing.Drawing(width=300*3,height=300)
    EUflag = wand.image.Image()
    EUleaf = wand.image.Image()
    QR = wand.image.Image()
    
    def load_images(self):
        # White flag: self.EUflag = wand.image.Image(filename = 'euflag_black_white_contrast_60.png')
        self.EUflag = wand.image.Image(filename = 'EUflag60black.png')
        
        #self.EUflag = wand.image.Image(filename = 'EUflag200.png')
        self.EUleaf = wand.image.Image(filename = 'EUleaf200black.png')
        self.Logo = wand.image.Image(filename = '2021-logo-side-w-text-bw_100.png')
        self.Butterfly= wand.image.Image(filename = 'butterfly_75.png')
        
        
        pass
        
    def generate_qr(self, IDcode ):
        qr = qrcode.QRCode( version=1, \
        error_correction=qrcode.constants.ERROR_CORRECT_M,\
        box_size=6,\
        border=4)
        qr.add_data( IDcode )
        qr.make(fit=True)
        pilQR = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        pilQR.save("tempQR.png")
        self.QR = wand.image.Image(filename = 'tempQR.png')
        # self.QR.transform( resize="200x200>")
    
    def make_label(self, species_string, cultivar_string, nursery_string, plantID_string, country_string, isOrganic, species_nl="", label1=" ", label2=" ", label3=" ", label4 =" ", label5 =" ", overwrite = True, price = " "):
            # 
            #
            #
            fname = "label_"+plantID_string+".png"
            if( overwrite == False):
                if(  os.path.isfile('labels/' + fname ) ):
                    print("File exists, skipping " + fname)
                    return () #Skip making this one if it exists

            self.load_images()
            self.generate_qr("https://kwekerijculinair.nl/t/"+plantID_string)
            ppimage = wand.image.Image(width=WIDTH,height=HEIGHT)
            ppimage.background_color = wand.image.Color("white")
            ppimage.alpha_channel = "remove"
            # Assemble the image
            ppimage.composite( self.EUflag, left = 200, top = 15 )
            ppimage.composite( self.Logo, left = 1700, top = 15 )
            
            
              # Euro-leaf if organic
            if( isOrganic ):
                # TODO - fix the BIO-label-info later!
                ppimage.composite( self.EUleaf, left = 430, top = 10 )
                
            # add the QR code image
            ppimage.composite( self.QR, left = 760, top = -10 )
           
            
            # create ABCD-text image
            ABCD = wand.image.Image(width = 600, height = 300)

            #ABCD = wand.image.Image()
            lineheight = int(200/6)
            textwidth = 300
            
            with wand.drawing.Drawing() as drw:
                drw.font_family = 'Times New Roman, Nimbus Roman No9'
                drw.font_family = 'Arial, Calibri'
                drw.font_family = '-*-helvetica-*-r-*-*-25-*-*-*-*-138-*-*'
                # drw.font_family = '-*-fixed-*-*-normal-*-24-*-*-100-*-*-iso8859-*'
                
                drw.font_size = 25
                drw.font_weight = 800
                drw.text_kerning = -1
                drw.text_kerning = 0
                #drw.text("Plant Passport", left=0, baseline=40)
                #drw.text(x = 0, y = lineheight, body = "Plant Passport" )
                ppimage.annotate("Plant Passport", drw, left = 320, baseline = 10+lineheight)
                #drw.draw(ABCD)
                drw.font_weight = 400
                drw.text(x = 0, y = lineheight*5+20, body=  "A " + species_string )
                drw.text(x = 0, y = lineheight*6+20, body=  "B " + nursery_string )
                drw.text(x = textwidth, y = lineheight*5+20, body=  "C " + plantID_string )
                drw.text(x = textwidth, y = lineheight*6+20, body=  "D " + country_string )
                #ABCD.text("    " + cultivar_string, drw, left=0, baseline=120)
                #ABCD.text("B. " + nursery_string, drw, left=0, baseline=160)
                #ABCD.text("C. " + plantID_string, drw, left=0, baseline=200)
                #ABCD.text("D. " + country_string, drw, left=0, baseline=240)
                drw.draw(ABCD)
                #drw.clear()
                        
            # scale ABCD-image to perfectly fit between the EU flag and QR code
            ABCD.trim( )
            ABCD.transform( resize='600x200>')
            # add ABCD image to ppimage
            ppimage.composite( ABCD, left = 200, top = 130 )
            
            InfoText = wand.image.Image(width = 1200, height = 300)
            lineheight = int(200/6)
            #print("lineheight: " + str(lineheight) ) 
            textwidth = 300
            
            with wand.drawing.Drawing() as drw:
                drw.font_family = 'Times New Roman, Nimbus Roman No9'
                drw.font_family = 'Arial, Calibri'
                drw.font_family = '-*-helvetica-*-r-*-*-34-*-*-*-*-138-*-*'

                drw.font_size = 34
                drw.font_weight = 800
                drw.text_kerning = -1
                drw.text_kerning = 0
                #drw.text("Plant Passport", left=0, baseline=40)
                #drw.text(x = 0, y = lineheight, body = "Plant Passport" )
                if len( cultivar_string ) > 1:
                        species_name = species_nl + " '" + cultivar_string+"'"
                else:
                        species_name = species_nl 
                ppimage.annotate( species_name , drw, left = 1000, baseline = int(lineheight*1.5))
                #drw.draw(ABCD)
                drw.font_weight = 400
                drw.font_family = '-*-helvetica-*-r-*-*-25-*-*-*-*-138-*-*'
                drw.font_size = 25
                drw.text(x = 0, y = lineheight*5+20, body=  label1)
                drw.text(x = 0, y = lineheight*6+20, body=  label2)
                drw.text(x = 0, y = lineheight*7+20, body=  "Lees meer op kwekerijculinair.nl of scan de QR-code")
                drw.text(x = textwidth, y = lineheight*5+20, body=  label3)
                drw.text(x = textwidth, y = lineheight*6+20, body=  label4)
                #ABCD.text("    " + cultivar_string, drw, left=0, baseline=120)
                #ABCD.text("B. " + nursery_string, drw, left=0, baseline=160)
                #ABCD.text("C. " + plantID_string, drw, left=0, baseline=200)
                #ABCD.text("D. " + country_string, drw, left=0, baseline=240)
                
                drw.font_family = '-*-helvetica-*-r-*-*-34-*-*-*-*-138-*-*'
                drw.font_size = 34
                drw.font_weight = 400
                drw.text(x = textwidth*3, y = lineheight*7+20, body=  price)
                drw.draw(InfoText)
                #drw.clear()
                        
            # scale InfoText-image 
            InfoText.trim( )
            InfoText.transform( resize='1200x200>')
            # add ABCD image to ppimage
            ppimage.composite( InfoText, left = 1000, top = 100 )
            
            # Insect-friendly - label5 == 1
            if( label5 == "1"):
                ppimage.composite( self.Butterfly, left = 1600, top = 80)
                
           
            # save the image
            fname = "label_"+plantID_string+".png"
            # If this label has been printed - we do not generate a new label .png file. This helps to keep track of printed/not printed labels. 
            if( os.path.isfile('labels/printed/' + fname ) ):
                pass
            else:
                #ppimage.save( filename = "labels/" + fname )
                # Quantize monochrome - sharp black/white
                ppimage.quantize(2,       # Target colors
                 'gray',  # Colorspace
                 1,       # Treedepth
                 False,   # No Dither
                 False)   # Quantization error
                ppimage.save( filename = "labels/" + fname )
                 
            self.ppimage = ppimage.clone()
            # print the image
            pass
            
    def __init__(self, species_string="", cultivar_string="", nursery_string="", plantID_string="", country_string="", isOrganic=False, species_nl=" ", label1=" ", label2=" ", label3=" ", label4 =" ", label5 =" ", overwrite = True, price = " "):
        #
        if( species_string == ""):
            pass
        else:
            self.make_label(  species_string, cultivar_string, nursery_string, plantID_string, country_string, isOrganic, species_nl, label1, label2, label3, label4, label5, overwrite, price)
         
# Test the class 
if __name__ == "__main__":
    p = Plantpassport()
    p.make_label("Castanea sativa","Marron de Lyon","NL-150390416",'18-012345','NL', False, "Tamme kastanje", "6-15 m hoog", "volle zon", "oogsttijd oktober", "kastanjes vallen op de grond","1", overwrite = False, price="\u20ac 10")
    
    p2 = Plantpassport("Castanea sativa x cr.","Maraval",'NAK123','18-12100','NL',isOrganic = True)
