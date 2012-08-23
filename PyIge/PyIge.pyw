#!/usr/bin/python3
import sys
import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    from ui.Ui_MainWindow import Ui_MainWindow
    from ui.Ui_AboutWin import Ui_AboutForm
    from ui.Ui_NewSceneDlg import Ui_NewSceneDlg
    from IgeProjWin import *
    from IgeSettings import *
except:
    import compile
    compile.main(sys.argv)
    from ui.Ui_MainWindow import Ui_MainWindow
    from ui.Ui_AboutWin import Ui_AboutForm
    from ui.Ui_NewSceneDlg import Ui_NewSceneDlg
    from IgeProjWin import *
    from IgeSettings import *


from MainIge import *
from IgeXmlProject import *
from IgeEditor import *
from aspell import *


class IgeMainWin(QMainWindow,  IgeMain):
    """ Class representing main form of the application."""

    def __init__(self):
        QMainWindow.__init__(self)
        IgeMain.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.AddWidgets()

        self.RestoreFormState()

        # Style of GUI
        # Cleanlooks is prety!!!
        if str(self.Settings.value("main/cleanlooks", "false")).lower() == "true":
            QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
            if str(self.Settings.value("main/cleanlooks_defcolor", "false")).lower() == "true":
                QApplication.setPalette(QApplication.style().standardPalette())
        
        self.SetEditorSettings()    

        # project path on the status-bar
        self.LabelPath = QLabel()
        self.statusBar().addPermanentWidget(self.LabelPath, 100)

        self.ui.Code.connect(self.ui.Code, SIGNAL("MouseMove"), self.CodeMouseMove)
        self.ui.Code.connect(self.ui.Code, SIGNAL('MouseDoubleClick'), self.CodeMouseDoubleClick)

        self.ui.LineNumber.installEventFilter(self)

        self.UpdateUi()

        self.Game.Changed = False
        
        #error_indicator (for spelling)
        self.ui.Code.indicatorDefine(self.ui.Code.INDIC_CONTAINER+1, self.ui.Code.INDIC_SQUIGGLE, 255)#Qt.red not effect :(

    def AddWidgets(self):
        self.ui.SceneCode = IgeEditor(self.ui.SceneSplitter)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.SceneCode.sizePolicy().hasHeightForWidth())
        self.ui.SceneCode.setSizePolicy(sizePolicy)
        self.ui.SceneCode.setSizeIncrement(QSize(10, 0))
        self.ui.SceneCode.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.SceneCode.setObjectName("SceneCode")

        self.ui.ObjCode = IgeEditor(self.ui.ObjSplitter)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.ObjCode.sizePolicy().hasHeightForWidth())
        self.ui.ObjCode.setSizePolicy(sizePolicy)
        self.ui.ObjCode.setSizeIncrement(QSize(10, 0))
        self.ui.ObjCode.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.ObjCode.setObjectName("ObjCode")

        self.ui.FuncCode = IgeEditor(self.ui.FuncSplitter)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.FuncCode.sizePolicy().hasHeightForWidth())
        self.ui.FuncCode.setSizePolicy(sizePolicy)
        self.ui.FuncCode.setSizeIncrement(QSize(10, 0))
        self.ui.FuncCode.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.FuncCode.setObjectName("FuncCode")

        self.ui.DlgCode = IgeEditor(self.ui.DlgSplitter)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.DlgCode.sizePolicy().hasHeightForWidth())
        self.ui.DlgCode.setSizePolicy(sizePolicy)
        self.ui.DlgCode.setSizeIncrement(QSize(10, 0))
        self.ui.DlgCode.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.DlgCode.setObjectName("DlgCode")

        self.ui.Code = IgeEditor(self.ui.CodeTab)
        self.ui.Code.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.Code.setObjectName("Code")
        self.ui.verticalLayout.addWidget(self.ui.Code)



    def UpdateUi(self, Lists = True):
        # fill scene list, position on GLOBAL_CONTEXT, update SceneCode
        if Lists:
            self.UpdateList(self.ui.SceneList, GLOBAL_CONTEXT)
            self.UpdateList(self.ui.ObjList)
            self.UpdateList(self.ui.DlgList)
            self.UpdateList(self.ui.FuncList)

        # strange call. but we need it to update our main.lua
        # and game.lua code and define wether code was checked
        self.on_Tabs_currentChanged(4)

        self.LabelPath.setText('"' + self.Game.Settings['Name'] + '"  ' + self.ProjPath)

        self.UpdateApi()
  

    def SetEditorSettings(self):
        """ Set editor settings"""

        for CodeWidget in (self.ui.SceneCode,
                           self.ui.DlgCode,
                           self.ui.ObjCode,
                           self.ui.FuncCode,
                           self.ui.Code):
            # Setting Utf-8 for editors
            CodeWidget.setUtf8(True)
            # Setting Lua-lexer for editors
            CodeWidget.setLexer(self.LuaLexer)

            # Wrap strings
            if str(self.Settings.value('editor/wrap_strings', 'true')).lower() == 'true':
                CodeWidget.setWrapMode(QsciScintilla.WrapMode(1))
                CodeWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            else:
                CodeWidget.setWrapMode(QsciScintilla.WrapMode(0))
                CodeWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            #Tab and Indentation settings
            Width = int(self.Settings.value('editor/tab_size', 4))
            CodeWidget.setIndentationWidth(Width)
            CodeWidget.setTabWidth(Width)
            UseSpaces = (str(self.Settings.value('editor/use_spaces', 'false')).lower() == 'true')
            CodeWidget.setIndentationsUseTabs(not UseSpaces)
            #CodeWidget.setTabIndents(True)

            #autocompletion
            CodeWidget.Completion = (str(self.Settings.value('editor/autocompletion', 'false')).lower() == 'true')

            #braces completion
            CodeWidget.BracesCompletion = (str(self.Settings.value('editor/braces_completion', 'true')).lower() == 'true')

            # it's not editor options but it's easier to set them here
            self.ConfirmRemove =  (str(self.Settings.value('editor/confirm_delete', 'true')).lower() == 'true')
            self.Game.AutoComma = (str(self.Settings.value('editor/autocomma', 'true')).lower() == 'true')

            
        # Show line numbers for code
        self.ui.Code.setMarginLineNumbers (1, True)
        self.ui.Code.setMarginWidth(1, 60)

        # Set code read only
        self.ui.Code.setReadOnly(True)
        
    def RestoreFormState(self):
        Pos = self.Settings.value("form/pos", QPoint(100, 100))
        Size = self.Settings.value("form/size", QSize(800, 600))
        self.resize(Size)
        self.move(Pos)

        toolbar = (str(self.Settings.value("form/toolbar", "true")).lower() == "true")
        statusbar = (str(self.Settings.value("form/statusbar", "true")).lower() == "true")
        self.ui.toolBar.setVisible(toolbar)
        self.ui.actionShowToolbar.setChecked(toolbar)
        self.ui.statusBar.setVisible(statusbar)
        self.ui.actionShowStatusbar.setChecked(statusbar)


    def SaveFormState(self):
        self.Settings.setValue("form/pos", self.pos())
        self.Settings.setValue("form/size", self.size())

        self.Settings.setValue("form/toolbar", self.ui.toolBar.isVisible())
        self.Settings.setValue("form/statusbar", self.ui.statusBar.isVisible())


    def closeEvent(self, event):
        """ catch form close"""
        if self.MaybeSave() == QMessageBox.Cancel:
            event.ignore()
            return
              
        self.SaveFormState()

        # Current project = Last project
        if self.ProjPath not in {None, ""}:
            self.Settings.setValue("main/last_proj", self.ProjPath)
        else:
            self.Settings.setValue("main/last_proj", "")
            
        event.accept()


    def MaybeSave(self):
        self.CommitCode()
        Reply = QMessageBox.No
        if self.Game.Changed:
            Reply = QMessageBox.question(self,
                                         "Вопрос",
                                         "Проект изменен. Сохранить изменения в проекте?",
                                         QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if Reply == QMessageBox.Yes:
                Reply = self.Save()
                
        return Reply


    def CommitCode(self):
        """ Save code from TextEdits to memory"""
        try:
            # save all code
            self.Game.SetCode(self.ui.SceneList.currentItem().text(), self.ui.SceneCode.text())
        except:
            # if currentItem does not exist
            pass
        try:
            self.Game.SetCode(self.ui.ObjList.currentItem().text(), self.ui.ObjCode.text())
        except:
            pass
        try:
            self.Game.SetCode(self.ui.DlgList.currentItem().text(), self.ui.DlgCode.text())
        except:
            pass
        try:
            self.Game.SetCode(self.ui.FuncList.currentItem().text(), self.ui.FuncCode.text())
        except:
            pass


    def Save(self, SaveAs = False):
        """
        This function saves current Project

        @param SaveAs - open a dialog for saving the project in a custom project file
        """

        self.CommitCode()

        if self.ProjPath in {None, ""} or SaveAs:
            # Show save dialog
            OldProjPath = self.ProjPath 
            self.ProjPath = QFileDialog.getSaveFileName(self, "Сохранить проект",
                        os.getenv('HOME'),
                        "INSTEAD Project file (*.ipf);; Any file (*.*)")
            if self.ProjPath in {None, ""}:
                self.ProjPath = OldProjPath #in case of canselling SaveAs
                return QMessageBox.Cancel

        if self.ProjPath[-4:].lower() != '.ipf':
            self.ProjPath += '.ipf'

        self.GameXmlProject = IgeXmlProject(self.Game)
        Backup = (str(self.Settings.value("main/backup", "true")).lower() == "true")
        self.GameXmlProject.Save(self.ProjPath, Backup)
        self.Game.Changed = False
        self.UpdateUi(False)
        return QMessageBox.Yes


    def UpdateList(self, List, PositionOnItem = 0):
        """ Update List. It's needed when item added/deleted/changed"""

        if List == self.ui.SceneList:
            Type = SCENE
            CodeEditor = self.ui.SceneCode
        elif List == self.ui.ObjList:
            Type = OBJECT
            CodeEditor = self.ui.ObjCode
        elif List == self.ui.DlgList:
            Type = DIALOG
            CodeEditor = self.ui.DlgCode
        elif List == self.ui.FuncList:
            Type = FUNCTION
            CodeEditor = self.ui.FuncCode

        # I need this call because List.clear() initiate
        # on_SceneList_currentItemChanged which make a lot of troubles for me
        # IT'S STUPID!
        try:
            CodeEditor.setText(self.Game.GetCode(List.currentItem().text()))
        except:
            pass
        List.clear()

        # inserting names
        for Item in self.Game.GetNames(Type, True, True):
            List.addItem(Item)

        if Type == SCENE:
            for Item in self.Game.GetNames(XSCENE):
                List.addItem(Item)
                curItem = List.item(List.count()-1)
                font = curItem.font()
                font.setBold(True)
                curItem.setFont(font)



        # positioning on the item
        if type(PositionOnItem) == QListWidgetItem: # if got Item
            List.setCurrentItem(PositionOnItem)
        elif type(PositionOnItem) == str:   # if got item name
            List.setCurrentItem(self.FindItem(List, PositionOnItem))
        elif type(PositionOnItem) == int: # got it number
            List.setCurrentItem(List.item(PositionOnItem))
        List.setItemSelected(List.currentItem(), True)

        # Update Code 
        try:
            CodeEditor.setText(self.Game.GetCode(List.currentItem().text()))
        except:
            # probably no items in the list
            CodeEditor.setText("")

        self.UpdateApi()


    def FindItem(self, List, Name):
        """ Searches Item in the list by name"""
        for i in range(List.count()):
            if List.item(i).text() == Name:
                return List.item(i)


#################################   SLOTS   ###################################

    ###########################################################################
    #   Slots that relate to Scene tab
    ###########################################################################
    @pyqtSlot()
    def on_actionExit_triggered(self):
        """ Exit function"""
        self.close()


    @pyqtSlot('QListWidgetItem*', 'QListWidgetItem*')
    def on_SceneList_currentItemChanged(self, NextItem, PrevItem):

        """User choose another scene. We must update the code."""
        try:
            # It's always some errors here =(
            # save the old code
            self.Game.SetCode(PrevItem.text(), self.ui.SceneCode.text())
            # set new code
            self.ui.SceneCode.setText(self.Game.GetCode(NextItem.text()))
        except:
            pass
    

    @pyqtSlot()
    def on_butAddScene_clicked(self):
        """Add new scene"""
        dlg = QDialog(self)
        NewSceneDlg = Ui_NewSceneDlg()
        NewSceneDlg.setupUi(dlg)
        NewSceneDlg.label.setText('Имя сцены')
        if dlg.exec():
            name = NewSceneDlg.SceneName.text()
            xroom = NewSceneDlg.xroom.isChecked()
            if name in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butAddScene_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", name)
            if name == "" or s == None or s.group() != name:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butAddScene_clicked()
                return

            self.CommitCode()

            if xroom:
                templ = 'xroom.txt'
            else:
                templ = 'room.txt'
            SceneCode = self.ReadTemplate(templ)[0]

            if xroom:
                room_type = XSCENE
            else:
                room_type = SCENE

            self.Game.AddItem(room_type, name, SceneCode)
            self.UpdateList(self.ui.SceneList, name)



    @pyqtSlot()
    def on_butDelScene_clicked(self):
        RoomName = self.ui.SceneList.currentItem().text()
        if RoomName in {GLOBAL_CONTEXT, MAIN_SCENE}:
            QMessageBox.information(self, "Внимание!", "Невозможно удалить комнату " + RoomName)
            return
        if (not self.ConfirmRemove or
            QMessageBox.question(self, "Вопрос!",
                             "Вы уверены, что хотите удалить команту " + RoomName + "?",
                             QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            self.Game.DelItem(RoomName)
            self.UpdateList(self.ui.SceneList)


    @pyqtSlot()
    def on_butRenameScene_clicked(self):
        self.CommitCode()
        if self.ui.SceneList.currentItem().text() in {GLOBAL_CONTEXT, MAIN_SCENE}:
            QMessageBox.information(self, "Внимание!", "Невозможно переименовать эту комнату")
            return

        temp = QInputDialog.getText(self, "Переименовать", "Новое имя")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butRenameScene_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", temp[0])
            if temp[0] == "" or s == None or s.group() != temp[0]:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butRenameScene_clicked()
                return

            self.Game.RenameItem(self.ui.SceneList.currentItem().text(), temp[0])
            self.UpdateList(self.ui.SceneList, temp[0])
            
    @pyqtSlot()
    def on_butChangeRoom_clicked(self):
        self.CommitCode()
        Name = self.ui.SceneList.currentItem().text()
        if Name in {GLOBAL_CONTEXT, MAIN_SCENE}:
            QMessageBox.information(self, "Внимание!", "Невозможно изменить тип этой комнаты")
            return

        if self.Game.GetType(Name) == SCENE:
            self.Game.SetType(Name, XSCENE)
        else:
            self.Game.SetType(Name, SCENE)

        self.UpdateList(self.ui.SceneList, Name)

    ###########################################################################
    #   Slots that relate to Object tab
    ###########################################################################

    @pyqtSlot('QListWidgetItem*', 'QListWidgetItem*')
    def on_ObjList_currentItemChanged(self, NextItem, PrevItem):
        """User choose another object. We must update the code."""
        try: 
            # It's always some errors here =(
            # I can't understand what happens but it usually works
            # Possible reason is that when selection is changed but item haven't created yet
            # or have been deleted, PrevItem or NextItem are wrong or None or something.

            # save the old code
            self.Game.SetCode(PrevItem.text(), self.ui.ObjCode.text())
            # set new code
            self.ui.ObjCode.setText(self.Game.GetCode(NextItem.text()))
        except:
            pass


    @pyqtSlot()
    def on_butAddObj_clicked(self):
        """Add new object"""

        temp = QInputDialog.getText(self, "Новый объект", "Имя объекта")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butAddObj_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", temp[0])
            if temp[0] == "" or s == None or s.group() != temp[0]:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butAddObj_clicked()
                return

            self.CommitCode()

            ObjectCode = self.ReadTemplate('obj.txt')[0]

            self.Game.AddItem(OBJECT, temp[0], ObjectCode)
            self.UpdateList(self.ui.ObjList, temp[0])



    @pyqtSlot()
    def on_butDelObj_clicked(self):
        ObjName = self.ui.ObjList.currentItem().text()
        if (not self.ConfirmRemove or
            QMessageBox.question(self, "Вопрос!",
                             "Вы уверены, что хотите удалить " + ObjName + "?",
                             QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            self.Game.DelItem(ObjName)
            self.UpdateList(self.ui.ObjList)


    @pyqtSlot()
    def on_butRenameObj_clicked(self):
        self.CommitCode()
        temp = QInputDialog.getText(self, "Переименовать объект", "Новое имя")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butRenameObj_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", temp[0])
            if temp[0] == "" or s == None or s.group() != temp[0]:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butRenameObj_clicked()
                return
            
            self.Game.RenameItem(self.ui.ObjList.currentItem().text(), temp[0])
            self.UpdateList(self.ui.ObjList, temp[0])


    ###########################################################################
    #   Slots that relate to Dialog tab
    ###########################################################################

    @pyqtSlot('QListWidgetItem*', 'QListWidgetItem*')
    def on_DlgList_currentItemChanged(self, NextItem, PrevItem):
        """User choose another object. We must update the code."""
        try: 
            # It's always some errors here =(
            # I can't understand what happens but it usually works
            # Possible reason is that when selection is changed but item haven't created yet
            # or have been deleted, PrevItem or NextItem are wrong or None or something.

            # save the old code
            self.Game.SetCode(PrevItem.text(), self.ui.DlgCode.text())
            # set new code
            self.ui.DlgCode.setText(self.Game.GetCode(NextItem.text()))
        except:
            pass


    @pyqtSlot()
    def on_butAddDlg_clicked(self):
        """Add new object"""

        temp = QInputDialog.getText(self, "Новый диалог", "Имя диалога")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butAddDlg_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", temp[0])
            if temp[0] == "" or s == None or s.group() != temp[0]:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butAddDlg_clicked()
                return

            self.CommitCode()

            DialogCode = self.ReadTemplate('dlg.txt')[0]

            self.Game.AddItem(DIALOG, temp[0], DialogCode)
            self.UpdateList(self.ui.DlgList, temp[0])



    @pyqtSlot()
    def on_butDelDlg_clicked(self):
        DlgName = self.ui.DlgList.currentItem().text()
        if (not self.ConfirmRemove or
            QMessageBox.question(self, "Вопрос!",
                                 "Вы уверены, что хотите удалить " + DlgName + "?",
                                  QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            self.Game.DelItem(DlgName)
            self.UpdateList(self.ui.DlgList)


    @pyqtSlot()
    def on_butRenameDlg_clicked(self):
        self.CommitCode()
        temp = QInputDialog.getText(self, "Переименовать диалог", "Новое имя")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butRenameDlg_clicked()
                return

            # is name right?
            s = re.search(r"[a-zA-Z_]\w*", temp[0])
            if temp[0] == "" or s == None or s.group() != temp[0]:
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Данное имя не является допустимым идентификатором! Введите новое имя.")
                self.on_butRenameDlg_clicked()
                return
            
            self.Game.RenameItem(self.ui.DlgList.currentItem().text(), temp[0])
            self.UpdateList(self.ui.DlgList, temp[0])

    ###########################################################################
    #   Slots that relate to Func tab
    ###########################################################################

    @pyqtSlot('QListWidgetItem*', 'QListWidgetItem*')
    def on_FuncList_currentItemChanged(self, NextItem, PrevItem):
        """User choose another object. We must update the code."""
        try: 
            # It's always some errors here =(
            # I can't understand what happens but it usually works
            # Possible reason is that when selection is changed but item haven't created yet
            # or have been deleted, PrevItem or NextItem are wrong or None or something.

            # save the old code
            self.Game.SetCode(PrevItem.text(), self.ui.FuncCode.text())
            # set new code
            self.ui.FuncCode.setText(self.Game.GetCode(NextItem.text()))
        except:
            pass


    @pyqtSlot()
    def on_butAddFunc_clicked(self):
        """Add new object"""

        temp = QInputDialog.getText(self, "Новая функция", "Имя функции")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butAddFunc_clicked()
                return
            
            # is name right?
            if temp[0] == "":
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Имя функции не может быть пустым.")
                self.on_butRenameFunc_clicked()
                return


            # is name right?
            if temp[0] == "":
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Имя функции не может быть пустым.")
                self.on_butRenameFunc_clicked()
                return

            self.CommitCode()

            FuncCode = self.ReadTemplate('func.txt')[0]

            self.Game.AddItem(FUNCTION, temp[0], FuncCode)
            self.UpdateList(self.ui.FuncList, temp[0])



    @pyqtSlot()
    def on_butDelFunc_clicked(self):
        FuncName = self.ui.FuncList.currentItem().text()
        if (not self.ConfirmRemove or
            QMessageBox.question(self, "Вопрос!",
                                "Вы уверены, что хотите удалить " + FuncName + "?",
                                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            self.Game.DelItem(FuncName)
            self.UpdateList(self.ui.FuncList)


    @pyqtSlot()
    def on_butRenameFunc_clicked(self):
        self.CommitCode()
        temp = QInputDialog.getText(self, "Переименовать функцию", "Новое имя")
        if temp[1]:
            if temp[0] in self.Game.GetNames(ANY):
                # name is owned by someone else
                QMessageBox.information(self, "Внимание!", "Имя уже используется! Введите новое имя.")
                self.on_butRenameFunc_clicked()
                return

            # is name right?
            if temp[0] == "":
                QMessageBox.information(self,
                                        "Внимание!",
                                        "Имя функции не может быть пустым.")
                self.on_butRenameFunc_clicked()
                return

            self.Game.RenameItem(self.ui.FuncList.currentItem().text(), temp[0])
            self.UpdateList(self.ui.FuncList, temp[0])


    ###########################################################################
    #   Slots that relate to Code tab
    ###########################################################################

    @pyqtSlot('QString')
    def on_LineNumber_textChanged(self, Line):
        """ Go to line"""
        try:
            Line = int(Line) - 1
            self.ui.Code.setCursorPosition(Line, 0)
            LineLength = len(self.ui.Code.text(Line))
            self.ui.Code.setSelection(Line, 0, Line, LineLength)
        except:
            pass

    @pyqtSlot(int, int)
    def on_LineNumber_cursorPositionChanged(self, x, y):
        self.on_LineNumber_textChanged(self.ui.LineNumber.text())

    @pyqtSlot(int)
    def on_Tabs_currentChanged(self, Tab):
        """ Tab changed. Reconstruct Code """
        if Tab == 4:
            self.CommitCode()

            # update code in memory
            self.Game.UpdateCode()
            self.Game.AutoComma = (str(self.Settings.value('editor/autocomma', 'true')).lower() == 'true')
            # show
            if self.ui.butMainLua.isChecked():
                self.ui.Code.setText(self.Game.Files['main.lua'])
            elif self.ui.butGameLua.isChecked():
                self.ui.Code.setText(self.Game.Files['game.lua'])
            elif self.ui.butFuncLua.isChecked():
                self.ui.Code.setText(self.Game.Files['func.lua'])

            else: # no one checked???
                self.ui.butMainLua.setChecked(True)
                self.ui.Code.setText(self.Game.Files['main.lua'])

            if self.isOrf:
                self.NextBadWord()

        
    @pyqtSlot()
    def on_butMainLua_clicked(self):
        """ Show main.lua code """

        self.ui.butMainLua.setChecked(True)
        self.ui.butGameLua.setChecked(False)
        self.ui.butFuncLua.setChecked(False)
        self.ui.Code.setText(self.Game.Files['main.lua'])

        if self.isOrf:
            self.NextBadWord()


    @pyqtSlot()
    def on_butGameLua_clicked(self):
        """ Show main.lua code """

        self.ui.butGameLua.setChecked(True)
        self.ui.butMainLua.setChecked(False)
        self.ui.butFuncLua.setChecked(False)
        self.ui.Code.setText(self.Game.Files['game.lua'])

        if self.isOrf:
            self.NextBadWord()

    @pyqtSlot()
    def on_butFuncLua_clicked(self):
        """ Show func.lua code """

        self.ui.butFuncLua.setChecked(True)
        self.ui.butGameLua.setChecked(False)
        self.ui.butMainLua.setChecked(False)
        self.ui.Code.setText(self.Game.Files['func.lua'])

        if self.isOrf:
            self.NextBadWord()


    ###########################################################################
    #   Slots that respond to different actions
    ###########################################################################

    @pyqtSlot()
    def on_actionCreateProject_triggered(self):
        """ New project action triggered """
        
        # save changes if needed
        if self.MaybeSave() == QMessageBox.Cancel:
            return
        
        # show New Project dialog
        Params = self.on_actionProjSettings_triggered(new = True)
        if Params != None:
            # create project
            self.NewProject(Params)

            self.UpdateUi()
        self.Game.Changed = False


    @pyqtSlot()
    def on_actionOpenProject_triggered(self):
        """ Open project action triggered """
        if self.MaybeSave() == QMessageBox.Cancel:
            return

        Path = QFileDialog.getOpenFileName(self, "Открыть проект",
                        os.getenv('HOME'),
                        "INSTEAD Project file (*.ipf);; Any file (*.*)")
        if Path == "":
            return

        self.ProjPath = Path
        OldGame = self.Game
        self.Game = IgeGame()
        self.GameXmlProject = IgeXmlProject(self.Game)
        if self.GameXmlProject.Load(self.ProjPath) != 0:
            self.Game = OldGame
            QMessageBox.critical(self,
                                        "Ошибка!",
                                        "Не удалось открыть файл.")
            return
        
        self.UpdateUi()

        self.Game.Changed = False

        
    @pyqtSlot()
    def on_actionSaveProject_triggered(self):
        """ Save project action triggered """
        self.Save(SaveAs = False)



    @pyqtSlot()
    def on_actionSaveProjectAs_triggered(self):
        self.Save(SaveAs = True)

    @pyqtSlot()
    def on_actionProjSettings_triggered(self, new = False):
        """ Show project settings window

        @param new - show empty window
        """
        
        if new:
            ProjWin = IgeProjWin()
        else:
            ProjWin = IgeProjWin(self.Game.Settings)
        if ProjWin.exec():
            Name = ProjWin.ui.ProjectName.text()
            Version = ProjWin.ui.Version.text()
            Author = ProjWin.ui.Author.text()
            Dsc = ProjWin.ui.Dsc.toPlainText()

            # did we change anything?
            if (self.Game.Settings['Name'] != Name or
                self.Game.Settings['Version'] != Version or
                self.Game.Settings['Author'] != Author or
                self.Game.Settings['Description'] != Dsc):

                self.Game.Changed = True
                
            self.Game.Settings['Name'] = Name
            self.Game.Settings['Version'] = Version 
            self.Game.Settings['Author'] = Author
            self.Game.Settings['Description'] = Dsc

            return (self.Game.Settings.copy())

    @pyqtSlot()
    def on_actionPyIgeSettings_triggered(self):
        """ Show PyIge settings"""

        if self.SettingsWin.exec():
            self.InitLua()
            self.SetEditorSettings()
            self.UpdateUi()

    @pyqtSlot()
    def on_actionRunGame_triggered(self):
        #save code
        self.on_Tabs_currentChanged(4)
        
        # does project exist
        if self.ProjPath == "":
            Reply = QMessageBox.information(self, 'Внимание', 
                                            'Перед запуском игры необходимо сохранить проект. Продолжить?',
                                            QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if Reply == QMessageBox.Yes:
                self.Game.Changed = True
                if self.Save(SaveAs = True) != QMessageBox.Yes:
                    self.Game.Changed = False
                    return
            else:
                return

        if self.Settings.value("instead/path", "") == "":
            QMessageBox.information(self,
                                 "Внимание",
                                 "Путь к интерпретатору INSTEAD не задан")
            self.on_actionPyIgeSettings_triggered()
            return
        
        if (self.Game.GenerateGame(os.path.dirname(self.ProjPath)) != 0):
            QMessageBox.critical(self,
                                "Ошибка!",
                                "Не удалось сохранить файлы игры.")
            return

        GameDir = os.path.dirname(self.ProjPath)
        Instead = self.Settings.value("instead/path", "")
        Options = self.Settings.value("instead/options", r"-debug -noautosave -gamespath %1 -game %2")

        os.chdir(os.path.dirname(self.Settings.value("instead/path", "")))

        # stop last session
        try:
            self.Run.kill()
        except:
            pass
        
        self.Run = self.Game.RunGame(GameDir, Instead, Options)
        if self.Run == -1:
            QMessageBox.critical(self,
                    "Ошибка!",
                    "Не удалось запустить игру.")


    #@pyqtSlot()
    #def on_actionInsteadHelp_triggered(self):
    #    manual = os.path.join(self.ExecDir, 'doc', 'manual.pdf')
    #    os.startfile(manual)


    @pyqtSlot()
    def on_actionCreateScene_triggered(self):
        self.ui.Tabs.setCurrentIndex(0)
        self.on_butAddScene_clicked()


    @pyqtSlot()
    def on_actionCreateObj_triggered(self):
        self.ui.Tabs.setCurrentIndex(1)
        self.on_butAddObj_clicked()


    @pyqtSlot()
    def on_actionCreateDlg_triggered(self):
        self.ui.Tabs.setCurrentIndex(2)
        self.on_butAddDlg_clicked()


    @pyqtSlot()
    def on_actionCreateFunc_triggered(self):
        self.ui.Tabs.setCurrentIndex(3)
        self.on_butAddFunc_clicked()


    @pyqtSlot()
    def on_actionAbout_triggered(self):
        """ About dialog """
        About = QDialog()
        ui = Ui_AboutForm()
        ui.setupUi(About)
        About.exec()


    @pyqtSlot()
    def on_butOrf_clicked(self):
        if self.speller == None:
            QMessageBox.information(self, 'Внимание', 'Проверка орфографии недоступна. Проверьте, что aspell правильно установлен')
            self.ui.butOrf.setChecked(False)
            return
        if self.isOrf:
            self.isOrf = False
            self.ui.butOrf.setChecked(False)
            self.ui.butSpellWord.setEnabled(False)
            self.ui.butIgnoreWord.setEnabled(False)
            self.on_Tabs_currentChanged(4)
        else:
            self.isOrf = True
            self.ui.butOrf.setChecked(True)
            self.ui.butSpellWord.setEnabled(True)
            self.ui.butIgnoreWord.setEnabled(True)
            self.on_Tabs_currentChanged(4)


    @pyqtSlot()
    def on_butSpellWord_clicked(self):
        self.CodeMouseDoubleClick(None, -1, self.BadWord[0])
        self.on_Tabs_currentChanged(4)


    @pyqtSlot()
    def on_butIgnoreWord_clicked(self):
        self.IgnoreWord(self.BadWord[1])
        self.on_Tabs_currentChanged(4)
        if self.isOrf:
            self.NextBadWord()


    def NextBadWord(self):
        text = self.ui.Code.text()
        r = re.compile(r".??(?P<word>[а-яА-ЯёЁa-zA-Z0-9]+).??")#Word with en\ru\num-char
        r1=re.compile(r"([а-яА-ЯёЁ])") #has ru-char
        matches = r.finditer(text)
        for word in matches:
            myword = word.group('word')
            if r1.search(myword) and myword not in self.IgnoreList and not self.speller.check(myword)[0]:
                pos = word.start('word')
                line = text.count('\n', 0, pos)
                index = pos - text.rfind('\n', 0, pos)-1
                bytepos = self.ui.Code.positionFromLineIndex(line,index)
                start, end = self.ui.Code.getWordBoundaries(line, index, False)
                byteposend=self.ui.Code.positionFromLineIndex(line,index+end-start)
                self.ui.Code.setIndicatorRange(self.ui.Code.INDIC_CONTAINER+1,bytepos,byteposend-bytepos)
                self.ui.Code.setCursorPosition(line, index)
                self.ui.Code.ensureLineVisible(line)
                self.ui.Code.selectWord(line, index)
                self.BadWord = (bytepos, myword)
                return
                
        QMessageBox.information(self, 'Информация', 'Проверка орфографии закончена')
        self.on_butOrf_clicked()
        self.BadWord = (-1, None)
        return


    def eventFilter(self, o, e):

        #pressing Enter while typing line number
        if type(e) == QKeyEvent:
            if e.key() == 16777220:
                try:
                    Line = int(self.ui.LineNumber.text())
                    if Line > 0:
                        self.CodeMouseDoubleClick(None, Line - 1)
                except:
                    pass
        return False

    @pyqtSlot('QEvent')
    def CodeMouseMove(self, event):
        pos = self.ui.Code.positionFromPoint(event.pos())
        if pos > 0:
            if self.ui.Code.hasIndicator(self.ui.Code.INDIC_CONTAINER+1,pos):
                bytepos = pos 
                line, index = self.ui.Code.lineIndexFromPosition(pos)
                word = self.ui.Code.getWord(line, index, 0, False)
                v = self.speller.check(word)
                if not v[0]:
                    if v[1] == None:
                        text = 'Нет вариантов'
                    else:
                        text = v[1]
                    QToolTip.showText(event.globalPos(), text)


    @pyqtSlot('QEvent')
    def CodeMouseDoubleClick(self, event, goto_line = -1, word_pos = -1):

        """ Jumping from code to object when doubleclicked on code"""

        if goto_line > 0:
            # we know exactly what line
            pos = 0
            line = goto_line
            index = 0
        elif word_pos > 0:
            pos = word_pos
            line, index = self.ui.Code.lineIndexFromPosition(pos)
        else:
            pos = self.ui.Code.positionFromPoint(event.pos())
            line, index = self.ui.Code.lineIndexFromPosition(pos)

        # main.lua
        if self.ui.butMainLua.isChecked():
            for item in self.Game.main_lua:
                if line >= item[0] and line <= item[1]:
                    delta = line - item[0]
                    self.ui.Tabs.setCurrentIndex(0)
                    self.UpdateList(self.ui.SceneList, item[2])
                    self.ui.SceneCode.setCursorPosition(delta, index)
                    self.ui.SceneCode.ensureLineVisible(delta)

                    #line in normal mode. word in spell-checking
                    if self.ui.Code.hasIndicator(self.ui.Code.INDIC_CONTAINER+1,pos):
                        self.ui.SceneCode.selectWord(delta, index)
                    else:
                        self.ui.SceneCode.setSelection(delta, 0, delta + 1, 0)
                    return

        # game.lua
        elif self.ui.butGameLua.isChecked():
            for item in self.Game.game_lua:
                if line >= item[0] and line <= item[1]:
                    delta = line - item[0]

                    # define what list to open
                    if item[3] in {SCENE, XSCENE}:
                        List = self.ui.SceneList
                        Code = self.ui.SceneCode
                        self.ui.Tabs.setCurrentIndex(0)
                    elif item[3] in {OBJECT}:
                        List = self.ui.ObjList
                        Code = self.ui.ObjCode
                        self.ui.Tabs.setCurrentIndex(1)
                    elif item[3] in {DIALOG}:
                        List = self.ui.DlgList
                        Code = self.ui.DlgCode
                        self.ui.Tabs.setCurrentIndex(2)
                    self.UpdateList(List, item[2])
                    Code.setCursorPosition(delta, index)
                    Code.ensureLineVisible(delta)
                    
                    #line in normal mode. word in spell-checking
                    if self.ui.Code.hasIndicator(self.ui.Code.INDIC_CONTAINER+1,pos):
                        Code.selectWord(delta, index)
                    else:
                        Code.setSelection(delta, 0, delta + 1, 0)
                    return


        # func.lua
        if self.ui.butFuncLua.isChecked():
            for item in self.Game.func_lua:
                if line >= item[0] and line <= item[1]:
                    delta = line - item[0]
                    self.ui.Tabs.setCurrentIndex(3)
                    self.UpdateList(self.ui.FuncList, item[2])
                    self.ui.FuncCode.setCursorPosition(delta, index)
                    self.ui.FuncCode.ensureLineVisible(delta)

                    #line in normal mode. word in spell-checking
                    if self.ui.Code.hasIndicator(self.ui.Code.INDIC_CONTAINER+1,pos):
                        self.ui.FuncCode.selectWord(delta, index)
                    else:
                        self.ui.FuncCode.setSelection(delta, 0, delta + 1, 0)

                    return



def main(args):
    app = QApplication(sys.argv)
    window = IgeMainWin()
    window.show()
    sys.exit(app.exec_())


###################### program starts here!!! ###################

if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        pass
    except:
        print("""An internal error occured.  Please report all the output of the program,
including the following traceback, to developers of PyIge.""")
        raise
