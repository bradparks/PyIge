#!/usr/bin/python3.1
import sys
import os

def compileUiFiles():
    """
    Compile the .ui files to Python sources.
    """

    from PyQt4.uic import compileUi

    def compileUiDir(dir, recurse=False, map=None, **compileUi_args):
        """compileUiDir(dir, recurse=False, map=None, **compileUi_args)

        Creates Python modules from Qt Designer .ui files in a directory or
        directory tree.

        dir is the name of the directory to scan for files whose name ends with
        '.ui'.  By default the generated Python module is created in the same
        directory ending with '.py'.
        recurse is set if any sub-directories should be scanned.  The default is
        False.
        map is an optional callable that is passed the name of the directory
        containing the '.ui' file and the name of the Python module that will be
        created.  The callable should return a tuple of the name of the directory
        in which the Python module will be created and the (possibly modified)
        name of the module.  The default is None.
        compileUi_args are any additional keyword arguments that are passed to
        the compileUi() function that is called to create each Python module.
        """

        import os

        # Compile a single .ui file.
        def compile_ui(ui_dir, ui_file):
            # Ignore if it doesn't seem to be a .ui file.
            if ui_file.endswith('.ui'):
                py_dir = ui_dir
                py_file = ui_file[:-3] + '.py'

                # Allow the caller to change the name of the .py file or generate
                # it in a different directory.
                if map is not None:
                    py_dir, py_file = map(py_dir, py_file)

                # Make sure the destination directory exists.
                try:
                    os.makedirs(py_dir)
                except:
                    pass

                ui_path = os.path.join(ui_dir, ui_file)
                py_path = os.path.join(py_dir, py_file)

                ui_file = open(ui_path, 'rt', encoding = 'utf-8')
                py_file = open(py_path, 'wt', encoding = 'utf-8')

                try:
                    compileUi(ui_file, py_file, **compileUi_args)
                finally:
                    ui_file.close()
                    py_file.close()

        if recurse:
            for root, _, files in os.walk(dir):
                for ui in files:
                    compile_ui(root, ui)
        else:
            for ui in os.listdir(dir):
                if os.path.isfile(os.path.join(dir, ui)):
                    compile_ui(dir, ui)
   

    def pyName(py_dir, py_file):
        """
        Local function to create the Python source file name for the compiled .ui file.
        
        @param py_dir suggested name of the directory (string)
        @param py_file suggested name for the compile source file (string)
        @return tuple of directory name (string) and source file name (string)
        """
        return py_dir, "Ui_%s" % py_file
    
    compileUiDir("ui", True, pyName)

def compileResources(dir):
    """
    Creates resources using pyrcc4
    """
    dir = os.path.realpath(dir)
    for res in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, res)):
            if res[-4:].lower() == ".qrc":
                file_in = os.path.join(dir, res)
                file_out =  os.path.join(os.path.split(dir)[0], res[:-4]) + "_rc.py"
                os.system("pyrcc4 -py3 " + file_in + " -o " + file_out )
    

def main(args):
    print("Compiling user interface files...", end = '')
    compileUiFiles()
    compileResources("res")
    print("   [DONE]\n")

    

if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except:
        print("""An internal error occured.  Please report all the output of the program,
including the following traceback, to developers.
""")
        raise