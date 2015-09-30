#!/usr/bin/env python2

import os, sys, subprocess, signal
from PyQt4 import QtGui, QtCore
from gi.repository import Notify

dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

ICON = dir + "/../icon_glow.png"
LOGO = dir + "/../icon_plain.png"
VERSION = 'Perdyshot ' + open(dir + '/../.version', 'r').read()
URL = "https://github.com/Locercus/Perdyshot"

Notify.init("Perdyshot")

app = QtGui.QApplication(sys.argv)

# Create about dialog
class AboutDialog(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedSize(450, 230)
        self.setWindowTitle("About Perdyshot")

        image = QtGui.QLabel(self)
        image.setPixmap(QtGui.QPixmap(LOGO))
        image.move((450 - image.sizeHint().width()) / 2, 10)

        text = QtGui.QLabel(self)
        text.setText("<b>%s &copy; 2015 Jonatan Nordentoft. MIT License</b>" % VERSION)
        text.move((450 - text.sizeHint().width()) / 2, image.sizeHint().height() + 30)

        website = QtGui.QPushButton("Website", self)
        website.move((450 - website.sizeHint().width()) / 2, image.sizeHint().height() + 60)
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

        menu.addAction("Capture Active Window", self.onActiveWindowCapture)

        menu.addSeparator()

        menu.addAction("About", self.onAbout)
        menu.addAction("Quit", self.onQuit)

        self.setContextMenu(menu)

    def onQuit(self):
        sys.exit(0)

    def onAbout(self):
        aboutDialog.show()

    def onActiveWindowCapture(self):
        subprocess.call(["/usr/bin/env", "python2", dir + "/../cli/window.py", "--delay", "0"])
        notification = Notify.Notification.new("Screenshot saved", "", ICON)
        notification.show()


aboutDialog = AboutDialog()

iconWidget = QtGui.QWidget()
trayIcon = SystemTrayIcon(QtGui.QIcon(ICON), iconWidget)
trayIcon.show()

signal.signal(signal.SIGINT, signal.SIG_DFL)
app.exec_()
