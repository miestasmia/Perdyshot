Perdyshot
=========

Perdyshot is a command-line (for now) Python application for Linux that takes perdy screenshots. Us Linux-folk like nice stuff, too. :penguin:

![Perdyshot Example Image](http://i.imgur.com/suygnfu.png)

While Perdyshot will work for *any* Linux distro, it'll require some modification of the configuration file to look good on distros other than Elementary OS. That's not a very difficult task, though.

At the current state of the project, Perdyshot is only capable of screenshotting entire windows, but support for area selections and more is planned. :whale:

To use Perdyshot, grab the latest release (or clone this repository for bleeding edge) and run `python perdyshot.py` or simply `./perdyshot.py` if you have execute permission to make use of shebang! Then select the window you want to capture and let it do its magic. The screenshot will be saved as `screenshot.png` by default.

For a list of options, use the `-h` command-line flag. Check out `perdyshot.conf`, too for even more options! :raised_hands:

# Examples
![](http://i.imgur.com/HhPFWtT.png)
![](http://i.imgur.com/FZzSqWh.png)

## TODO :thumbsup:
* Implement support for other selection types
* GUI
* Add support for custom shadows
