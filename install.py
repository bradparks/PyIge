#!/usr/bin/python3
import sys
import os
import stat
import distutils.sysconfig
import shutil

def doDependancyChecks():
    """
    Perform some dependency checks.
    """
    print('Checking dependencies')

    # perform dependency checks
    if sys.version_info < (3, 1, 0):
        print('Sorry, you must have Python 3.1.0 or higher.')
        sys.exit(5)
    if sys.version_info > (3, 9, 9):
        print('Sorry, eric5 requires Python 3 for running.')
        sys.exit(5)
    print("Python Version: %d.%d.%d" % sys.version_info[:3])

    try:
        from PyQt4.QtCore import qVersion
    except ImportError as msg:
        print('Sorry, please install PyQt4.')
        print('Error: %s' % msg)
        sys.exit(1)
    print("Found PyQt")

    try:
        from PyQt4 import Qsci
    except ImportError as msg:
        print("Sorry, please install QScintilla2 and")
        print("it's PyQt4 wrapper.")
        print('Error: %s' % msg)
        sys.exit(1)
    print("Found QScintilla2")

    # check version of Qt
    qtMajor = int(qVersion().split('.')[0])
    qtMinor = int(qVersion().split('.')[1])
    if qtMajor < 4 or (qtMajor == 4 and qtMinor < 5):
        print('Sorry, you must have Qt version 4.5.0 or higher.')
        sys.exit(2)
    print("Qt Version: %s" % qVersion())

    #check version of PyQt
    from PyQt4.QtCore import PYQT_VERSION_STR
    pyqtVersion = PYQT_VERSION_STR
    # always assume, that snapshots are new enough
    if "snapshot" not in pyqtVersion:
        while pyqtVersion.count('.') < 2:
            pyqtVersion += '.0'
        (maj, min, pat) = pyqtVersion.split('.')
        maj = int(maj)
        min = int(min)
        pat = int(pat)
        if maj < 4 or (maj == 4 and min < 7):
            print('Sorry, you must have PyQt 4.7.0 or higher or' \
                  ' a recent snapshot release.')
            sys.exit(3)
    print("PyQt Version: ", pyqtVersion)

    #check version of QScintilla
    from PyQt4.Qsci import QSCINTILLA_VERSION_STR
    scintillaVersion = QSCINTILLA_VERSION_STR
    # always assume, that snapshots are new enough
    if "snapshot" not in scintillaVersion:
        while scintillaVersion.count('.') < 2:
            scintillaVersion += '.0'
        (maj, min, pat) = scintillaVersion.split('.')
        maj = int(maj)
        min = int(min)
        pat = int(pat)
        if maj < 2 or (maj == 2 and min < 4):
            print('Sorry, you must have QScintilla 2.4.0 or higher or' \
                  ' a recent snapshot release.')
            sys.exit(4)
    print("QScintilla Version: ", QSCINTILLA_VERSION_STR)
    print("All dependencies ok.")
    print()


def copyTree(src, dst, excludeDirs=[]):
    """
    Copy tree from one dir to another

    @param src name of the source directory
    @param dst name of the destination directory
    @param excludeDirs list of (sub)directories to exclude from copying
    """
    try:
        names = os.listdir(src)
    except OSError:
        return      # ignore missing directories
    #print(names)
    #print('\n\n\n')
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isfile(srcname):
            if not os.path.isdir(dst):
                os.makedirs(dst)
            shutil.copy2(srcname, dstname)
        else:
            if os.path.isdir(srcname) and not srcname in excludeDirs:
                copyTree(srcname, dstname)


def copyToFile(name, text):
    """
    Copy a string to a file.

    @param name the name of the file.
    @param text the contents to copy to the file.
    """
    f = open(name,"wt+", encoding = "utf-8")
    f.write(text)
    f.close()


def createExe():

    text_win = r"""import os
import sys
import subprocess
import distutils.sysconfig

python_lib = distutils.sysconfig.get_python_lib(True)
pyige_path = os.path.join(python_lib, 'PyIge')
os.chdir(pyige_path)
pyige_exe = os.path.join(pyige_path, 'PyIge.pyw')
subprocess.Popen((os.path.join(sys.exec_prefix, 'pythonw.exe '), pyige_exe))"""

    text_lin = r"""#!/usr/bin/env python3
import os
import subprocess
import distutils.sysconfig

python_lib = distutils.sysconfig.get_python_lib(True)
pyige_path = os.path.join(python_lib, 'PyIge')
os.chdir(pyige_path)
pyige_exe = os.path.join(pyige_path, 'PyIge.pyw')
os.system('/usr/bin/python3 ' + pyige_exe)"""


    #for windows
    if sys.platform.startswith("win"):
        copyToFile(os.path.join(sys.exec_prefix, 'StartPyIge.pyw'), text_win)
    else:
        copyToFile('/usr/bin/pyige', text_lin)
        os.chmod('/usr/bin/pyige', stat.S_IROTH | stat.S_IXOTH )




if __name__ == "__main__":

    doDependancyChecks()
    os.chdir('./PyIge')
    exec(open('compile.py', 'rt', encoding='utf8').read())
    print("Installing PyIge ...", end = '')
    copyTree('../PyIge',
             os.path.join(distutils.sysconfig.get_python_lib(True), 'PyIge'))
    createExe()
    print("   [DONE]\n")
    print(r"""Installation complete!

To start PyIge on Windows run "StartPyIge.pyw" scrypt from you Python directory.
To start PyIge on Linux use command "pyige"
""")
    if sys.platform.startswith("win"):
        input("Press enter to continue...\n")
    
