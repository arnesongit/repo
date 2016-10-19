""" repository files and addons.xml generator """

""" Modified by Rodrigo@XMBCHUB to zip plugins/repositories to a "zip" folder """
""" Modified by BartOtten: create a repository addon, skip folders without addon.xml, user config file """

""" This file is "as is", without any warranty whatsoever. Use as own risk """

import os
import md5
import zipfile
import shutil
from xml.dom import minidom
import glob
import datetime
from ConfigParser import SafeConfigParser

class Generator:
    
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from a subdirectory (eg. _tools) of
        the checked-out repo. Only handles single depth folder structure.
    """
    
    def __init__( self ):
       
        """
        Load the configuration
        """
        self.config = SafeConfigParser()
        self.config.read('config.ini')
        
        self.tools_path=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
        self.output_path="_" + self.config.get('locations', 'output_path')
        
        # travel path one up
        os.chdir(os.path.abspath(os.path.join(self.tools_path, os.pardir)))
        
        # generate files
        self._pre_run()
        self._generate_repo_files()
        self._generate_addons_file()
        self._generate_md5_file()
        self._generate_zip_files()
        # notify user
        print "Finished updating addons xml, md5 files and zipping addons"
        
    def _pre_run ( self ):

        # create output  path if it does not exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def _generate_repo_files ( self ):
        
        addonid=self.config.get('addon', 'id')
        name=self.config.get('addon', 'name')
        version=self.config.get('addon', 'version')
        author=self.config.get('addon', 'author')
        summary=self.config.get('addon', 'summary') 
        description=self.config.get('addon', 'description')
        url=self.config.get('locations', 'url')      

        if os.path.isfile(addonid + os.path.sep + "addon.xml"):return
        
        print "Create repository addon"
        
        with open (self.tools_path + os.path.sep + "template.xml", "r") as template:
            template_xml=template.read()
        
        repo_xml = template_xml.format(
            addonid= addonid,
            name=name,
            version=version,
            author=author,
            summary=summary,
            description=description,
            url=url,
            output_path=self.output_path)
        
        # save file
        if not os.path.exists(addonid):
            os.makedirs(addonid)
            
        self._save_file( repo_xml.encode( "utf-8" ), file=addonid + os.path.sep + "addon.xml" )
        

    def _generate_zip_files ( self ):
        addons = os.listdir( "." )
        # loop thru and add each addons addon.xml file
        for addon in addons:
            # create path
            _path = os.path.join( addon, "addon.xml" )         
            #skip path if it has no addon.xml
            if not os.path.isfile( _path ): continue       
            try:
                # skip any file or .git folder
                if ( not os.path.isdir( addon ) or addon == ".git" or addon == self.output_path or addon == self.tools_path): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                document = minidom.parse(_path)
                for parent in document.getElementsByTagName("addon"):
                    version = parent.getAttribute("version")
                    addonid = parent.getAttribute("id")
                self._generate_zip_file(addon, version, addonid)
            except Exception, e:
                print e

    def _generate_zip_file ( self, path, version, addonid):
        print "Generate zip file for " + addonid + " " + version
        filename = path + "-" + version + ".zip"
        try:
            zip = zipfile.ZipFile(filename, 'w')
            for root, dirs, files in os.walk(path + os.path.sep):
                for file in files:
                    zip.write(os.path.join(root, file))
                    
            zip.close()
         
            if not os.path.exists(self.output_path + addonid):
                os.makedirs(self.output_path + addonid)
         
            if os.path.isfile(self.output_path + addonid + os.path.sep + filename):
                os.rename(self.output_path + addonid + os.path.sep + filename, self.output_path + addonid + os.path.sep + filename + "." + datetime.datetime.now().strftime("%Y%m%d%H%M%S") )
            shutil.move(filename, self.output_path + addonid + os.path.sep + filename)
        except Exception, e:
            print e

    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir( "." )
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            # create path
            _path = os.path.join( addon, "addon.xml" )
            #skip path if it has no addon.xml
            if not os.path.isfile( _path ): continue
            try:               
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "utf-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_file( addons_xml.encode( "utf-8" ), file=self.output_path + "addons.xml" )

    def _generate_md5_file( self ):
        try:
            # create a new md5 hash
            m = md5.new( open(self.output_path +  "addons.xml" ).read() ).hexdigest()
            # save file
            self._save_file( m, file=self.output_path + "addons.xml.md5" )
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % ( e, )

    def _save_file( self, data, file ):
        try:
            # write data to the file
            open( file, "w" ).write( data )
        except Exception, e:
            # oops
            print "An error occurred saving %s file!\n%s" % ( file, e, )


if ( __name__ == "__main__" ):
    # start
    Generator()