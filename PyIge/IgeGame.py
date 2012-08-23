import re
import os
import subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import *

from PyIgeApi import *


class IgeGame:
    """Class does scene/object/dialog  adding/removing/renaming 
    and implement other functions serving game-items table like searching etc."""



    def __init__(self):
        # Game settings
        self.Settings = dict(Name = "",
                    Version = "",
                    Author = "",
                    Description = "")
        
        # wether code has been changed
        self.Changed = False

        # Main variable in the program
        # Includes information about all scenes, dialogs and objects
        # It has the following form:
        # [ [SCENE, "house", "...code of the scene.... "], [OBJECT, "knife", "...code for the object..."], ... ... ... ]
        self.__GameItems = []

        self.Files = {'main.lua': '', 'game.lua': '', 'func.lua':''} 


    def AddItem(self,  type,  name,  code):
        self.__GameItems += [[type,  name,  code]]
        self.Changed = True


    def DelItem(self, Name):
        for i in range(len(self.__GameItems)):
            if self.__GameItems[i][1] == Name and Name not in {GLOBAL_CONTEXT, MAIN_SCENE}:
                del self.__GameItems[i]
                self.Changed = True
                break

    def RenameItem(self, OldName, NewName):
        for i in range(len(self.__GameItems)):
            if self.__GameItems[i][1] == OldName and OldName not in {GLOBAL_CONTEXT, MAIN_SCENE}:
                self.__GameItems[i][1] = NewName
                self.Changed = True
    

    def GetNames(self, Type, Main_room = False, Global_room = False):
        result = [Item[1] for Item in self.__GameItems if Type == ANY or (Item[0] == Type and Item[1] not in {GLOBAL_CONTEXT, MAIN_SCENE})]
        result.sort()
        #include special scenes
        if Type == SCENE:
            # main scene and global context should be at the top
            if Main_room:
                result.insert(0, MAIN_SCENE)
            if Global_room:
                result.insert(0, GLOBAL_CONTEXT)
        return result


    def GetCode(self, Name):
        for Item in self.__GameItems:
            if Item[1] == Name:
                return Item[2]


    def SetCode(self, Name, Code):
        for Item in self.__GameItems:
            if Item[1] == Name:
                if Item[2] != Code:
                    Item[2] = Code
                    self.Changed = True

    def GetType(self, Name):
        for Item in self.__GameItems:
            if Item[1] == Name:
                return Item[0]


    def SetType(self, Name, Type):
        for Item in self.__GameItems:
            if Item[1] == Name:
                Item[0] = Type



    def UpdateCode(self):
        """ Function updates main.lua and game.lua in the memory."""

        # tuples that help to match string of code and object from where that string came from
        # tuples have the following structure
        # self.main_lua = [(n1, n2, GLOBAL_CONTEXT),
        #                  (n1, n2, MAIN_SCENE)
        #                 ]
        # game_lua and func_lua are built in the same way
        self.main_lua = list()
        self.game_lua = list()
        self.func_lua = list()


        # filling main.lua
        self.Files['main.lua'] = (  "-- $Name:" + self.Settings['Name'] + "$\n" +
                                    "-- $Version:" + self.Settings['Version'] + "$\n" +
                                    "-- $Author:" + self.Settings['Author'] + "$\n\n" +
                                    'game.dsc = [[' + self.Settings['Description'] + ']];\n\n')
        
        # set global context range
        n1 = self.Files['main.lua'].count('\n')
        gc = self.GetCode(GLOBAL_CONTEXT)
        n2 = gc.count('\n')
        self.main_lua.append((n1, n1 + n2, GLOBAL_CONTEXT, SCENE))
        
        self.Files['main.lua'] += gc + "\n\n\n"
        
        n1 = self.Files['main.lua'].count('\n')
        mainroom = "main = room {\n\t" + self.GetCode(MAIN_SCENE).replace('\n', '\n\t') + "\n};\n\n"
        n2 = mainroom.count('\n')
        self.main_lua.append((n1 + 1, n1 + n2, MAIN_SCENE, SCENE))

        self.Files['main.lua'] += mainroom


        # filling game.lua
        self.Files['game.lua'] = ""
        for name in self.GetNames(XSCENE):
            # xrooms
            n1 = self.Files['game.lua'].count('\n')
            xroom = name + " = " + "xroom {\n\t" + self.GetCode(name).replace('\n', '\n\t') + "\n};"
            n2 = xroom.count('\n')
            self.game_lua.append((n1 + 1, n1 + n2, name, XSCENE))
            self.Files['game.lua'] += xroom + "\n\n"


        for name in self.GetNames(SCENE):
            # rooms
            n1 = self.Files['game.lua'].count('\n')
            room = name + " = " + "room {\n\t" + self.GetCode(name).replace('\n', '\n\t') + "\n};"
            n2 = room.count('\n')
            self.game_lua.append((n1 + 1, n1 + n2, name, SCENE))
            self.Files['game.lua'] += room + "\n\n"
       

        for name in self.GetNames(OBJECT):
            # objects
            n1 = self.Files['game.lua'].count('\n')
            obj = name + " = " + "obj {\n\t" + self.GetCode(name).replace('\n', '\n\t') + "\n};"
            n2 = obj.count('\n')
            self.game_lua.append((n1 + 1, n1 + n2, name, OBJECT))
            self.Files['game.lua'] += obj + "\n\n"


        for name in self.GetNames(DIALOG):
            # dialogs
            n1 = self.Files['game.lua'].count('\n')
            dlg = name + " = " + "dlg {\n\t" + self.GetCode(name).replace('\n', '\n\t') + "\n};"
            n2 = dlg.count('\n')
            self.game_lua.append((n1 + 1, n1 + n2, name, DIALOG))
            self.Files['game.lua'] += dlg + "\n\n"


        # filling func.lua
        self.Files['func.lua'] = ""
        for name in self.GetNames(FUNCTION):
            # functions
            n1 = self.Files['func.lua'].count('\n')
            func = self.GetCode(name)
            n2 = func.count('\n')
            self.func_lua.append((n1, n1 + n2, name, FUNCTION))
            self.Files['func.lua'] += func + "\n\n"


        if self.Autocomma:
            rx = re.compile(r"""
            ^                                       # start of the string
            [ \t]*                                  # tabs and spaces before name
            \w+                                     # name
            [ \t]*                                  # tabs and spaces after name
            =                                       # =
            [ \t]*                                  # tabs and spaces after =
            (                                       # one of the folowing combinations
                        '.*?'                       # string in single quotes
                |                                   # or
                        ".*?"                       # string in double quotes
                |                                   # or
                        \[\[[^\]]*?\]\]             # string in double braces (may be multiline)
                |                                   # or
                        \{[^\{]*?\}                 # string in {} braces
            )                                       # end of the alternatives list
            [ \t]*                                  # tabs and spaces after line
            $                                       # end of the line
            """, re.MULTILINE|re.VERBOSE)
            for file in self.Files.keys():
                while True:
                    m = rx.search(self.Files[file])
                    if m != None:
                        end = m.span(0)[1]
                        self.Files[file] = self.Files[file][0:end] + ',' + self.Files[file][end:]
                    else:
                        break


    def GenerateGame(self, game_dir):

        try:
            main_lua = open(os.path.join(game_dir, "main.lua"), "tw+", encoding = "utf-8")
            main_lua.write(self.Files['main.lua'])
            main_lua.close()

            game_lua = open(os.path.join(game_dir, "game.lua"), "tw+", encoding = "utf-8")
            game_lua.write(self.Files['game.lua'])
            game_lua.close()

            func_lua = open(os.path.join(game_dir, "func.lua"), "tw+", encoding = "utf-8")
            func_lua.write(self.Files['func.lua'])
            func_lua.close()

            return 0
        except:
            #raise
            return 1


    def RunGame(self, GameDir, Instead, Options):
        try:
            dirs = os.path.split(GameDir) # split path into two
            OptList = Options.split()
            for i in range(len(OptList)):
                if OptList[i] == '%1':
                    OptList[i] = dirs[0]
                if OptList[i] == '%2':
                    OptList[i] = dirs[1]
            #Options = Options.replace("%1", dirs[0])
            #Options = Options.replace("%2", dirs[1])
            #Options = Instead + " " + Options
            OptList.insert(0, Instead)
            #print(OptList)
            
            Run = subprocess.Popen(OptList)
            return Run
        except:
            return -1
            #raise


