#!/usr/bin/env python2

import os, sys, subprocess
from PyQt4 import QtGui
from gi.repository import Notify

dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

ICON = dir + "/../icon_glow.png"

Notify.init("Perdyshot")


# Create tray icon
# http://stackoverflow.com/a/895721/1248084
class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent = None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        menu = QtGui.QMenu(parent)

        menu.addAction("Capture Active Window", self.onActiveWindowCapture)

        menu.addSeparator()

        menu.addAction("Quit", self.onQuit)

        self.setContextMenu(menu)

    def onQuit(self):
        sys.exit(0)

    def onActiveWindowCapture(self):
        subprocess.call(["/usr/bin/env", "python2", dir + "/../cli/window.py", "--delay", "0"])
        notification = Notify.Notification.new("Screenshot saved", "", ICON)
        notification.show()



app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()
trayIcon = SystemTrayIcon(QtGui.QIcon(ICON), w)
trayIcon.show()
sys.exit(app.exec_())