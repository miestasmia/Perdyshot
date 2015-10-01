#!/usr/bin/env python2

import imp, os, sys, subprocess

from distutils import spawn

def readBool(text):
    reply = raw_input(text + ' (y/n): ')

    if reply == 'y':
        return True
    elif reply == 'n':
        return False
    else:
        print "Invalid option. Please answer y or n for yes or no."

    return readBool(text)

def hasModule(name):
    try:
        imp.find_module(name)
        return True
    except ImportError:
        return False

def checkModule(name):
    installed = hasModule(name)
    print "Module %s installed: %s" % (name, installed)

    return installed

def moduleNeedsInstalling(name):
    installed = checkModule(name)

    if installed:
        return False
    elif ROOT:
        return readBool("Do you wish to install it now?")

def manualInstallNotify(name, tutorial):
    if not readBool("We can't automatically install %s for you. Please refer to %s to install it manually. Do you wish to continue now?" % (name, tutorial)):
        sys.exit()

def checkApplication(name, friendlyName, tutorial):
    installed = spawn.find_executable(name) != None
    print "Executable %s (%s) found: %s " % (name, friendlyName, installed)

    if not installed:
        manualInstallNotify(friendlyName, tutorial)






print "Perdyshot dependency checker"
print "============================\n"

ROOT = os.geteuid() == 0

if not ROOT:
    if not readBool("You're not root. Installing missing packages will not be supported. Do you wish to continue?"):
        sys.exit()

print "\nChecking module dependencies for Perdyshot ...\n"



if moduleNeedsInstalling("argparse"):
    subprocess.call(["pip2", "install", "-U", "argparse"])

if moduleNeedsInstalling("configobj"):
    subprocess.call(["pip2", "install", "-U", "configobj"])

if not checkModule("gi"):
    manualInstallNotify("gi", "http://python-gtk-3-tutorial.readthedocs.org/en/latest/install.html")

if moduleNeedsInstalling("gtk"):
    subprocess.call(["pip2", "install", "-U", "PyGTK"])

if moduleNeedsInstalling("PIL"):
    subprocess.call(["pip2", "install", "-U", "Pillow"])

if not checkModule("PyQt4"):
    manualInstallNotify("PyQt4", "http://pyqt.sourceforge.net/Docs/PyQt4/installation.html")

if moduleNeedsInstalling("validate"):
    subprocess.call(["pip2", "install", "-U", "validate"])



print "\nChecking application dependencies for Perdyshot ... \n"



checkApplication("convert", "ImageMagick", "http://www.imagemagick.org/script/binary-releases.php")

