#!/usr/bin/env python2

from configobj import ConfigObj
from validate import Validator

import os, sys, signal

from gtk import gdk

from PyQt4 import QtGui, QtCore
Qt = QtCore.Qt

dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

app = QtGui.QApplication(sys.argv)

# Create area screenshot selection window
class AreaWindow(QtGui.QWidget):
    def __init__(self, width, height):
        QtGui.QWidget.__init__(self)

        self.setContentsMargins(-1, -1, -1, -1) # Hacky af but it works

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setCursor(Qt.CrossCursor)

        self.scene = QtGui.QGraphicsScene()

        self.view = QtGui.QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mousePressEvent = self.mousePressEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.background = QtGui.QGraphicsPixmapItem(QtGui.QPixmap('/tmp/perdyselection.png'))
        self.scene.addItem(self.background)

        coverBrush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        coverPen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))

        self.coverLeft = QtGui.QGraphicsRectItem(0, 0, width, height)
        self.coverLeft.setBrush(coverBrush)
        self.coverLeft.setPen(coverPen)
        self.scene.addItem(self.coverLeft)

        self.coverRight = QtGui.QGraphicsRectItem(0, 0, 0, 0)
        self.coverRight.setBrush(coverBrush)
        self.coverRight.setPen(coverPen)
        self.scene.addItem(self.coverRight)

        self.coverTop = QtGui.QGraphicsRectItem(0, 0, 0, 0)
        self.coverTop.setBrush(coverBrush)
        self.coverTop.setPen(coverPen)
        self.scene.addItem(self.coverTop)

        self.coverBottom = QtGui.QGraphicsRectItem(0, 0, 0, 0)
        self.coverBottom.setBrush(coverBrush)
        self.coverBottom.setPen(coverPen)
        self.scene.addItem(self.coverBottom)

        self.selection = QtGui.QGraphicsRectItem(0, 0, 0, 0)
        selectionPen = QtGui.QPen(QtGui.QColor(0xffffff))
        selectionPen.setStyle(Qt.DashLine)
        self.selection.setPen(selectionPen)
        self.scene.addItem(self.selection)

        self.pressed = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selPos = (event.x(), event.y())

            self.selection.setRect(self.selPos[0], self.selPos[1], 0, 0)
            self.coverLeft.setRect(0, 0, self.width(), self.height())
            self.coverRight.setRect(0, 0, 0, 0)
            self.coverTop.setRect(0, 0, 0, 0)
            self.coverBottom.setRect(0, 0, 0, 0)

            self.pressed = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed = False

    def mouseMoveEvent(self, event):
        if self.pressed:
            x = self.selPos[0]
            y = self.selPos[1]
            w = event.x() - x
            h = event.y() - y

            if w < 0:
                x, w = x + w, -w

            if h < 0:
                y, h = y + h, -h

            self.selection.setRect(x, y, w, h)
            self.coverLeft.setRect(0, 0, x, self.height())
            self.coverRight.setRect(x + w, 0, self.width(), self.height())
            self.coverTop.setRect(x, 0, w, y)
            self.coverBottom.setRect(x, y + h, w, self.height() - y - h)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit()



areaWindow = None

def activate():
    screen = gdk.screen_get_default()

    screenWidth  = screen.get_width()
    screenHeight = screen.get_height()

    pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, screenWidth, screenHeight)
    screenshot = gdk.Pixbuf.get_from_drawable(pixbuf, gdk.get_default_root_window(), gdk.colormap_get_system(), 0, 0, 0, 0, screenWidth, screenHeight)
    screenshot.save('/tmp/perdyselection.png', 'png')

    areaWindow = AreaWindow(screenWidth, screenHeight)
    areaWindow.move(0, 0)
    areaWindow.setFixedSize(screenWidth, screenHeight)
    areaWindow.show()

if __name__ == '__main__':
    activate()

signal.signal(signal.SIGINT, signal.SIG_DFL)
app.exec_()
