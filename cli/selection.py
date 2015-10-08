#!/usr/bin/env python2

from configobj import ConfigObj
from validate import Validator

import argparse, os, sys, signal, time, tempfile

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, os.path.pardir, "lib"))

from enum import Enum

import wireutils
wireutils.cprintconf.name = "Perdyshot"
wireutils.cprintconf.color= wireutils.bcolors.DARKCYAN

from gtk import gdk

from PyQt4 import QtGui, QtCore
Qt = QtCore.Qt

from PIL import Image


def main(argSource):
    cwd = os.getcwd()

    app = QtGui.QApplication(sys.argv)


    version = 'Perdyshot ' + open(os.path.join(dirname, os.path.pardir, '.version'), 'r').read()

    parser = argparse.ArgumentParser(description = 'Takes a perdy screenshot of an area selection.')

    parser.add_argument('-f', '--file', help = 'overrides setting in perdyshot.conf', default = None)

    parser.add_argument('-v', '--version', action = 'version', version = version)

    args = vars(parser.parse_args(argSource))

    config = ConfigObj(os.path.join(dirname, os.path.pardir, 'perdyshot.conf'), encoding = 'UTF8', configspec = os.path.join(dirname, os.path.pardir, 'perdyshot.conf.spec'))
    validator = Validator()
    if not config.validate(validator):
        wireutils.cprint("Invalid configuration file", color = wireutils.bcolors.DARKRED)
        sys.exit(1)


    settings = {}

    settings['filename'] = config['Settings']['filename']

    PressMode = Enum('PressMode', 'Dragging KeyDragging CreateResizeCenter Creating ResizeLeft ResizeTop ResizeRight ResizeBottom ResizeTopLeft ResizeTopRight ResizeBottomRight ResizeBottomLeft')


    # Create area screenshot selection window
    class AreaWindow(QtGui.QWidget):
        def __init__(self, width, height):
            QtGui.QWidget.__init__(self)

            self.setContentsMargins(-1, -1, -1, -1) # Hacky af but it works

            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

            self.setCursor(Qt.CrossCursor)

            self.scene = QtGui.QGraphicsScene()

            self.view = QtGui.QGraphicsView(self.scene)
            self.view.setFocusPolicy(Qt.NoFocus)
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

            self.background = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(os.path.join(tempfile.gettempdir(), 'perdyselection.png')))
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
            self.pressMode = None
            self.selPos =  (0, 0, 0, 0)
            self.selDims = (0, 0, 0, 0)
            self.curPos =  (0, 0)

        def mousePressEvent(self, event):
            x, y = event.x(), event.y()
            dx, dy, dw, dh = self.selDims

            button = event.button()

            if button == Qt.LeftButton:
                self.leftPressed = True

                self.pressMode = self.getPositionPressMode(x, y)

                if self.pressMode == PressMode.Creating:
                    self.selPos = (x, y, 0, 0)
                    self.selDims = (0, 0, 0, 0)

                    self.selection.setRect(x, y, 0, 0)
                    self.coverLeft.setRect(0, 0, self.width(), self.height())
                    self.coverRight.setRect(0, 0, 0, 0)
                    self.coverTop.setRect(0, 0, 0, 0)
                    self.coverBottom.setRect(0, 0, 0, 0)

            elif button == Qt.RightButton:
                self.pressMode = None

                self.selPos = (0, 0, 0, 0)
                self.selDims = (0, 0, 0, 0)

                self.selection.setRect(0, 0, 0, 0)
                self.coverLeft.setRect(0, 0, self.width(), self.height())
                self.coverRight.setRect(0, 0, 0, 0)
                self.coverTop.setRect(0, 0, 0, 0)
                self.coverBottom.setRect(0, 0, 0, 0)

            self.updateCursor()

        def mouseReleaseEvent(self, event):
            if event.button() == Qt.LeftButton:
                self.leftPressed = False
                self.pressMode = None

                # Fix mirrored selections
                self.selPos = self.selDims

            self.updateCursor()

        def mouseMoveEvent(self, event):
            if self.leftPressed:
                tw, th = self.width(), self.height()
                x, y, w, h = self.selPos
                dx, dy, dw, dh = self.selDims
                mx, my = event.x(), event.y()
                mxo, myo = self.curPos
                xDiff = mx - mxo
                yDiff = my - myo

                if self.pressMode in [PressMode.Dragging, PressMode.KeyDragging]:
                    x += xDiff
                    y += yDiff

                elif self.pressMode == PressMode.CreateResizeCenter:
                    x -= xDiff
                    y -= yDiff
                    
                    w += xDiff * 2
                    h += yDiff * 2

                elif self.pressMode == PressMode.Creating:
                    w = event.x() - x
                    h = event.y() - y

                elif self.pressMode == PressMode.ResizeLeft:
                    x += xDiff
                    w -= xDiff

                elif self.pressMode == PressMode.ResizeTop:
                    y += yDiff
                    h -= yDiff

                elif self.pressMode == PressMode.ResizeRight:
                    w += xDiff

                elif self.pressMode == PressMode.ResizeBottom:
                    h += yDiff

                elif self.pressMode == PressMode.ResizeTopLeft:
                    x += xDiff
                    y += yDiff
                    w -= xDiff
                    h -= yDiff

                elif self.pressMode == PressMode.ResizeTopRight:
                    w += xDiff
                    y += yDiff
                    h -= yDiff

                elif self.pressMode == PressMode.ResizeBottomRight:
                    w += xDiff
                    h += yDiff

                elif self.pressMode == PressMode.ResizeBottomLeft:
                    x += xDiff
                    w -= xDiff
                    h += yDiff




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
            key = event.key()

            tw, th = self.width(), self.height()
            x, y, w, h = self.selPos
            dx, dy, dw, dh = self.selDims

            if key == Qt.Key_Escape:
                if __name__ == '__main__':
                    sys.exit()
                else:
                    self.hide()

            elif key in [Qt.Key_Enter, Qt.Key_Return]:
                self.capture(dx, dy, dw, dh)

            elif key == Qt.Key_Space:
                if self.pressMode == PressMode.Creating:
                    self.pressMode = PressMode.KeyDragging

            elif key == Qt.Key_Alt:
                if self.pressMode == PressMode.Creating:
                    self.pressMode = PressMode.CreateResizeCenter

            elif key in [Qt.Key_Left, Qt.Key_Up, Qt.Key_Right, Qt.Key_Down]:
                if self.pressMode is None:
                    diffx = 0
                    diffy = 0

                    if key == Qt.Key_Left:
                        diffx = -1

                    elif key == Qt.Key_Up:
                        diffy = -1

                    elif key == Qt.Key_Right:
                        diffx = 1

                    elif key == Qt.Key_Down:
                        diffy = 1


                    if event.modifiers() & Qt.ShiftModifier:
                        diffx *= 4
                        diffy *= 4


                    x  += diffx
                    dx += diffx

                    y  += diffy
                    dy += diffy

                    self.selPos = (x, y, w, h)
                    self.selDims = (dx, dy, dw, dh)

                    self.selection.setRect(dx, dy, dw, dh)
                    self.coverLeft.setRect(0, 0, x, th)
                    self.coverRight.setRect(x + w, 0, tw, th)
                    self.coverTop.setRect(x, 0, w, y)
                    self.coverBottom.setRect(x, y + h, w, th - y - h)

            self.updateCursor()


        def keyReleaseEvent(self, event):
            key = event.key()

            if key == Qt.Key_Space:
                if self.pressMode == PressMode.KeyDragging:
                    self.pressMode = PressMode.Creating

            elif key == Qt.Key_Alt:
                if self.pressMode == PressMode.CreateResizeCenter:
                    self.pressMode = PressMode.Creating


        def getPositionPressMode(self, x, y):
            dx, dy, dw, dh = self.selDims

            if x in xrange(dx + 8, dx + dw - 8) and y in xrange(dy + 8, dy + dh - 8):
                return PressMode.Dragging

            elif x in xrange(dx - 8, dx + 8) and y in xrange(dy + 8, dy + dh - 8):
                return PressMode.ResizeLeft

            elif x in xrange(dx + 8, dx + dw - 8) and y in xrange(dy - 8, dy + 8):
                return PressMode.ResizeTop

            elif x in xrange(dx + dw - 8, dx + dw + 8) and y in xrange(dy + 8, dy + dh - 8):
                return PressMode.ResizeRight

            elif x in xrange(dx + 8, dx + dw - 8) and y in xrange(dy + dh - 8, dy + dh + 8):
                return PressMode.ResizeBottom

            elif x in xrange(dx - 8, dx + 8) and y in xrange(dy - 8, dy + 8):
                return PressMode.ResizeTopLeft

            elif x in xrange(dx + dw - 8, dx + dw + 8) and y in xrange(dy - 8, dy + 8):
                return PressMode.ResizeTopRight

            elif x in xrange(dx + dw - 8, dx + dw + 8) and y in xrange(dy + dh - 8, dy + dh + 8):
                return PressMode.ResizeBottomRight

            elif x in xrange(dx - 8, dx + 8) and y in xrange(dy + dh - 8, dy + dh + 8):
                return PressMode.ResizeBottomLeft

            else:
                return PressMode.Creating


        # Set the cursor according to its position
        def updateCursor(self):
            x, y = self.curPos

            rx, ry, rw, rh = self.selDims
            rx2, ry2 = rx + rw, ry + rh

            mode = self.getPositionPressMode(x, y)

            if self.pressMode == PressMode.KeyDragging:
                self.setCursor(Qt.ClosedHandCursor)

            elif self.pressMode == PressMode.CreateResizeCenter:
                self.setCursor(Qt.SizeAllCursor)

            elif self.pressMode == PressMode.Creating or mode == PressMode.Creating:
                self.setCursor(Qt.CrossCursor)

            elif mode == PressMode.Dragging:
                if self.leftPressed:
                    self.setCursor(Qt.ClosedHandCursor)
                else:
                    self.setCursor(Qt.OpenHandCursor)

            elif mode in [PressMode.ResizeLeft, PressMode.ResizeRight]:
                self.setCursor(Qt.SizeHorCursor)

            elif mode in [PressMode.ResizeTop, PressMode.ResizeBottom]:
                self.setCursor(Qt.SizeVerCursor)

            elif mode in [PressMode.ResizeBottomLeft, PressMode.ResizeTopRight]:
                self.setCursor(Qt.SizeBDiagCursor)

            elif mode in [PressMode.ResizeTopLeft, PressMode.ResizeBottomRight]:
                self.setCursor(Qt.SizeFDiagCursor)


        # Captures the screenshot
        def capture(self, x, y, w, h):
            self.hide()

            filename = args['file'] if args['file'] != None else settings['filename']
            filename = time.strftime(filename)

            image = Image.open(os.path.join(tempfile.gettempdir(), 'perdyselection.png'))
            image = image.crop((x, y, x + w, y + h))
            image.save(filename, 'png')

            if __name__ == '__main__':
                sys.exit()




    areaWindow = None

    def activate():
        screen = gdk.screen_get_default()

        screenWidth  = screen.get_width()
        screenHeight = screen.get_height()

        pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, screenWidth, screenHeight)
        screenshot = gdk.Pixbuf.get_from_drawable(pixbuf, gdk.get_default_root_window(), gdk.colormap_get_system(), 0, 0, 0, 0, screenWidth, screenHeight)
        screenshot.save(os.path.join(tempfile.gettempdir(), 'perdyselection.png'), 'png')

        areaWindow = AreaWindow(screenWidth, screenHeight)
        areaWindow.move(0, 0)
        areaWindow.setFixedSize(screenWidth, screenHeight)
        areaWindow.show()

    if __name__ == '__main__':
        activate()

    app.exec_()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except (KeyboardInterrupt, EOFError):
        print

signal.signal(signal.SIGINT, signal.SIG_DFL)
