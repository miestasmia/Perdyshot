"""
Wire Segal's utility library. 

Do whatever with it, I seriously couldn't care less.
"""
from __future__ import print_function
import os, json, time, sys, re

def format(string, **kwargs):
	"""
	Format strings with **kwargs.
	"""
	for arg in kwargs:
		regex = re.compile(r"\{" + arg + r"\}", re.IGNORECASE)
		string = regex.sub(str(kwargs[arg]), string)
	for color in bcolors.COLORS:
		regex = re.compile(r"\{" + color + r"\}", re.IGNORECASE)
		string = regex.sub(str(bcolors.COLORS[color]), string)
	return string

import traceback
def tbformat(e, text="Traceback (most recent call last):"):
	"""
	Format a traceback into a printable string.
	"""
	if not hasattr(e, "__traceback__"):
		if str(e):
			return str(type(e).__name__) + ": " + str(e)
		return str(type(e).__name__)
	trace = traceback.extract_tb(e.__traceback__) # Get the traceback object
	error = format("{text}\n", text=text) # Start out with `text`

	# Iterate through the traceback and add each iteration to the string
	for filename,lineno,function,message in trace:
		error += format("  File \"{name}\", line {num}, in {funcname}\n",
			name=filename, 
			num=lineno, 
			funcname=function)
		if message: 
			error += format("    {data}\n", data=message)

	# Add the type and message of the error
	error += str(type(e).__name__)
	if str(e): error += format(": {description}", description=e)

	return error 

class Config:
	"""
	A JSON read-only loader that will update automatically from `path`.
	"""
	def __init__(self, path):
		self.path = path
		self.lastmodtime = os.path.getctime(path) # get the last modified time of the target file
		self.data = json.load(open(path))
	def checkreload(self):
		if os.path.getctime(self.path) > self.lastmodtime: # check the last modified time of the target file
			self.reload()
	def reload(self):
		self.data = json.load(open(self.path))
		self.lastmodtime = os.path.getctime(self.path)
	# These are extensions of self.data's methods, except they run self.checkreload.
	def __getitem__(self, y):
		self.checkreload()
		return self.data[y]
	def __contains__(self, key):
		self.checkreload()
		return key in self.data
	def get(self, k, d=None):
		self.checkreload()
		return self.data.get(k, d)


def date_time_string(timestamp=None):
	"""
	Return the current date and time formatted for a message header.
	"""
	monthname = [None,
							 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
							 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	now = time.time()
	year, month, day, hh, mm, ss, x, y, z = time.localtime(now)

	# Add zeroes to keep the length of the timestamp constant
	hh = format("0{hours}", hours=hh) if hh < 10 else str(hh)
	mm = format("0{minutes}", minutes=mm) if mm < 10 else str(mm)
	ss = format("0{seconds}", seconds=ss) if ss < 10 else str(ss)
	day = format("0{day}", day=day) if day < 10 else str(day)
	
	s = format("{magenta}[{dd}/{mon}/{yyyy} {hh}:{mm}:{ss}]{endc} ", 
		dd = day, 
		mon = monthname[month], 
		yyyy = year, 
		hh = hh, 
		mm = mm, 
		ss = ss)
	return s

def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True



if supports_color():
	class bcolors: # All color codes
		"""
		A helper class containing colors (for pretty printing.)
		"""
		BLACK = '\033[30m'
		DARKRED = '\033[31m'
		DARKGREEN = '\033[32m'
		DARKYELLOW = '\033[33m'
		DARKBLUE = '\033[34m'
		PURPLE = '\033[35m'
		DARKCYAN = '\033[36m'
		GRAY = '\033[37m'
		DARKGRAY = '\033[90m'
		RED = '\033[91m'
		GREEN = '\033[92m'
		YELLOW = '\033[93m'
		BLUE = '\033[94m'
		MAGENTA = '\033[95m'
		CYAN = '\033[96m'
		WHITE = '\033[97m'
		ORANGE = '\033[38;5;202m'
		DARKPURPLE = '\033[38;5;53m'
		BROWN = '\033[38;5;94m'
		REMAKELINE = '\033[F\033[K'
		ENDC = '\033[0m'
		COLORS = {
			"black": BLACK,
			"darkred": DARKRED,
			"darkgreen": DARKGREEN,
			"darkyellow": DARKYELLOW,
			"darkblue": DARKBLUE,
			"purple": PURPLE,
			"darkcyan": DARKCYAN,
			"gray": GRAY,
			"darkgray": DARKGRAY,
			"red": RED,
			"green": GREEN,
			"yellow": YELLOW,
			"blue": BLUE,
			"magenta": MAGENTA,
			"cyan": CYAN,
			"white": WHITE,
			"orange": ORANGE,
			"darkpurple": DARKPURPLE,
			"brown": BROWN,
			"endc": ENDC
		}
else:
	class bcolors: # No color codes
		"""
		A helper class containing no colors, allowing systems that don't support ANSI to continue running without strange logs.
		"""
		BLACK = ''
		DARKRED = ''
		DARKGREEN = ''
		DARKYELLOW = ''
		DARKBLUE = ''
		PURPLE = ''
		DARKCYAN = ''
		GRAY = ''
		DARKGRAY = ''
		RED = ''
		GREEN = ''
		YELLOW = ''
		BLUE = ''
		MAGENTA = ''
		CYAN = ''
		WHITE = ''
		ORANGE = ''
		DARKPURPLE = ''
		BROWN = ''
		REMAKELINE = ''
		ENDC = ''
		COLORS = {
			"black": BLACK,
			"darkred": DARKRED,
			"darkgreen": DARKGREEN,
			"darkyellow": DARKYELLOW,
			"darkblue": DARKBLUE,
			"purple": PURPLE,
			"darkcyan": DARKCYAN,
			"gray": GRAY,
			"darkgray": DARKGRAY,
			"red": RED,
			"green": GREEN,
			"yellow": YELLOW,
			"blue": BLUE,
			"magenta": MAGENTA,
			"cyan": CYAN,
			"white": WHITE,
			"orange": ORANGE,
			"darkpurple": DARKPURPLE,
			"brown": BROWN,
			"endc": ENDC
		}

def rainbonify(string):
	if not supports_color(): return string
	else:
		colors = [bcolors.RED, bcolors.ORANGE, bcolors.YELLOW, bcolors.GREEN, 
				bcolors.BLUE, bcolors.PURPLE, bcolors.DARKPURPLE]
		nstring = ""
		cind = 0
		for i in string:
			nstring += colors[cind] + i
			cind += 1
			cind %= len(colors)
		return nstring + bcolors.ENDC

class colorconf:
	"""
	An object used to configure cprint and cinput.
	"""
	def __init__(self):
		self.color = bcolors.WHITE
		self.name = "Generic"
	def tag(self):
		"""
		Return the tag for pretty printing from the config.
		"""
		return format("{color}[{name}] {endc}",
			color=self.color, 
			name=self.name)
	def whitespace(self):
		"""
		Return the whitespace for non-printed lines.
		"""
		return " "*(26+len(self.name))

cprintconf = colorconf() # create the instance of colorconf used to configure cprint and cinput

lastprinted = None

def cprint(text, color="", strip=False, func=print, add_newline=False, colorconfig = None, **kwargs):
	"""
	Pretty print `text`, with `color` as its color, using `func`.
	If `strip`, then remove whitespace from both sides of each line.
	"""
	global lastprinted
	if not colorconfig:
		colorconfig = cprintconf
	if "whitespace" not in kwargs:
		kwargs["whitespace"] = colorconfig.whitespace()
	kwargs["color"] = color
	text = format(str(text), **kwargs)

	# Make sure not to print the same thing twice
	if text == lastprinted: return
	lastprinted = text

	# Split the text by lines
	if strip:
		prints = [i.strip().rstrip() for i in text.split("\n")]
	else:
		prints = text.split("\n")


	originstr = colorconfig.tag()
	func(format("{timestamp}{processtag}{color}{text}{endc}",
		timestamp = date_time_string(), 
		processtag = originstr, 
	  color = color, 
	  text = prints[0])) # Print the first line with a timestamp
	if add_newline: func("\n")

	for i in prints[1:]:
			func(format("{whitespace}{color}{text}{endc}",
				whitespace = colorconfig.whitespace(), 
			  color = color, 
			  text = i)) # Print all consecutive lines
			if add_newline: func("\n")

def cinput(text, color="", strip=False, func=raw_input, add_newline=False, colorconfig = None, **kwargs):
	"""
	Pretty print `text`, with `color` as its color. Take input using `func` on the last line.
	If `strip`, then remove whitespace from both sides of each line.
	"""
	if not colorconfig:
		colorconfig = cprintconf
	if "whitespace" not in kwargs:
		kwargs["whitespace"] = colorconfig.whitespace()
	kwargs["color"] = color
	text = format(str(text), **kwargs)
	# Split the text by lines
	if strip:
		prints = [i.strip().rstrip() for i in text.split("\n")]
		prints[-1] += " " # Add a spacing to the last line
	else:
		prints = text.split("\n")

	originstr = colorconfig.tag()
	# Print in order if there's more than one line
	if len(prints) > 1: 
		print(format("{timestamp}{processtag}{color}{text}",
			timestamp = date_time_string(), 
			processtag = originstr, 
		  color = color, 
		  text = prints[0]))
		if add_newline: func("\n")

		for i in prints[1:-1]:
			print(format("{whitespace}{color}{text}",
				whitespace = colorconfig.whitespace(), 
				color = color, 
				text = i))
			if add_newline: func("\n")

		return func(format("{whitespace}{color}{text}{endc}",
			whitespace = colorconfig.whitespace(), 
			color = color,
		  text = prints[-1]))
		if add_newline: func("\n")
	else:
		return func(format("{timestamp}{processtag}{color}{text}{endc}",
			timestamp = date_time_string(), 
			processtag = originstr, 
			color = color,
		  text = prints[0]))
		if add_newline: func("\n")
