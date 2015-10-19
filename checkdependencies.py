#!/usr/bin/env python2

import imp, os, sys, subprocess

from distutils import spawn

try:
    import pip
except:
    pip = None

dirname = os.path.dirname(__file__)

from lib import wireutils
wireutils.cprintconf.name = "Perdyshot"
wireutils.cprintconf.color= wireutils.bcolors.DARKCYAN

def readBool(text):
    reply = wireutils.cinput(text + ' (y/n): ')

    if reply == 'y':
        return True
    elif reply == 'n':
        return False
    else:
        print
        wireutils.cprint("Invalid option. Please answer y or n for yes or no.\n", color = wireutils.bcolors.RED)

    return readBool(text)

def hasModule(name):
    try:
        imp.find_module(name)
        return True
    except ImportError:
        return False

def checkModule(name):
    installed = hasModule(name)
    if installed:
        if not args.get("quiet") and args.get("clean"):
            print wireutils.format("m {name}: y", name = name)
        elif not args.get("quiet"):
            wireutils.cprint("Module {name} installed.", name = name, color = wireutils.bcolors.GREEN)
    else:
        if args.get("clean"):
            print wireutils.format("m {name}: n", name = name)
        else:
            wireutils.cprint("Module {name} not installed.", name = name, color = wireutils.bcolors.RED)

    return installed

def installModule(name):
    if pip and not args.get("dry") and not args.get("clean"):
        pip.main(["install", "-U", name])

def moduleNeedsInstalling(name):
    installed = checkModule(name)
    if not args.get("dry"):
        if installed or args.get("clean"):
            return False
        elif ROOT:
            return readBool("Do you wish to install it now?")

def manualInstallNotify(name, tutorial):
    if not args.get("dry") and not args.get("clean"):
        if not readBool("%s can't be automatically installled.\nPlease refer to {blue}{line}%s{endc} to install it manually.\nDo you wish to continue?" % (name, tutorial)):
            sys.exit()

def checkApplication(name, friendlyName, tutorial):
    installed = spawn.find_executable(name) != None
    if installed:
        if not args.get("quiet") and args.get("clean"):
            print wireutils.format("a {name}: y", name = name)
        elif not args.get("quiet"):
            wireutils.cprint("Executable {name} ({readable}) found.", name = name, readable = friendlyName, color=wireutils.bcolors.GREEN)
    else:
        if args.get("clean"):
            print wireutils.format("a {name}: n", name = name)
        else:
            wireutils.cprint("Executable {name} ({readable}) not found.", name = name, readable = friendlyName, color=wireutils.bcolors.RED)

    if not installed and not args.get("dry"):
        manualInstallNotify(friendlyName, tutorial)





if __name__ == "__main__":
    try:
        try:
            import argparse
            parser = argparse.ArgumentParser(description = 'Checks the Perdyshot dependencies.', usage="%(prog)s [options]")
            parser.add_argument('-o', '--omit', help="Omit an update step", default="", choices=["module", "app", "m", "a"], dest="omit")
            parser.add_argument('--dry-run', help="Don't actually do anything", action = 'store_true', dest="dry")
            parser.add_argument('-q', '--quiet', help="Supress most output", action = 'store_true', dest="quiet")
            parser.add_argument('--porcelain', help="Machine-readable output (implies --dry-run)", action = 'store_true', dest="clean")

            args = vars(parser.parse_args())
        except Exception:
            wireutils.cprint("Argparse library missing. Will not be able to parse cli arguments.\n", color=wireutils.bcolors.DARKRED)
            args = {}

        if not args.get("quiet") and not args.get("clean"):
            wireutils.cprint("""Perdyshot Dependency Checker
                          {bold}============================{endc}
                                """,
                                strip = True)

        ROOT = os.geteuid() == 0

        if not args.get("dry") and not args.get("clean"):
            if not ROOT:
                if not readBool("You aren't root.\nInstalling missing packages will not be supported.\nDo you wish to continue?"):
                    sys.exit()
                print
            if not pip:
                if not readBool("{bold}pip{endc} isn't installed.\nInstalling missing packages will not be supported.\nDo you wish to continue?"):
                    sys.exit()
                print

        if args.get("omit") not in ["module", "m"]:
            if not args.get("quiet") and not args.get("clean"):
                wireutils.cprint("Checking module dependencies for Perdyshot ...\n{bold}----------------------------------------------{endc}\n")

            if moduleNeedsInstalling("argparse"):
                installModule("argparse")

            if moduleNeedsInstalling("configobj"):
                installModule("configobj")

            if not checkModule("gi"):
                manualInstallNotify("gi", "http://python-gtk-3-tutorial.readthedocs.org/en/latest/install.html")

            if moduleNeedsInstalling("gtk"):
                installModule("PyGTK")

            if moduleNeedsInstalling("PIL"):
                installModule("Pillow")

            if not checkModule("PyQt4"):
                manualInstallNotify("PyQt4", "http://pyqt.sourceforge.net/Docs/PyQt4/installation.html")

            if moduleNeedsInstalling("validate"):
                installModule("validate")

            if moduleNeedsInstalling("enum"):
                installModule("enum34")

            if moduleNeedsInstalling("datetime"):
                installModule("DateTime")


        if not args.get("omit") and not args.get("quiet") and not args.get("clean"): 
            print

        if args.get("omit") not in ["app", "a"]:
            if not args.get("quiet") and not args.get("clean"):
                wireutils.cprint("Checking application dependencies for Perdyshot ...\n{bold}---------------------------------------------------{endc}\n")

            checkApplication("convert", "ImageMagick", "http://www.imagemagick.org/script/binary-releases.php")
            checkApplication("xclip", "xclip", "https://github.com/milki/xclip/blob/master/INSTALL")



    except (KeyboardInterrupt, EOFError):
        print
