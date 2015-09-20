Perdyshot
=========

Perdyshot is a command-line (for now) Python application for Elementary OS that takes perdy screenshots. Us Linux-folk like nice stuff, too. :penguin:

![Perdyshot Example Image](http://i.imgur.com/suygnfu.png)

At the current state of the project, Perdyshot is only capable of screenshotting entire windows, but support for area selections and more is planned. :whale:

To use Perdyshot, grab the latest release (or clone this repository for bleeding edge) and run `python perdyshot.py` or simply `./perdyshot.py` if you have execute permission to make use of shebang! Then select the window you want to capture and let it do its magic. The screenshot will be saved as `screenshot.png` by default.

For a list of options, use the `-h` command-line flag. Check out `perdyshot.conf`, too for even more options! :raised_hands:

# Examples
![](http://i.imgur.com/HhPFWtT.png)
![](http://i.imgur.com/FZzSqWh.png)

## TODO :thumbsup:
* Implement support for other selection types
* Improve corner rounding (proper anti-aliasing?)
* GUI
* Add support for disabling Elementary OS hacks to add support for other distros (the hacks are the only thing preventing it from working properly on Arch, fx)
* Add support for custom shadows
