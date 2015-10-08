Perdyshot
=========

Perdyshot is a Linux application that takes perdy screenshots. Us Linux-folk like nice stuff, too. :penguin:

![Perdyshot Example Image](http://i.imgur.com/82OA2py.png)

While Perdyshot will work on *any* Linux distro, it'll require some modification of the configuration file to look good on distros other than Elementary OS. That's not a very difficult task, though. :fist:

Perdyshot can at the current state of the project capture the active window or a selection. :whale:

To use Perdyshot, grab the latest release (or clone this repository for bleeding edge) and run `./checkdependencies.py` to make sure you have everything you need. :star:

Then run `./gui/perdyshot.py`. That'll create a tray icon that opens a menu when you click it. :v:

If you want a bit more control, check out the `cli` directory. The scripts in there are what the GUI uses. For a list of options, use the `-h` command-line flag. :musical_note:

Make sure to check out `perdyshot.conf`, to see if there's anything you want to change! :raised_hands:

# Examples :sparkles:
![](http://i.imgur.com/ORmXCdS.png)
![](http://i.imgur.com/mCluahW.png)

# License :book:
Perdyshot is free software (as in freedom and free beer) released under the MIT license. See `LICENSE.md` for the full license. :statue_of_liberty:

# Thanks to :thumbsup:
* [Prof. Erik Ernst](http://www.daimi.au.dk/~eernst/) for helping me figure out alpha compositing and having a tonne of patience.
* [Tallerkenen](http://tallerknen.deviantart.com/gallery/) for making an awesome icon.

## TODO :calendar:
* Other selection types (ancestor window, monitor, screen)
* Actual GUI
* More premade configuration files and bitmaps for different themes/wms
    * Set up a guide so others can contribute with setups for their themes/wms
* Support for uploading (with support for custom destinations using an API configuration system)
* Support for built-in image manipulation
* Support for hotkeys to invoke a capture mode
