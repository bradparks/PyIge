import sys
import os
import MainIge


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui.Ui_ProjWin import Ui_ProjWin

class IgeProjWin(QDialog):
    """ Class that holds Project settings window"""

    def __init__(self, Project = None):
        """Init window. If project is already exist it fill in
        project settings. If not it does nothing.

        @param Project - a structure like (Name, Version, Author,
        Description
        """
        QDialog.__init__(self)
        
        # set up ui
        self.ui = Ui_ProjWin()
        self.ui.setupUi(self)

        if Project != None:
            self.ui.ProjectName.setText(Project['Name'])
            self.ui.Version.setText(Project['Version'])
            self.ui.Author.setText(Project['Author'])
            self.ui.Dsc.setText(Project['Description'])
            


    @pyqtSlot()
    def on_butSetGamePath_clicked(self):
        FileName =  QFileDialog.getExistingDirectory(self, "Каталог проекта",
                                                 os.environ['HOME'],
                                                 QFileDialog.ShowDirsOnly
                                                 | QFileDialog.DontResolveSymlinks);
        if FileName != "":
            self.ui.GamePath.setText(FileName)
            

    @pyqtSlot()
    def on_butSetProjPath_clicked(self):
        FileName = QFileDialog.getSaveFileName(self,
                                               "Сохранить проект",
                                               os.environ['HOME'],
                                               "INSTEAD game project (*.igp);;Any file (*.*)")
        if FileName != "":
            self.ui.ProjPath.setText(FileName)        


    @pyqtSlot()
    def on_butOk_clicked(self):
        if self.ui.ProjectName.text() == "":
            QMessageBox.information(self,
                                    "Внимание",
                                    "Название игры не может быть пустым")     
        else:
            self.accept()
            
