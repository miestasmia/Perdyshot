#!/usr/bin/env python2

import imp, os, sys, subprocess

from distutils import spawn

import pip

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, "lib"))

import wireutils
wireutils.cprintconf.name = "Perdyshot"
wireutils.cprintconf.color= wireutils.bcolors.DARKCYAN

def readBool(text):
    reply = wireutils.cinput(text + ' (y/n): ')

    if reply == 'y':
        return True
    elif reply == 'n':
        return False
    else:
        wireutils.cprint("Invalid option. Please answer y or n for yes or no.")

    return readBool(text)

def hasModule(name):
    try:
        imp.find_module(name)
        return True
    except ImportError:
        return False

def checkModule(name):
    installed = hasModule(name)
    wireutils.cprint("Module {name} installed: {installed}", name = name, installed = installed)

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
    wireutils.cprint("Executable {name} ({readable}) found: {installed} ", name = name, readable = friendlyName, installed = installed)

    if not installed:
        manualInstallNotify(friendlyName, tutorial)





try:
    wireutils.cprint("""Perdyshot dependency checker
                        ============================\n""",
                        strip = True)

    ROOT = os.geteuid() == 0

    if not ROOT:
        if not readBool("You're not root. Installing missing packages will not be supported. Do you wish to continue?"):
            sys.exit()

    wireutils.cprint("Checking module dependencies for Perdyshot ...")



    if moduleNeedsInstalling("argparse"):
        pip.main(["install", "-U", "argparse"])

    if moduleNeedsInstalling("configobj"):
        pip.main(["install", "-U", "configobj"])

    if not checkModule("gi"):
        manualInstallNotify("gi", "http://python-gtk-3-tutorial.readthedocs.org/en/latest/install.html")

    if moduleNeedsInstalling("gtk"):
        pip.main(["install", "-U", "PyGTK"])

    if moduleNeedsInstalling("PIL"):
        pip.main(["install", "-U", "Pillow"])

    if not checkModule("PyQt4"):
        manualInstallNotify("PyQt4", "http://pyqt.sourceforge.net/Docs/PyQt4/installation.html")

    if moduleNeedsInstalling("validate"):
        pip.main(["install", "-U", "validate"])



    wireutils.cprint("Checking application dependencies for Perdyshot ... \n")



    checkApplication("convert", "ImageMagick", "http://www.imagemagick.org/script/binary-releases.php")
    checkApplication("xclip", "xclip", "https://github.com/milki/xclip/blob/master/INSTALL")



except (KeyboardInterrupt, EOFError):
    print
