import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from ui.Ui_SettingsWin import Ui_IgeSettingsWin

class IgeSettings(QDialog):
    """ Class resposible for Settings window.

    It doesn't hold project settings.
    """

    def __init__(self, Settings):

        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_IgeSettingsWin()
        self.ui.setupUi(self)

        self.Settings = Settings

        

    @pyqtSlot()
    def on_butInstead_clicked(self):
        """ choose INSTEAD """
        
        Path = QFileDialog.getOpenFileName(self,
                                    "Путь к интерпретатору INSTEAD",
                                    os.getenv("HOME"),
                                    "Интерпретатор INSTEAD (sdl-instead sdl-instead.exe)")
        if Path != "":
            self.ui.Path.setText(Path)


    @pyqtSlot(bool)
    def on_Cleanlooks_clicked(self, state):
        self.ui.DefColor.setEnabled(state)

    @pyqtSlot()
    def on_butOk_clicked(self):
        self.Settings.setValue("instead/path", self.ui.Path.text())
        self.Settings.setValue("instead/options", self.ui.Options.text())
        self.Settings.setValue("font/name", self.ui.FontName.currentFont().family())
        self.Settings.setValue("font/size", self.ui.FontSize.currentText())
        self.Settings.setValue("main/load_last_proj", self.ui.LastLoad.isChecked())
        self.Settings.setValue("main/backup", self.ui.Backup.isChecked())
        self.Settings.setValue("main/cleanlooks", self.ui.Cleanlooks.isChecked())
        self.Settings.setValue("main/cleanlooks_defcolor", self.ui.DefColor.isChecked())

        self.Settings.setValue("editor/wrap_strings", self.ui.WrapStrins.isChecked())
        self.Settings.setValue("editor/autocompletion", self.ui.Autocompletion.isChecked())
        self.Settings.setValue("editor/tab_size", self.ui.TabSize.currentText())
        self.Settings.setValue("editor/confirm_delete", self.ui.ConfirmDelete.isChecked())
        self.Settings.setValue("editor/use_spaces", self.ui.UseSpaces.isChecked())
        self.Settings.setValue("editor/braces_completion", self.ui.BracesCompletion.isChecked())
        self.Settings.setValue("editor/autocomma", self.ui.AutoComma.isChecked())


    @pyqtSlot()
    def on_butDefault_clicked(self):
        """ set default settings"""
        self.ui.Options.setText("-debug -noautosave -gamespath %1 -game %2")
        self.ui.FontName.setCurrentFont(QFont("Courier New"))
        self.ui.FontSize.setCurrentIndex(self.ui.FontSize.findText("13"))
        self.ui.LastLoad.setChecked(True)
        self.ui.Backup.setChecked(True)
        self.ui.DefColor.setEnabled(False)
        self.ui.DefColor.setChecked(False)
        self.ui.Cleanlooks.setChecked(False)
        self.ui.WrapStrins.setChecked(True)
        self.ui.Autocompletion.setChecked(False)
        self.ui.ConfirmDelete.setChecked(True)
        self.ui.TabSize.setCurrentIndex(self.ui.TabSize.findText('4'))
        self.ui.UseSpaces.setChecked(False)
        self.ui.BracesCompletion.setChecked(True)
        self.ui.AutoComma.setChecked(True)


    def showEvent(self, event):
        """ init form fields """
        self.ui.Path.setText(self.Settings.value("instead/path", ""))
        self.ui.Options.setText(self.Settings.value("instead/options", "-debug -noautosave -gamespath %1 -game %2"))
        self.ui.FontName.setCurrentFont(QFont(self.Settings.value("font/name", "Courier New")))
        self.ui.FontSize.setCurrentIndex(self.ui.FontSize.findText(self.Settings.value("font/size", "13")))
        self.ui.LastLoad.setChecked(str(self.Settings.value("main/load_last_proj", "true")).lower() == "true")
        self.ui.Backup.setChecked(str(self.Settings.value("main/backup", "true")).lower() == "true")
        self.ui.Cleanlooks.setChecked(str(self.Settings.value("main/cleanlooks", "false")).lower() == "true")
        self.ui.DefColor.setEnabled(self.ui.Cleanlooks.isChecked())
        self.ui.DefColor.setChecked(str(self.Settings.value("main/cleanlooks_defcolor", "false")).lower() == "true")
        self.ui.WrapStrins.setChecked(str(self.Settings.value("editor/wrap_strings", "true")).lower() == "true")
        self.ui.Autocompletion.setChecked(str(self.Settings.value("editor/autocompletion", "false")).lower() == "true")
        self.ui.ConfirmDelete.setChecked(str(self.Settings.value("editor/confirm_delete", "true")).lower() == "true")
        self.ui.TabSize.setCurrentIndex(self.ui.TabSize.findText(self.Settings.value("editor/tab_size", "4")))
        self.ui.UseSpaces.setChecked(str(self.Settings.value("editor/use_spaces", "false")).lower() == "true")
        self.ui.BracesCompletion.setChecked(str(self.Settings.value("editor/braces_completion", "true")).lower() == "true")
        self.ui.AutoComma.setChecked(str(self.Settings.value("editor/autocomma", "true")).lower() == "true")
        




    
