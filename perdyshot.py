#!/usr/bin/python2

from __future__ import division

from configobj import ConfigObj
from validate import Validator

from gtk import gdk

# We use PIL for simple tasks and ImageMagick for computationally-heavy tasks
from PIL import Image

import subprocess

import time

import sys

import os

import argparse

# Make sure ImageMagick is installed
subprocess.check_call('which convert > /dev/null', shell = True)

dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

parser = argparse.ArgumentParser(description = 'Take a perdy screenshot.')

parser.add_argument('-f', '--file', help = 'the name of the output file', default = 'screenshot.png')
parser.add_argument('--delay', help = 'the delay in seconds before capturing the active window', default = 1, type = float)

args = vars(parser.parse_args())

config = ConfigObj(dir + '/perdyshot.conf', encoding = 'UTF8', configspec = dir + '/perdyshot.conf.spec')
validator = Validator()
if not config.validate(validator):
    print "Invalid configuration file"
    sys.exit(1)



print "Please select the window to be captured\n"
time.sleep(args['delay'])

startTime = time.time()

# https://gist.github.com/mozbugbox/10cd35b2872628246140
def pixbuf2image(pix):
    """Convert gdkpixbuf to PIL image"""
    data = pix.get_pixels()
    w = pix.props.width
    h = pix.props.height
    stride = pix.props.rowstride
    mode = "RGB"
    if pix.props.has_alpha == True:
        mode = "RGBA"
    im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
    return im

# Get the root window
root = gdk.screen_get_default()

# And its size
screenSize = (root.get_width(), root.get_height())
print "Screen size: %sx%s" % screenSize

# Get the active window
window = root.get_active_window()

if window == None:
    print "Failed to capture window, exiting."
    sys.exit(1)

# And its geometry
x, y = window.get_origin()
width, height = window.get_size()

# Fix something that may just be specific to my fucked up left monitor
if x < 0:
    x = 0
    window.move(x, y)
    time.sleep(.5)

# Get the position of the window decorations
decoX, decoY = window.get_root_origin()

# Check if the window has a custom titlebar
hascustomtitlebar = (y == decoY)

print "Coordinates: (%s, %s)" % (x, y)
print "Window decoration coordinates: (%s, %s)" % (y, decoY)
print "Window decorations:", window.get_decorations()
print "Borders requested:", not not (window.get_decorations() & gdk.DECOR_BORDER)

# Add the dimensions of the decorations to window dimensions
width  += x - decoX
height += y - decoY

print "Size (estimate): %sx%s" % (width, height)

# To account for the one pixel border on some applications
width  += 1
height += 1

# Get pixbuf
pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, width, height)

# Screenshot the window (and its decorations)
screenshot = gdk.Pixbuf.get_from_drawable(pixbuf, gdk.get_default_root_window(), gdk.colormap_get_system(), decoX, decoY, 0, 0, width, height)

# Convert it to a PIL image
image = pixbuf2image(screenshot)

# Find out how long it took
partialTime = time.time()

# Get the geometry of the window's monitor
monitorid = root.get_monitor_at_window(window)
monitor = root.get_monitor_geometry(monitorid)

geometry = window.get_geometry()
bounds = window.get_frame_extents()

print "Monitor:", monitorid
print "Monitor geometry: (%s, %s) %sx%s" % (monitor.x, monitor.y, monitor.width, monitor.height)
print "Window geometry: (%s, %s) %sx%s %s bit" % geometry
print "Window bounding box: (%s, %s) %sx%s" % (bounds.x, bounds.y, bounds.width, bounds.height)


# This is an estimate by a long-shot, but it's usually about right
# At least on Pantheon, the gtk.gdk.WINDOW_STATE_MAXIMIZED state isn't set, so we resort to this
maximized = height + 31 >= monitor.height and bounds.y - monitor.y + bounds.height == monitor.height

print "Maximized:", maximized

# Get its WM_CLASS
WM_CLASS = window.property_get('WM_CLASS')[2].split('\x00')[0]

# Read the config file and figure out the settings
settings = {}
if WM_CLASS in config['Applications']:
    app = config['Applications'][WM_CLASS]

    settings['sizeBugged'] = app['sizeBugged']

    settings['roundTop'] = app['roundTop']
    if settings['roundTop'] == None:
        settings['roundTop'] = not hascustomtitlebar

    settings['roundBottom'] = app['roundBottom']
    if settings['roundBottom'] == None:
        if hascustomtitlebar:
            settings['roundBottom'] = 0
        else:
            settings['roundBottom'] = 2
else:
    settings['sizeBugged'] = False

    settings['roundTop'] = not hascustomtitlebar

    if hascustomtitlebar:
        settings['roundBottom'] = 0
    else:
        settings['roundBottom'] = 2


print "WM_CLASS:", WM_CLASS

print "Application-specific settings:"
print "\tsizeBugged:",  settings['sizeBugged']
print "\troundTop:",    settings['roundTop']
print "\troundBottom:", settings['roundBottom']


if settings['sizeBugged']:
    if not maximized:
        image = image.crop((50, 38, width - 51, height - 62))
        width -= 51 + 50
        height -= 62 + 38

# Maximized windows or those with a custom title bar shouldn't have an extra row and column of pixels
if maximized or hascustomtitlebar:
    image = image.crop((0, 0, width - 1, height - 1))
    width -= 1
    height -= 1

# Fix borders
pixels = image.load()

# Top
if settings['roundTop']:
    # Left
    pixels[0, 0] =     (0,   0,   0,   0)
    pixels[1, 0] =     (0,   0,   0,   0)
    pixels[2, 0] =     (0,   0,   0,   0)

    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[3, 0] = (227, 227, 227, 255)
        pixels[4, 0] = (136, 136, 136, 255)
        pixels[5, 0] = (116, 116, 116, 255)

    pixels[0, 1] =     (0,   0,   0,   0)
    pixels[1, 1] =     (0,   0,   0,   0)
    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[2, 1] = (133, 133, 133, 255)

    pixels[0, 2] =     (0,   0,   0,   0)
    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[1, 2] = (133, 133, 133, 255)

    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[0, 3] = (227, 227, 227, 255)

        pixels[0, 4] = (134, 134, 134, 255)

        pixels[0, 5] = (117, 117, 117, 255)

    # Right
    pixels[width -      1, 0] = (0,   0,   0,   0)
    pixels[width -      2, 0] = (0,   0,   0,   0)
    pixels[width -      3, 0] = (0,   0,   0,   0)
    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[width -  4, 0] = (227, 227, 227, 255)
        pixels[width -  5, 0] = (136, 136, 136, 255)
        pixels[width -  6, 0] = (116, 116, 116, 255)

    pixels[width -      1, 1] = (0,   0,   0,   0)
    pixels[width -      2, 1] = (0,   0,   0,   0)
    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[width -  3, 1] = (133, 133, 133, 255)

    pixels[width -      1, 2] = (0,   0,   0,   0)
    if not maximized and window.get_decorations() & gdk.DECOR_BORDER:
        pixels[width -  2, 2] = (133, 133, 133, 255)

        pixels[width -  1, 3] = (227, 227, 227, 255)

        pixels[width -  1, 4] = (134, 134, 134, 255)

        pixels[width -  1, 5] = (117, 117, 117, 255)

# Bottom
if settings['roundBottom'] == 1 or (settings['roundBottom'] == 2 and maximized):
    # Left
    pixels[0, height - 1] = (0, 0, 0, 0)
    pixels[1, height - 1] = (0, 0, 0, 0)
    pixels[2, height - 1] = (0, 0, 0, 0)

    pixels[0, height - 2] = (0, 0, 0, 0)
    pixels[1, height - 2] = (0, 0, 0, 0)

    pixels[0, height - 3] = (0, 0, 0, 0)

    # Right
    pixels[width - 1, height - 1] = (0, 0, 0, 0)
    pixels[width - 2, height - 1] = (0, 0, 0, 0)
    pixels[width - 3, height - 1] = (0, 0, 0, 0)

    pixels[width - 1, height - 2] = (0, 0, 0, 0)
    pixels[width - 2, height - 2] = (0, 0, 0, 0)

    pixels[width - 1, height - 3] = (0, 0, 0, 0)

print "Custom titlebar:", hascustomtitlebar

# Save the image with PIL for modification with ImageMagick
image.save('/tmp/perdyshot.png', 'png')

# Apply a shadow and save the image to the user-supplied path
subprocess.check_output("convert /tmp/perdyshot.png -bordercolor none -border 64x64 -repage +48+48 \( +clone -background \#949494 -shadow 100x24+0+32 \) +swap -background none -mosaic " + args['file'], shell = True)

totalTime = time.time()
print "\nScreenshot time: %.2f seconds" % (partialTime - startTime)
print "Post-processing time: %.2f seconds" % (totalTime - partialTime)
print "Total time: %.2f seconds" % (totalTime - startTime)
