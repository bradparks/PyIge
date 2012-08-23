import sys
import shutil
import xml
import xml.dom
import xml.dom.minidom

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from PyIgeApi import *

# I think Python deals with XML easier then Qt, so I choose Python XML module.
# Also, between DOM and SAX I choose DOM.

class IgeXmlProject:
    """A class which is responsible for doing with XML-project file. Reading and writing data to it."""

    def __init__(self,  Game):
        """
        Init procedure
        
        @param Game is refference to the game class
        @param Path is path to the ProjectFile
        """
        
        self.Game = Game


    def Save(self, ProjPath, Backup = False):
        """Save project in XML-project file"""

        # simple DOM realisation
        dom = xml.dom.minidom.getDOMImplementation()
        
        # "Game" - is root element
        # "IGv1" means that XML document is Instead Game of version 1
        DocType = dom.createDocumentType("IGv1", None, None) 
        tree = dom.createDocument(None, "Game", DocType)
        root = tree.documentElement

        #saving settings
        Settings = tree.createElement("Settings")
        Settings.setAttribute("Name", self.Game.Settings['Name'])
        Settings.setAttribute("Version", self.Game.Settings['Version'])
        Settings.setAttribute("Author", self.Game.Settings['Author'])
        Settings.setAttribute("Description", self.Game.Settings['Description'])
        root.appendChild(Settings)

        # Game Items section
        Items = tree.createElement("Items") 
        root.appendChild(Items)

        # xml element presenting Item looks like this
        # <Item Type="Scene" Name="house">text of the scene</Item>
        temp = ((SCENE, "Scene"), (XSCENE, "XScene"), (OBJECT, "Object"), (DIALOG, "Dialog"), (FUNCTION, "Function"))
        for i in range(len(temp)):
            for name in self.Game.GetNames(temp[i][0], True, True):
                element = tree.createElement("Item")
                element.setAttribute("Type", temp[i][1])
                element.setAttribute("Name", name)

                Code = self.Game.GetCode(name)
                if Code == "":
                    # Empty text data is not allowed in XML!
                    Code = " "
                    
                code = tree.createTextNode(Code)
                element.appendChild(code)
                Items.appendChild(element)    

        # make backup
        if Backup:
            try:
                shutil.copyfile(ProjPath, ProjPath + '~')
            except:
                pass

        # writing project file
        file = open(ProjPath,  "tw+", encoding = "utf-8")
        #xml_code = tree.toprettyxml(indent = " "*8)
        #print(xml_code)
        xml_code = tree.toxml()
        file.write(xml_code)


    def Load(self, ProjPath):
        """Load project from XML-project file"""
        try:
            tree = xml.dom.minidom.parse(ProjPath)
            if tree.doctype.name != "IGv1":
                # wrong file or version
                return 1

            #getting settings
            item = tree.getElementsByTagName('Settings')[0]
            self.Game.Settings['Name'] = item.getAttribute('Name')
            self.Game.Settings['Version'] = item.getAttribute('Version')
            self.Game.Settings['Author'] = item.getAttribute('Author')
            self.Game.Settings['Description'] = item.getAttribute('Description')

            # getting items
            for item in tree.getElementsByTagName('Item'):
                Type = item.getAttribute('Type')
                Name = item.getAttribute('Name')
                Code = item.firstChild.data
                types = {"Scene":SCENE, "XScene":XSCENE, "Dialog":DIALOG, "Object":OBJECT, "Function":FUNCTION}
                self.Game.AddItem(types[Type], Name, Code)

            return 0
        except:
            print(sys.exc_info())
            return 1
        

