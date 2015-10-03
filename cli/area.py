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

        self.view.setMouseTracking(True)
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

        self.leftPressed = False
        self.pressMode = None # 0: Dragging, 1: Creating
        self.selPos = (0, 0)
        self.selDims = (0, 0, 0, 0)
        self.curPos = (0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftPressed = True

            # If clicking inside the current selection
            if event.x() in xrange(self.selDims[0], self.selDims[0] + self.selDims[2]) and event.y() in xrange(self.selDims[1], self.selDims[1] + self.selDims[3]):
                self.pressMode = 0
            # Outside the current selection
            else:
                self.pressMode = 1

                self.selPos = (event.x(), event.y(), 0, 0)
                self.selDims = (0, 0, 0, 0)

                self.selection.setRect(self.selPos[0], self.selPos[1], 0, 0)
                self.coverLeft.setRect(0, 0, self.width(), self.height())
                self.coverRight.setRect(0, 0, 0, 0)
                self.coverTop.setRect(0, 0, 0, 0)
                self.coverBottom.setRect(0, 0, 0, 0)

        self.updateCursor()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftPressed = False
            self.pressMode = None

        self.updateCursor()

    def mouseMoveEvent(self, event):
        if self.leftPressed:
            tw, th = self.width(), self.height()
            x, y, w, h = self.selPos
            dx, dy, dw, dh = self.selDims
            mx, my = event.x(), event.y()
            mxo, myo = self.curPos

            # In the current selection
            if self.pressMode == 0:
                xDiff = mx - mxo
                yDiff = my - myo

                x += xDiff
                y += yDiff
                w -= xDiff - xDiff
                h -= yDiff - yDiff

                self.selPos = (x, y, w, h)

            # Outside the current selection
            elif self.pressMode == 1:
                w = event.x() - x
                h = event.y() - y

                self.selPos = (x, y, w, h)

            if w < 0:
                x, w = x + w, -w

            if h < 0:
                y, h = y + h, -h

            self.selDims = (x, y, w, h)

            self.selection.setRect(x, y, w, h)
            self.coverLeft.setRect(0, 0, x, th)
            self.coverRight.setRect(x + w, 0, tw, th)
            self.coverTop.setRect(x, 0, w, y)
            self.coverBottom.setRect(x, y + h, w, th - y - h)

        self.curPos = (event.x(), event.y())
        self.updateCursor()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit()

    # Set the cursor according to its position
    def updateCursor(self):
        x, y = self.curPos

        rx, ry, rw, rh = self.selDims
        rx2, ry2 = rx + rw, ry + rh

        # Inside the selection
        if x in xrange(rx, rx2) and y in xrange(ry, ry2):
            if self.leftPressed:
                self.setCursor(Qt.ClosedHandCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)
        # Outside the selection
        else:
            self.setCursor(Qt.CrossCursor)



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
