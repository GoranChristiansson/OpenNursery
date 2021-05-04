#!/usr/bin/python3
#
# webpager.py - generate a html page for each tree in the database
#
# for the Open Source Food Tree Nursery project
# Trees for Peace, Goran Christiansson
#
# v 1.0 Use Jinja2 as templating engine for the webpages
#           Main information on the page = species, when was it grafted/seeded, where does it come from, link to wikipedia
#
# v 1.1 Change foldername to /t/ (so that we can use https and geolocation!)
#        - I need to make index.html files for all existing labels (300 pcs) that forward from http://.../p/ to https://.../t/  so that old labels are still working.
#

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import os

class Webpage:
    
    file_loader = FileSystemLoader('jinjatemplates')
    env = Environment(    autoescape=select_autoescape(['html', 'xml']), loader=file_loader)
    template = env.get_template('plantpage.html.jinja2')
        
    def safe_makedir( self, foldername ):
        try:
            os.mkdir( foldername )  
        except:
            print("warning- folder maybe already exists")
            
    def make_webpage( self, fields, plant_strings ):
            # 
            # We get a list of fields = ["IDNr","Genus","Species" ...]
            #  and a list of plant_strings = ["20-0001","Asimina","triloba",....
            #
            # we fill the basic_template with the right strings, save to a file (and upload to one.com)
            plant_data = {}
            # generate dictionary for jinja
            for f,ps in zip(fields,plant_strings):
                plant_data[f] = ps
            
            print(plant_data )
            webpage = self.template.render( p = plant_data ) 
            
            foldername = "t/" + plant_data["IDNr"]
            self.safe_makedir( foldername )
            filename = "index.html"
            file = open( foldername + "/" + filename, "w")
            file.write( webpage )
            file.close()



         
# Test the class 
if __name__ == "__main__":
    wp = Webpage()
    wp.make_webpage(["IDNr","Genus","Species"],["20-9991","Castanea","mollissima"])
    