'''
Created on Jul 28, 2014

@author: kahere

A simple setup script to create an executable using PyQt4. This also
demonstrates the method for creating a Windows executable that does not have
an associated console.

PyQt4app.py is a very simple type of PyQt4 application

Run the build process by running the command 'python setup.py build'

If everything works well you should find a subdirectory in the build
subdirectory that contains the files needed to run the application

Modified from http://www.pythonschool.net/cxfreeze_win/
'''

import sys  
from cx_Freeze import setup, Executable

 

application_title = "Parametric_Price" #what you want to application to be called
main_python_file = "ParamMain.py" #the name of the python file you use to run the program



base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["atexit","re"]
includeFiles = "ParamBox.py"

setup(
        name = application_title,
        version = "0.1",
        description = "Parametric pricing tool using historical earthquake, hurricane datasets",
        options = {"build_exe" : {"includes" : includes , "include_files" : includeFiles }},
        executables = [Executable(main_python_file, base = base)])