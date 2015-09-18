Perdyshot
=========

Perdy is a command-line (for now) Python application for Elementary OS that takes perdy screenshots. Us Linux-folk like nice stuff, too.

![Perdyshot Example Image](http://i.imgur.com/suygnfu.png)

At the current state of the project, Perdyshot is only capable of screenshotting entire windows, but support for area selections and more is planned.

To use Perdyshot, grab the latest release (or clone this repository for bleeding edge) and run `python perdyshot.py`. Then select the window you want to capture and let it do its magic. It can take a while. The screenshot will be saved as `screenshot.png`.

# Examples
![](http://i.imgur.com/HhPFWtT.png)
![](http://i.imgur.com/FZzSqWh.png)

## TODO
* Implement support for other selection types
* Implement command-line options
* Look into optimising the post-processing (Pillow's gaussian blur is horrendously slow)
* Improve corner rounding (proper anti-aliasing?)
* Implement proper configuration system
* GUI