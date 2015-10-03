#!/usr/bin/env python2

from configobj import ConfigObj
from validate import Validator

import os, sys, signal

from gtk import gdk

from PyQt4 import QtGui, QtCore

dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

app = QtGui.QApplication(sys.argv)

# Create area screenshot selection window
class AreaWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setContentsMargins(-1, -1, -1, -1) # Hacky af but it works

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.scene = QtGui.QGraphicsScene()

        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.mouseMoveEvent = self.mouseMoveEvent

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.background = QtGui.QGraphicsPixmapItem(QtGui.QPixmap('/tmp/perdyselection.png'))
        self.scene.addItem(self.background)

        self.selection = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 0, 0))
        self.scene.addItem(self.selection)

        self.pressed = False

    def mousePressEvent(self, event):
        self.pressPosition = (event.x(), event.y())

        self.selection.setRect(self.pressPosition[0], self.pressPosition[1], 0, 0)

        self.pressed = True

    def mouseReleaseEvent(self, event):
        self.pressed = False

    def mouseMoveEvent(self, event):
        if self.pressed: # Doesn't draw for some reason
            self.selection.setRect(self.pressPosition[0], self.pressPosition[1], event.pos().x() - self.pressPosition[0], event.pos().y() - self.pressPosition[1])



areaWindow = None

def activate():
    screen = gdk.screen_get_default()

    screenWidth  = screen.get_width()
    screenHeight = screen.get_height()

    pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, screenWidth, screenHeight)
    screenshot = gdk.Pixbuf.get_from_drawable(pixbuf, gdk.get_default_root_window(), gdk.colormap_get_system(), 0, 0, 0, 0, screenWidth, screenHeight)
    screenshot.save('/tmp/perdyselection.png', 'png')

    areaWindow = AreaWindow()
    areaWindow.move(0, 0)
    areaWindow.setFixedSize(screenWidth, screenHeight)
    areaWindow.show()

if __name__ == '__main__':
    activate()

signal.signal(signal.SIGINT, signal.SIG_DFL)
app.exec_()
