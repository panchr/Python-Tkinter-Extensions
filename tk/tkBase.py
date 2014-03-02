# tk/tkBase.py
# Rushy Panchal
# v1.0

'''tkBase contains the base classes and methods found in tkExtra.py and ttkExtra.py.
This should not be imported directly. Instead, import tkExtra or ttkExtra, respectively.'''

try:
	from Tkinter import *
	import tkFont
except ImportError:
	from tkinter import *
	import tkinter.font as tkFont
try:
	from PIL import Image, ImageTk
	HAS_PIL = True
except ImportError:
	HAS_PIL = False
	
### Constants

root = Tk()
root.withdraw()
screenDim = (root.winfo_screenwidth(), root.winfo_screenheight())
SCREENDIM = {"width": screenDim[0], "w": screenDim[0], "height": screenDim[1], "h": screenDim[1]}
PACKING_WIDGETS = ("Tk", "Toplevel", "TFrame", "Labelframe", "TNotebook")
	
### Functions to be used in advanced GUI building
	
def getScreenDimensions():
	'''Returns dimensions of the screen, as (width, height)'''
	return SCREENDIM

def sys_exit(window = None):
	'''Exits the program'''
	if window:
		window.close()
	raise SystemExit

def close(window, shutdown = False):
	'''Closes the window'''
	if shutdown:
		sys_exit(window)
	else:
		window.close()
	
def doNothing():
	'''Standard cleanup function'''
	pass

def createLambda(funct, *variables):
	'''Creates a lambda function in the form of funct(variables)'''
	return lambda: funct(*variables)

def findAllWidgets(master, widgetsFound = None):
	'''Returns all of the widgets in a packing instance'''
	if not widgetsFound:
		widgetsFound = []
	subWidgets = master.winfo_children()
	for widget in subWidgets:
		widgetsFound.append(widget)
		if widget.winfo_class() in PACKING_WIDGETS:
			widgetsFound.extend(findAllWidgets(widget, widgetsFound))
	return list(set(widgetsFound))
	
def extractFromDict(dictionary, options):
	'''Extracts values from the dictionary, with default values
	Options should be formatted as:
		[
			(option1, defaultValue),
			option2 # no default provided, resorts to None
			]'''
	return_values = []
	for option in options:
		if isinstance(option, (list, tuple)):
			option_value = dictionary.get(option[0], option[1])
		else:
			option_value = dictionary.get(option)
		return_values.append(option_value)
	return return_values
	
def gridWidgets(widgets, **options):
	'''Grids the widgets. widgets should look like:
		[
		(widget1, widget2, widget3), # first row
		(widget4, widget5, widget6, ...), # second row
		(widget7, widget8), # third row, ends in an empty space
		widget9 # fourth row, has an automatically-adjusted columnspan, set to the length of the longest row (3)
		...
		]
	
	Supported options:
		padx, pady (for each individual widget)
		
	Note: Unexpected behavior if the widgets are not of the same parent'''
	
	padx, pady = extractFromDict(options, [("padx", 5), ("pady", 5)])
	try:
		max_row = max(len(row) for row in widgets if isinstance(row, (list, tuple)))
	except ValueError:
		max_row = 1
	for row_number, row in enumerate(widgets, 1):
		if isinstance(row, (list, tuple)):
			for column_number, widget in enumerate(row, 1):
				widget.grid(row = row_number, column = column_number, padx = padx, pady = pady)
		else:
			row.grid(row = row_number, column = 1, columnspan = max_row, padx = padx, pady = pady)
	
### Internal Base Classes used in multiple inheritance

class BaseWindow(object):
	'''Base class for multiple inheritance of other classes'''
	closed = False
	
	def center(self):
		'''Places the window in the center of the screen'''
		self.update()
		self.winWidth, self.winHeight = self.winfo_width(), self.winfo_height()
		winOffset = self.winfo_rootx() - self.winfo_x()
		self.w = self.winWidth + winOffset*2
		self.h = self.winHeight + (self.winfo_rooty() - self.winfo_y()) + winOffset
		self.x = (self.winfo_screenwidth() // 2) - (self.w // 2)
		self.y = (self.winfo_screenheight() // 2) - (self.h // 2)
		self.geometry('+{xPos}+{yPos}'.format(xPos = self.x, yPos = self.y))

	def resize(self):
		'''Allows the screen to be resized and moves the widgets to the center'''
		self.rowconfigure(0, weight = 1)
		self.columnconfigure(0, weight = 1)

	def fullscreen(self, showAll = False):
		'''Makes the window Fullscreen'''
		self.geometry("{}x{}".format(*screenDim))
		if not showAll: 
			self.overrideredirect(1)

	def getScreenDimensions(self):
		'''Returns window dimensions'''
		return self.winfo_width(), self.winfo_height()
		
	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets'''
		gridWidgets(*widgets, **options)
		
	def childWidgets(self):
		'''Finds all widgets in the main instance'''
		self.widgetsFound = findAllWidgets(self)
		return self.widgetsFound

	def delAllWidgets(self):
		'''Deletes all widgets'''
		for widget in self.childWidgets():
			widget.destroy()
		self.update()

	def close(self):
		'''Closes the window by quitting the mainloop and then destroying itself'''
		try:
			self.quit()
			self.destroy()
			self.closed = True
		except TclError:
			pass

	def configure(self, **options):
		self.options.update(options)
		self.config(**options)
		
class BaseCustomWindow(object):
	'''Base class that allows for multiple inheritance in Custom ttk Wrappers'''
	closed = False
	
	def mainloop(self):
		'''Shows the window'''
		try:
			self.shouldCenter
		except AttributeError:
			self.shouldCenter = True
		try:
			self.shouldResize
		except AttributeError:
			self.shouldResize = True
		if self.shouldCenter:
			self.center()
		if self.shouldResize:
			self.resize()
		self.master.lift()
		self.master.mainloop()

	def withdraw(self):
		'''Withdraws the window'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.withdraw()

	def iconify(self):
		'''Iconifies the window'''
		self.master.iconify()

	def deiconify(self):
		'''Deiconifies the window'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.deiconify()
		try:
			self.shouldCenter
		except AttributeError:
			self.shouldCenter = True
		if self.shouldCenter: 
			self.center()

	def destroy(self):
		'''Destroys the window'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.quit()
		try:
			self.master.destroy()
		except tk.TclError:
			pass

	def quit(self):
		'''Quits the mainloop'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.quit()
		self.withdraw()

	def close(self):
		'''Closes the window by quitting the mainloop and then destroying itself'''
		try:
			self.quit()
			self.destroy()
		except TclError:
			pass

	def resize(self):
		'''Resizes the master window'''
		self.master.resize()

	def center(self):
		'''Centers the window'''
		self.master.center()

	def update(self):
		'''Updates the master window'''
		self.master.update()

	def protocol(self, name = None, func = None):
		'''Calls wm_protocol and changes "name"s function to "func"'''
		self.master.protocol(name, func)

	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets'''
		gridWidgets(*widgets, **options)
		
	def childWidgets(self):
		'''Returns all widgets attached to this window'''
		return self.master.childWidgets()

	def delAllWidgets(self):
		'''Deletes all widgets'''
		for widget in self.childWidgets():
			widget.destroy()
		self.update()

	def configure(self, **options):
		'''Configures the window to a new set of options'''
		self.options.update(options)
		for widget in self.childWidgets():
			widget.destroy()
		if isinstance(self, MessageBox):
			self.__init__(self.master, **self.options)
		elif isinstance(self, (Calltip, Infobox)):
			self.__init__(self.widget, **self.options)
		elif isinstance(self, (Prompt, OptionsWindow)):
			options = self.options.copy()
			for name, widget in zip(['master', 'prompt'], [self.master, self.prompt]):
				if not name in options:
					options[name] = widget
					widget.destroy()
			self.__init__(*self.choices, **options)
		elif isinstance(self, InputWindow):
			options = self.options.copy()
			for name, widget in zip(['master', 'prompt'], [self.master, self.prompt]):
				if not name in options:
					options[name] = widget
					try:
						widget.destroy()
					except AttributeError:
						pass
			self.__init__(**options)
		else:
			self.__init__(self.master, **self.options)
			
class BaseCustomWidget(object):
	'''Base class for Custom Widgets'''
	
	def addCalltip(self, **options):
		'''Adds a calltip to the base'''
		self.calltip = Calltip(self, **options)
	
	def grid(self, *args, **kwargs):
		'''Grids the widget'''
		self.mainFrame.grid(*args, **kwargs)
		
	def pack(self, *args, **kwargs):
		'''Packs the widget'''
		self.mainFrame.grid(*args, **kwargs)
		
	def place(self, *args, **kwargs):
		'''Places the widget'''
		self.mainFrame.place(*args, **kwargs)
			
### Internal classes for disambiguation

class TkBase(Tk):
	'''Mock class for disambiguity'''
	pass

class ToplevelBase(Toplevel):
	'''Mock class for disambiguity'''
	pass

class FrameBase(Frame):
	'''Adds on to the Frame class'''
	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets'''
		gridWidgets(*widgets, **options)
	
	def childWidgets(self):
		'''Finds all widgets in the main instance'''
		self.widgetsFound = findAllWidgets(self)
		return self.widgetsFound
	
### Inherited classes that add on to existing Tkinter classes
	
class Tk(BaseWindow, TkBase):
	'''Inherited class that adds methods to tk.Tk'''
	def __init__(self, **options):
		self.options = options
		self.resizeWin, self.centerWin = options.get('resize'), options.get('center')
		for option in ('resize', 'center'):
			try:
				del options[option]
			except KeyError:
				pass
		TkBase.__init__(self, **options)
		if self.resizeWin:
			self.resize()
		if self.centerWin:
			self.center()

class Toplevel(BaseWindow, ToplevelBase):
	'''Inherited class that adds methods to tk.Toplevel'''
	def __init__(self, master = None, **options):
		self.options, self.master = options, master
		self.resizeWin, self.centerWin, self.inherit = options.get('resize'), options.get('center'), options.get('inherit', True)
		for option in ('resize', 'center', 'inherit'):
			try:
				del options[option]
			except KeyError:
				pass
		if master and self.inherit:
			root_options = master.keys()
			try: options.update({k:
				v for k, v in master.options.items() if ((k in root_options) and (k not in options.keys()))})
			except AttributeError:
				pass
		ToplevelBase.__init__(self, master, **options)
		if self.resizeWin:
			self.resize()
		if self.centerWin:
			self.center()

class Frame(FrameBase):
	'''Inherited class that adds methods to tk.Frame'''
	pass
		
if HAS_PIL:
	class TkImage:
		'''Creates a Tkinter-friendly image that supports most image formats'''
		def __init__(self, filePath = None):
			if isinstance(filePath, file):
				filePath = filePath.__name__
			self.filePath = filePath
			if isinstance(filePath, str):
				self.photo = Image.open(filePath)
				self.image  = ImageTk.PhotoImage(self.photo)
			else:
				raise TypeError('filePath was not str or file, or was not provided')
			self.width, self.height = self.getSize()

		def tkImage(self):
			'''Returns the image instance'''
			return self.image

		def change(self, filePath):
			'''Changes the image to a new image'''
			self.__init__(self.master, filePath)
			return self.tkImage()

		def getSize(self):
			'''Returns the size of the image'''
			return (self.image.width(), self.image.height())

		def getWidth(self):
			'''Returns the width of the image'''
			return self.width

		def getHeight(self):
			'''Returns the height of the image'''
			return self.height
			
### Additional Tkinter wrappers/extensions

class EventMenu(Menu):
	'''Creates a Menu on a widget based off of events
	Commands are in the format [{'label': label, 'command': command, 'type': type, 'accelerator': accelerator}, ...]
	For separators, simply use {'type': 'separator'}'''
	def __init__(self, widget, commands, **options):
		self.widget, self.master, self.options, self.commands = widget, widget.master, options, commands
		self.binding = self.options.get('binding')
		if self.binding: 
			del self.options['binding']
		else: 
			self.binding = "<Button-3>"
		if not "tearoff" in self.options.keys():
			self.options["tearoff"] = False
		Menu.__init__(self, self.widget, **self.options)
		self.var = StringVar(self, value = '')
		for d in self.commands:
			_type = d.get('type')
			if _type == 'separator':
				self.add_separator()
			elif _type == 'checkbutton':
				self.add_checkbutton(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
			elif _type == 'radiobutton':
				self.add_radiobutton(label = d.get("label"), command = d.get('command'), accelerator = d.get("accelerator", variable = self.var, value = d.get("label")))
			elif _type == 'command':
				self.add_command(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
		self.widget.bind(self.binding, lambda event: self.show(event))

	def show(self, event):
		'''Shows the window'''
		self.post(event.x_root, event.y_root)
		
class HyperlinkManager:
	'''Allows for Hyperlinks in a Text widget
	Supported options:
	underline, activeColor, inactiveColor, activatedColor'''
	def __init__(self, text, **options):
		self.text, self.options, self.clicked = text, options, []
		self.activeColor, self.inactiveColor, self.activatedColor = self.options.get('activeColor', 'red'), self.options.get('inactiveColor', 'blue'), self.options.get('activatedColor', 'purple')
		self.underline = self.options.get('underline', True)
		self.hyperFont = tkFont.Font(self.text, self.text.cget("font"))
		self.text.tag_config("hyper", font = self.hyperFont, foreground = self.inactiveColor, underline = self.underline)
		self.text.tag_config("hyper", font = self.hyperFont)
		self.text.tag_bind("hyper", "<Enter>", self._enter)
		self.text.tag_bind("hyper", "<Leave>", self._leave)
		self.text.tag_bind("hyper", "<Button-1>", self._click)
		self.reset()

	def reset(self):
		'''Resets all links'''
		self.links = {}

	def add(self, action):
		'''Adds a link to the Hyperlink'''
		tag = "hyper-%d" % len(self.links)
		self.links[tag] = action
		return "hyper", tag

	def _enter(self, event):
		'''Internal method'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.text.tag_config(current_tag, foreground = self.activeColor)
		self.text.config(cursor="hand2")

	def _leave(self, event):
		'''Internal method'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.text.tag_config(current_tag, foreground = self.activatedColor if (current_tag in self.clicked) else self.inactiveColor)
		self.text.config(cursor="")

	def _click(self, event):
		'''Internal method'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.clicked.append(current_tag)
		self.text.tag_config(current_tag, foreground = self.activatedColor)
		for tag in self.text.tag_names(CURRENT):
			if tag[:6] == "hyper-":
				self.links[tag]()
				return
				
class ScrolledText(Text):
	'''Creates a Text widget with a Scrollbar on the side'''
	def __init__(self, master = None, **options):
		self.frame = Frame(master)
		self.vbar = Scrollbar(self.frame)
		self.vbar.pack(side=RIGHT, fill=Y)
		options.update({'yscrollcommand': self.vbar.set})
		Text.__init__(self, self.frame, **options)
		self.pack(side=LEFT, fill=BOTH, expand=True)
		self.vbar['command'] = self.yview
		text_meths = vars(Text).keys()
		methods = vars(Pack).keys() + vars(Grid).keys() + vars(Place).keys()
		methods = set(methods).difference(text_meths)

		for m in methods:
			if m[0] != '_' and m != 'config' and m != 'configure':
				setattr(self, m, getattr(self.frame, m))

class VerticalLabel(Label):
	'''Creates a Vertical Label widget'''
	def __init__(self, master, *args, **kwargs):
		if 'wraplength' not in kwargs.keys():
			kwargs['wraplength'] = 1
		Label.__init__(self, master, *args, **kwargs)