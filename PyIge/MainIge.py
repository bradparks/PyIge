import os.path
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import *

from PyIgeApi import *
from IgeXmlProject import *
from IgeGame import *
from IgeSettings import *
from aspell import *

class IgeMain:
    """Main class that plays a role of container for other classes,
    keeps settings, and connects GUI with the other stuff. Base class of IgeMainWin."""

       
    def __init__(self):

        # directory from where we started
        self.ExecDir = os.getcwd()
        self.HomeDir = os.path.join(os.path.expanduser('~'), '.PyIge')

        # program settings
        self.Settings = QSettings(os.path.join(self.HomeDir, 'PyIge.conf'),  QSettings.IniFormat)
        self.SettingsWin = IgeSettings(self.Settings)

        # LUA-highliter
        self.InitLua()

        # spell-checker
        self.InitSpell()

        self.isOrf = False
        self.BadWord = (-1, None)

        LastOpened = 1
        if (str(self.Settings.value("main/load_last_proj", "true")).lower() == "true" and 
            os.path.isfile(self.Settings.value("main/last_proj", ""))):

            # open last project
            self.ProjPath = self.Settings.value("main/last_proj", "")
            self.Game = IgeGame()
            self.GameXmlProject = IgeXmlProject(self.Game)
            LastOpened = self.GameXmlProject.Load(self.ProjPath)
            self.Game.Changed = False

        if LastOpened != 0:
        # create an empty project (game class with no params)      
            self.NewProject()
            self.Game.Settings['Name'] = "Новая игра"
            self.ProjPath = ""
            self.Game.Changed = False

            # nothing is opened
            self.GameXmlProject = None
            self.GameGenerator = None

    def InitLua(self):
        # LUA-highliter
        self.LuaLexer = QsciLexerLua()

        FontName = self.Settings.value("font/name", "Courier New")
        FontSize = int(self.Settings.value("font/size", 13))
        
        # simple font for editor
        self.Font = QFont()
        self.Font.setFamily(FontName)
        self.Font.setFixedPitch(True)
        self.Font.setPointSize(FontSize)
        
        # Bold font
        self.BoldFont = QFont()
        
        self.BoldFont.setFamily(FontName)
        self.BoldFont.setFixedPitch(True)
        self.BoldFont.setPointSize(FontSize)
        self.BoldFont.setBold(True)

        self.LuaLexer.setDefaultFont(self.Font)

        # keywords
        self.LuaLexer.setFont(self.BoldFont, 5)
        self.LuaLexer.setColor(Qt.blue, 5)
        
        # operator signes
        self.LuaLexer.setFont(self.BoldFont, 10)
        self.LuaLexer.setColor(Qt.darkBlue, 10)
        
        # numbers
        self.LuaLexer.setColor(QColor.fromRgb(255, 128, 0), 4)
        self.LuaLexer.setFont(self.Font, 4)
        
        # strings like [[ hello ]]
        self.LuaLexer.setColor(Qt.darkMagenta,8)
        self.LuaLexer.setFont(self.Font, 8)
        self.LuaLexer.setPaper(Qt.white, 8)
        
        # strings and symbols
        self.LuaLexer.setColor(Qt.gray,7)
        self.LuaLexer.setFont(self.Font, 7)
        self.LuaLexer.setPaper(Qt.white, 7)
        self.LuaLexer.setColor(Qt.gray,6)
        self.LuaLexer.setFont(self.Font, 6)
        self.LuaLexer.setPaper(Qt.white, 6)
        
        # comments
        self.LuaLexer.setColor(Qt.darkGreen, 2)
        self.LuaLexer.setFont(self.Font, 2)
        self.LuaLexer.setPaper(Qt.white, 2)
        
        # all the rest (black on white)
        self.LuaLexer.setColor(Qt.black, 13)
        self.LuaLexer.setFont(self.Font, 13)
        self.LuaLexer.setPaper(Qt.white, 13)
        self.LuaLexer.setColor(Qt.black, 14)
        self.LuaLexer.setFont(self.Font, 14)
        self.LuaLexer.setPaper(Qt.white, 14)
        self.LuaLexer.setColor(Qt.black, 15)
        self.LuaLexer.setFont(self.Font, 15)
        self.LuaLexer.setPaper(Qt.white, 15)

        self.LuaLexer.setColor(Qt.red, 14)
        self.LuaLexer.setFont(self.BoldFont, 14)
        self.LuaLexer.setPaper(Qt.white, 14)


    def InitSpell(self):
        try:
            Spell_program=self.Settings.value("spell/path", "")
            Spell_options=self.Settings.value("spell/options", None)
            Spell_coding=self.Settings.value("spell/coding", "utf-8")
            self.speller = aspell(Spell_program,Spell_options,Spell_coding)
            self.speller.pipe.stdout.readline() #skip aspell hello line
            path = os.path.join(os.path.expanduser('~'), '.PyIge', 'ignore.txt')
            if not os.path.isfile(path):
                open(path, 'w', encoding = 'utf-8').close()
            self.IgnoreList = open(path, 'r', encoding = 'utf-8').read().split('\n')
            #print(self.IgnoreList)
        except:
            self.speller = None
            self.IgnoreList = None


    def IgnoreWord(self, word):
        if self.IgnoreList != None:
            if word not in self.IgnoreList:
                self.IgnoreList.append(word)

                path = os.path.join(os.path.expanduser('~'), '.PyIge', 'ignore.txt')
                f = open(path, 'a', encoding = 'utf-8')
                f.write(word + '\n')
                f.close()


    def NewProject(self, Params = None):
        """Create a new project.
        
        This function doesn't create a project file. It just (re)creates structure for the future game.
        """
        # Create game class
        self.Game = IgeGame()

        self.ProjPath = ""
        
        if Params != None:
            self.Game.Settings = Params


        #global context
        GlobalContextCode = self.ReadTemplate("global.txt")[0]
        self.Game.AddItem(SCENE,  GLOBAL_CONTEXT, GlobalContextCode)

        # main scene
        MainSceneCode = self.ReadTemplate("main.txt")[0]
        self.Game.AddItem(SCENE,  MAIN_SCENE, MainSceneCode)

        # help scene
        HelpSceneCode = self.ReadTemplate("help.txt")[0]
        self.Game.AddItem(SCENE,  "help", HelpSceneCode)

        #comment function
        CommentCode = self.ReadTemplate("func_help.txt")[0]
        self.Game.AddItem(FUNCTION,  "Comment", CommentCode)


    def ReadTemplate(self, Name):
        
        try:
            join = os.path.join
            TemplateDir = join(self.ExecDir, "templates")
            f = open(join(TemplateDir, Name), "rt", encoding = "utf-8")
            Text = f.read()
            f.close()
            return (Text, True)
        except:
            return ('', False)


    def UpdateApi(self):
        api = QsciAPIs(self.LuaLexer)
        api.clear()
        for name in self.Game.GetNames(ANY):
            api.add(name)
        api.prepare()

