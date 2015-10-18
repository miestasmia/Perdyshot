#!/usr/bin/env python2

from configobj import ConfigObj
from validate import Validator

import subprocess, time, sys, os, signal, argparse, tempfile

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, os.path.pardir))

from lib import wireutils
wireutils.cprintconf.name = "Perdyshot"
wireutils.cprintconf.color= wireutils.bcolors.DARKCYAN

from gtk import gdk

# We use PIL for simple tasks and ImageMagick for computationally-heavy tasks
from PIL import Image, ImageOps

def main(argSource):
    cwd = os.getcwd()

    version = 'Perdyshot ' + open(os.path.join(dirname, os.path.pardir, '.version'), 'r').read()

    parser = argparse.ArgumentParser(description = 'Takes a perdy screenshot of the active window.')

    parser.add_argument('-b', '--background', help = 'overrides setting in perdyshot.conf', default = '')

    parser.add_argument('--delay', help = 'the delay in seconds before capturing the active window (default: 1)', default = 1, type = float)

    parser.add_argument('-f', '--file', help = 'overrides setting in perdyshot.conf', default = None)

    parser.add_argument('--round-top', help = "overrides setting in perdyshot.conf", default = None, action = 'store_true')
    parser.add_argument('--no-round-top', help = "overrides setting in perdyshot.conf", dest = 'round_top', action = 'store_false')

    parser.add_argument('--round-bottom', help = "overrides setting in perdyshot.conf", type = int, choices = [0, 1, 2], default = None)

    parser.add_argument('--shadow', help = "overrides setting in perdyshot.conf", default = None)

    parser.add_argument('--size-bugged', help = "overrides setting in perdyshot.conf", type = int, default = None, choices = [0, 1, 2])

    parser.add_argument('-v', '--version', action = 'version', version = version)

    args = vars(parser.parse_args(argSource))

    config = ConfigObj(os.path.join(dirname, os.path.pardir, 'perdyshot.conf'), encoding = 'UTF8', configspec = os.path.join(dirname, os.path.pardir, 'perdyshot.conf.spec'))
    validator = Validator()
    if not config.validate(validator):
        wireutils.cprint("Invalid configuration file", color = wireutils.bcolors.DARKRED)
        sys.exit(1)



    wireutils.cprint("Please select the window to be captured\n")
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

    # Get the active window
    window = root.get_active_window()

    if window == None:
        wireutils.cprint("Failed to capture window, exiting.", color = wireutils.bcolors.DARKRED)
        sys.exit(1)

    # And its geometry
    x, y = window.get_origin()
    x -= 1
    y -= 1
    width, height = window.get_size()

    # Fix something that may just be specific to my fucked up left monitor
    if x < 0:
        x = 0
        window.move(x, y)
        time.sleep(.5)

    # Get the position of the window decorations
    decoX, decoY = window.get_root_origin()
    decoY += 1

    # Check if the window has a custom titlebar
    hascustomtitlebar = (y + 2 == decoY)

    # Add the dimensions of the decorations to window dimensions
    width  += x - decoX + 1
    height += y - decoY - 1

    windowType = window.get_type_hint()

    # Get its WM_CLASS
    WM_CLASS = window.property_get('WM_CLASS')[2].split('\x00')[0]

    # Read the config file and figure out the settings
    settings = {}

    if config['Settings']['background'] == "False":
        settings['background'] = False
    else:
        settings['background'] = config['Settings']['background']

    settings['shadow'] = config['Settings']['shadowColour']

    settings['filename'] = config['Settings']['filename']

    if config['Settings']['cornerImage'] == '':
        settings['cornerImage'] = None
    else:
        settings['cornerImage'] = Image.open(os.path.join(dirname, config['Settings']['cornerImage']))

    if config['Settings']['cornerImageDM'] == '':
        settings['cornerImageDM'] = None
    else:
        settings['cornerImageDM'] = Image.open(os.path.join(dirname, config['Settings']['cornerImageDM']))

    if config['Settings']['borderImage'] == '':
        settings['borderImage'] = None
    else:
        settings['borderImage'] = Image.open(os.path.join(dirname, config['Settings']['borderImage']))

    if config['Settings']['borderImageDM'] == '':
        settings['borderImageDM'] = None
    else:
        settings['borderImageDM'] = Image.open(os.path.join(dirname, config['Settings']['borderImageDM']))


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

    # Add the border size
    width  += settings['borderImage'].size[0]
    height += settings['borderImage'].size[1]

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


    # This is an estimate by a long-shot, but it's usually about right
    # At least on Pantheon, the gtk.gdk.WINDOW_STATE_MAXIMIZED state isn't set, so we resort to this
    maximized = height + 31 >= monitor.height and bounds.y - monitor.y + bounds.height == monitor.height

    sizeBugged = args['size_bugged'] if args['size_bugged'] != None else settings['sizeBugged']
    if sizeBugged == 1 or (sizeBugged == 2 and not(windowType & gdk.WINDOW_TYPE_HINT_DIALOG)):
        if not maximized:
            if windowType & gdk.WINDOW_TYPE_HINT_DIALOG:
                image = image.crop((37, 27, width - 38, height - 48))
                width -= 38 + 37
                height -= 48 + 27
            else:
                image = image.crop((50, 38, width - 51, height - 62))
                width -= 51 + 50
                height -= 62 + 38

    # Fix borders
    pixels = image.load()

    roundTop = args['round_top'] if args['round_top'] != None else settings['roundTop']

    roundBottom = args['round_bottom'] if args['round_bottom'] != None else settings['roundBottom']
    roundBottom = (roundBottom == 1 or (roundBottom == 2 and (maximized or windowType & gdk.WINDOW_TYPE_HINT_DIALOG)))

    # Apply deletion maps
    cornerDeleteMapSize = (0, 0)
    if settings['cornerImageDM'] != None:
        cornerDeleteMap = settings['cornerImageDM'].load()
        cornerDeleteMapSize = settings['cornerImageDM'].size
        for deleteColumn in xrange(0, cornerDeleteMapSize[0]):
            for deleteRow in xrange(0, cornerDeleteMapSize[1]):
                if cornerDeleteMap[deleteColumn, deleteRow][3] > 0:
                    if roundTop:
                        # Top left
                        pixels[deleteColumn, deleteRow] = (0, 0, 0, 0)
                        # Top right
                        pixels[width - deleteColumn - 1, deleteRow] = (0, 0, 0, 0)
                    if roundBottom:
                        # Bottom left
                        pixels[deleteColumn, height - deleteRow - 1] = (0, 0, 0, 0)
                        # Bottom right
                        pixels[width - deleteColumn - 1, height - deleteRow - 1] = (0, 0, 0, 0)

        if settings['borderImageDM'] != None:
            borderDeleteMap = settings['borderImageDM'].load()
            borderDeleteMapSize = settings['borderImageDM'].size
            for imx in xrange(0, width, borderDeleteMapSize[0]):
                for deleteColumn in xrange(0, borderDeleteMapSize[0]):
                    for deleteRow in xrange(0, borderDeleteMapSize[1]):
                        if borderDeleteMap[deleteColumn, deleteRow][3] > 0:
                            # Top
                            if not (roundTop and imx in xrange(cornerDeleteMapSize[0] - 1, width - cornerDeleteMapSize[0] - 1)):
                                pixels[imx + deleteColumn, deleteRow] = (0, 0, 0, 0)
                            # Bottom
                            if not (roundBottom and imx in xrange(cornerDeleteMapSize[0] - 1, width - cornerDeleteMapSize[0] - 1)):
                                pixels[imx + deleteColumn, height - deleteRow - 1] = (0, 0, 0, 0)

            for imy in xrange(0, height, borderDeleteMapSize[1]):
                # TODO: Rotate the image
                for deleteColumn in xrange(0, borderDeleteMapSize[0]):
                    for deleteRow in xrange(0, borderDeleteMapSize[1]):
                        if borderDeleteMap[deleteColumn, deleteRow][3] > 0:
                            # Left
                            if not ((roundTop and imy < cornerDeleteMapSize[1] - 1) or (roundBottom and imy > height - cornerDeleteMapSize[1] - 1)):
                                pixels[deleteColumn, imy + deleteRow] = (0, 0, 0, 0)
                            # Right
                            if not ((roundTop and imy < cornerDeleteMapSize[1] - 1) or (roundBottom and imy > height - cornerDeleteMapSize[1] - 1)):
                                pixels[width - deleteColumn - 1, imy + deleteRow] = (0, 0, 0, 0)

    # Apply overlay images
    cornerImageSize = (0, 0)
    if settings['cornerImage'] != None:
        cornerImage = settings['cornerImage']
        cornerImageSize = cornerImage.size

        if roundTop:
            imageTopLeft = cornerImage.copy()
            image.paste(imageTopLeft, (0, 0), imageTopLeft)

            imageTopRight = ImageOps.mirror(cornerImage)
            image.paste(imageTopRight, (width - cornerImageSize[0], 0), imageTopRight)

        if roundBottom:
            imageBottomLeft = ImageOps.flip(cornerImage)
            image.paste(imageBottomLeft, (0, height - cornerImageSize[1]), imageBottomLeft)

            imageBottomRight = ImageOps.flip(ImageOps.mirror(cornerImage))
            image.paste(imageBottomRight, (width - cornerImageSize[0], height - cornerImageSize[1]), imageBottomRight)

    if settings['borderImage'] != None:
        borderImage = settings['borderImage']
        borderImageSize = borderImage.size

        for imx in xrange(1, width, borderImageSize[0]):
            # Top
            if not roundTop or imx in xrange(cornerImageSize[0], width - cornerImageSize[0]):
                borderImageCopy = borderImage.copy()
                image.paste(borderImageCopy, (imx, 0), borderImageCopy)

            # Bottom
            if not roundBottom or imx in xrange(cornerImageSize[0], width - cornerImageSize[0]):
                borderImageCopy = ImageOps.flip(borderImage)
                image.paste(borderImageCopy, (imx, height - 1), borderImageCopy)


        rangeStartY = 1
        if roundTop:
            rangeStartY = cornerImageSize[1] - 1

        rangeEndY = height - 1
        if roundBottom:
            rangeEndY = height - cornerImageSize[1]

        for imy in xrange(rangeStartY, rangeEndY, borderImageSize[0]):
            # Left
            borderImageCopy = borderImage.rotate(90)
            image.paste(borderImageCopy, (0, imy), borderImageCopy)

            # Right
            borderImageCopy = borderImage.rotate(270)
            image.paste(borderImageCopy, (width - 1, imy), borderImageCopy)



    # Save the image with PIL for modification with ImageMagick
    image.save(os.path.join(tempfile.gettempdir(), 'perdywindow.png'), 'png')

    # Apply a shadow
    shadowColour = args['shadow'] if args['shadow'] != None else settings['shadow']
    command  = "convert " + os.path.join(tempfile.gettempdir(), 'perdywindow.png') + " -bordercolor none -border 64x64 -repage +48+48 \( +clone -background \"" + shadowColour + "\" -shadow 100x24+0+32 \) +swap -background none -mosaic"

    # Change the background if necessary
    background = args['background'] if args['background'] != '' else settings['background']
    if background != '' and background != False:
        command += " -background \"" + background + "\" -alpha remove"

    # Apply our magick to our image and save it to a file
    filename = args['file'] if args['file'] != None else settings['filename']
    filename = time.strftime(filename)
    subprocess.check_output(command + " " + filename, shell = True)

    totalTime = time.time()
    print # An empty line.
    wireutils.cprint("Screenshot time: %.2f seconds" % (partialTime - startTime))
    wireutils.cprint("Post-processing time: %.2f seconds" % (totalTime - partialTime))
    wireutils.cprint("Total time: %.2f seconds" % (totalTime - startTime))
    print
    wireutils.cprint("Saved as {name}.", name = filename)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except (KeyboardInterrupt, EOFError):
        print

signal.signal(signal.SIGINT, signal.SIG_DFL)
