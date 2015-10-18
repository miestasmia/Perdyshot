#!/usr/bin/env python2

from configobj import ConfigObj
from validate import Validator

import os, sys, subprocess, signal, tempfile, shutil, pipes, time, locale

from datetime import datetime

from PyQt4 import QtGui, QtCore
try:
    from gi.repository import Notify
except:
    Notify = None

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dirname, os.path.pardir))

from lib import wireutils
wireutils.cprintconf.name = "Perdyshot"
wireutils.cprintconf.color= wireutils.bcolors.DARKCYAN

cwd = os.getcwd()

ICON = os.path.join(dirname, os.path.pardir, "icon_glow.png")
LOGO = os.path.join(dirname, os.path.pardir, "icon_plain.png")
VERSION = 'Perdyshot ' + open(os.path.join(dirname, os.path.pardir, '.version'), 'r').read()
URL = "https://github.com/Miestasmia/Perdyshot"

DATE = os.path.getmtime(os.path.join(dirname, os.path.pardir, ".version"))
DATE = datetime.fromtimestamp(DATE).strftime(locale.nl_langinfo(locale.D_T_FMT))

if Notify:
    Notify.init("Perdyshot")


config = ConfigObj(os.path.join(dirname, os.path.pardir, 'perdyshot.conf'), encoding = 'UTF8', configspec = os.path.join(dirname, os.path.pardir, 'perdyshot.conf.spec'))
validator = Validator()
if not config.validate(validator):
    wireutils.cprint("Invalid configuration file", color = wireutils.bcolors.DARKRED)
    sys.exit(1)

settings = {}

settings['modes'] = config['GUI']['CaptureModes']


app = QtGui.QApplication(sys.argv)

# Create about dialog
class AboutDialog(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedSize(450, 240)
        self.setWindowTitle("About Perdyshot")

        image = QtGui.QLabel(self)
        image.setPixmap(QtGui.QPixmap(LOGO))
        image.move((450 - image.sizeHint().width()) / 2, 10)

        text = QtGui.QLabel(self)
        text.setText("<center><b>%s &copy; 2015 Mia Nordentoft. MIT License</b><br/>Released on %s</center>" % (VERSION, DATE))
        text.move((450 - text.sizeHint().width()) / 2, image.sizeHint().height() + 30)

        website = QtGui.QPushButton("Website", self)
        website.move((450 - website.sizeHint().width()) / 2, image.sizeHint().height() + text.sizeHint().height() + 45)
        website.clicked.connect(self.openWebsite)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def openWebsite(self):
        subprocess.call(["xdg-open", URL])


# Create tray icon
# http://stackoverflow.com/a/895721/1248084
class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent = None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        menu = QtGui.QMenu(parent)
        self.menu = menu

        # Add the options
        for key in settings['modes']:
            action = menu.addAction(key)
            action.triggered.connect(
                lambda x, key = key: self.onCapture(key)
                )

        menu.addSeparator()

        menu.addAction("About", self.onAbout)
        menu.addAction("Quit", self.onQuit)

        self.setContextMenu(menu)

    def onQuit(self):
        sys.exit(0)

    def onAbout(self):
        aboutDialog.show()

    def onCapture(self, item):
        options = settings['modes'][item]

        if options['type'] == 'script':
            subprocess.call([ options['file'] ])

        elif options['type'] == 'simple':
            filename = os.path.join(tempfile.gettempdir(), 'perdygui.png')
            if not os.path.exists(filename):
                open(filename, "w").close()

            args = [
                '/usr/bin/env', 'python2', os.path.join(dirname, os.path.pardir, 'cli', options['mode'] + '.py'),

                '-f', filename
            ]

            if options['mode'] == 'window':
                args.extend(['--delay', '0'])

            # Capture the screenshot
            subprocess.call(args)

            # Okay the screenshot has been captures. What do we do now?
            if options['file'] != None:
                newFilename = time.strftime(options['file'])
                shutil.copyfile(filename, newFilename)
                filename = newFilename

            if options['program'] != None:
                subprocess.call(options['program'] % filename, shell = True)

            if options['copy']:
                subprocess.call('xclip -i -sel clip < ' + pipes.quote(filename), shell = True)

            if options['notification'] and Notify:
                notification = Notify.Notification.new(
                    options['notificationTitle'],
                    options['notificationDescription'],
                    options['notificationImage'] if options['notificationImage'] != None else ICON
                    )
                notification.show()


aboutDialog = AboutDialog()

iconWidget = QtGui.QWidget()
trayIcon = SystemTrayIcon(QtGui.QIcon(ICON), iconWidget)
trayIcon.show()

signal.signal(signal.SIGINT, signal.SIG_DFL)
app.exec_()
