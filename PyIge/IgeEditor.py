import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import *

from QsciScintillaCompat import *

class IgeEditor(QsciScintillaCompat):
    """ Class representin featured editor based on Qscintilla"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoIndent(True)
        self.setEolMode(QsciScintilla.EolUnix)

        #autocompletion
        self.Completion = False
        #completion of braces
        self.BracesCompletion = True

        self.connect(self, SIGNAL("SCN_CHARADDED(int)"), self.__charAdded)

        ######### shortcuts #########
        sh_ctrl_sp = QShortcut(QKeySequence('Ctrl+Space'), self)
        sh_ctrl_sp.connect(sh_ctrl_sp, SIGNAL('activated()'), self.autocomplete)

        # highlite matched braces
        self.setBraceMatching(QsciScintilla.StrictBraceMatch)
        self.setMatchedBraceBackgroundColor(Qt.yellow)


    def mouseMoveEvent(self, event):
        """ Emitting MouseMove signal"""
        self.emit(SIGNAL("MouseMove"), event)
        QsciScintilla.mouseMoveEvent(self, event)


    def mouseDoubleClickEvent(self, event):
        """ Emitting MouseDoubleClick signal """
        self.emit(SIGNAL('MouseDoubleClick'), event)
        QsciScintilla.mouseDoubleClickEvent(self, event)


    def HighliteWord(self, pos, len):
        """ Highlite word

        @param pos - start from position pos
        @param len - highlite len simbols
        !Function clears all other styling and needs to be rewritten!
        """
        self.startStyling(pos, 0xff)
        self.setStyling(len, 14)
        self.startStyling(pos+len, 0)
        self.setStyling(100000, 14)


    @pyqtSlot()
    def autocomplete(self):
        self.autoCompleteFromAPIs()


    def keyPressEvent(self, event):
        #print(event.key())
        if event.key() == 16777218:
            self.unindentLineOrSelection()
            return

        needComplete = self.isListActive()

        QsciScintilla.keyPressEvent(self, event)

        # continue autocompletion if backspase was pressed
        if needComplete and event.key() == 16777219:
            self.autocomplete()

        #autocompletion
        bad_keys = {
                        16777220,
                        16777216,
                        16777217,
                        16777219,
                        16777234,
                        16777235,
                        16777236,
                        16777237,
                        16777239,
                        16777238,
                        16777232,
                        16777233,
                        16777249,
                        16777248,
                        16777251,
                        16777222,
                        16777223,
                        16777222,
                        16777252,
                        16777248,
                        16777249,
                        16777251
                    }
        if self.Completion and event.key() not in bad_keys:
            self.autocomplete()
            return


    def __charAdded(self, char):
        #print(char)
        line, col = self.getCursorPosition()
        if self.BracesCompletion:
            char2 = 0
            if char in {34, 39}:
                char2 = char
            if char == 40:
                char2 = 41
            if char in {91, 123}:
                char2 = char + 2
            if char2 != 0:
                self.insertAt(chr(char2), line, col)

        if self.isListActive():
            self.autocomplete()


    def getWordBoundaries(self, line, index, useWordChars = True):
        """
        Public method to get the word boundaries at a position.

        @param line number of line to look at (int)
        @param index position to look at (int)
        @keyparam useWordChars flag indicating to use the wordCharacters
            method (boolean)
        @return tuple with start and end indices of the word at the position
            (integer, integer)
        """
        text = self.text(line)
        if self.caseSensitive():
            cs = Qt.CaseSensitive
        else:
            cs = Qt.CaseInsensitive
        wc = self.wordCharacters()
        if wc is None or not useWordChars:
            regExp = QRegExp('[^\w_]', cs)
        else:
            regExp = QRegExp('[^%s]' % re.escape(wc), cs)
        start = regExp.lastIndexIn(text, index) + 1
        end = regExp.indexIn(text, index)
        if start == end + 1 and index > 0:
            # we are on a word boundary, try again
            start = regExp.lastIndexIn(text, index - 1) + 1
        if start == -1:
            start = 0
        if end == -1:
            end = len(text)

        return (start, end)

    def getWord(self, line, index, direction = 0, useWordChars = True):
        """
        Public method to get the word at a position.

        @param line number of line to look at (int)
        @param index position to look at (int)
        @param direction direction to look in (0 = whole word, 1 = left, 2 = right)
        @keyparam useWordChars flag indicating to use the wordCharacters
            method (boolean)
        @return the word at that position (string)
        """
        start, end = self.getWordBoundaries(line, index, useWordChars)
        if direction == 1:
            end = index
        elif direction == 2:
            start = index
        if end > start:
            text = self.text(line)
            word = text[start:end]
        else:
            word = ''
        return word


    def PosToLineIndex(self, pos):
        return  (self.text().count('\n', 0, pos), pos - self.text().rfind('\n', 0, pos)-1)

    def getWordLeft(self, line, index):
        """
        Public method to get the word to the left of a position.

        @param line number of line to look at (int)
        @param index position to look at (int)
        @return the word to the left of that position (string)
        """
        return self.getWord(line, index, 1)

    def getWordRight(self, line, index):
        """
        Public method to get the word to the right of a position.

        @param line number of line to look at (int)
        @param index position to look at (int)
        @return the word to the right of that position (string)
        """
        return self.getWord(line, index, 2)

    def getCurrentWord(self):
        """
        Public method to get the word at the current position.

        @return the word at that current position (string)
        """
        line, index = self.getCursorPosition()
        return self.getWord(line, index)

    def selectWord(self, line, index):
        """
        Public method to select the word at a position.

        @param line number of line to look at (int)
        @param index position to look at (int)
        """
        start, end = self.getWordBoundaries(line, index, False)
        self.setSelection(line, start, line, end)

    def selectCurrentWord(self):
        """
        Public method to select the current word.
        """
        line, index = self.getCursorPosition()
        self.selectWord(line, index)


    ############################################################################
    ## Indentation handling methods below
    ############################################################################

    def __indentLine(self, indent = True):
        """
        Private method to indent or unindent the current line.

        @param indent flag indicating an indent operation (boolean)
                <br />If the flag is true, an indent operation is performed.
                Otherwise the current line is unindented.
        """
        line, index = self.getCursorPosition()
        self.beginUndoAction()
        if indent:
            self.indent(line)
        else:
            self.unindent(line)
        self.endUndoAction()
        if indent:
            self.setCursorPosition(line, index + self.indentationWidth())
        else:
            self.setCursorPosition(line, index - self.indentationWidth())

    def __indentSelection(self, indent = True):
        """
        Private method to indent or unindent the current selection.

        @param indent flag indicating an indent operation (boolean)
                <br />If the flag is true, an indent operation is performed.
                Otherwise the current line is unindented.
        """
        if not self.hasSelectedText():
            return

        # get the selection
        lineFrom, indexFrom, lineTo, indexTo = self.getSelection()

        if indexTo == 0:
            endLine = lineTo - 1
        else:
            endLine = lineTo

        self.beginUndoAction()
        # iterate over the lines
        for line in range(lineFrom, endLine + 1):
            if indent:
                self.indent(line)
            else:
                self.unindent(line)
        self.endUndoAction()
        if indent:
            if indexTo == 0:
                self.setSelection(lineFrom, indexFrom + self.indentationWidth(),
                                  lineTo, 0)
            else:
                self.setSelection(lineFrom, indexFrom + self.indentationWidth(),
                                  lineTo, indexTo + self.indentationWidth())
        else:
            indexStart = indexFrom - self.indentationWidth()
            if indexStart < 0:
                indexStart = 0
            indexEnd = indexTo - self.indentationWidth()
            if indexEnd < 0:
                indexEnd = 0
            self.setSelection(lineFrom, indexStart, lineTo, indexEnd)

    def indentLineOrSelection(self):
        """
        Public slot to indent the current line or current selection
        """
        if self.hasSelectedText():
            self.__indentSelection(True)
        else:
            self.__indentLine(True)

    def unindentLineOrSelection(self):
        """
        Public slot to unindent the current line or current selection.
        """
        if self.hasSelectedText():
            self.__indentSelection(False)
        else:
            self.__indentLine(False)

    def smartIndentLineOrSelection(self):
        """
        Public slot to indent current line smartly.
        """
        if self.hasSelectedText():
            if self.lexer_ and self.lexer_.hasSmartIndent():
                self.lexer_.smartIndentSelection(self)
            else:
                self.__indentSelection(True)
        else:
            if self.lexer_ and self.lexer_.hasSmartIndent():
                self.lexer_.smartIndentLine(self)
            else:
                self.__indentLine(True)
