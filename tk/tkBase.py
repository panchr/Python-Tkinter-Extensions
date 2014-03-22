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
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
screenDim = (SCREEN_WIDTH, SCREEN_HEIGHT) # maintained for backwards compatibility
SCREENDIM = {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
PACKING_WIDGETS = ("Tk", "Toplevel", "TFrame", "Labelframe", "TNotebook")
	
MENU = "menu"
SEPARATOR = "separator"
COMMAND = "command"
RADIOBUTTON = "radiobutton"
CHECKBUTTON = "checkbutton"

PY_KEYWORDS = ["assert", "break", "continue", "del", "elif", "else", "except", "exec", "eval", "finally", "for", "from",
	"global", "if" "import", "lambda", "pass", "print", "len", "max", "min", "type", "isinstance"]
PY_OPERATORS = ["as", "in", "is", "not", "and", "or"]
PY_OBJECTS = ["int", "long", "float", "bin", "hex", "str", "set", "tuple", "list", "dict", "object", "self", "True", "False", "file", "range", "xrange", "complex"]
	
### Functions to be used in advanced GUI building
	
def getScreenDimensions(type_value = dict):
	'''Returns dimensions of the screen
	
	getScreenDimensions() --> {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
	getScreenDimensions(list) --> [SCREEN_WIDTH, SCREEN_HEIGHT]'''
	return SCREENDIM if type_value == dict else screenDim

def sys_exit(window = None):
	'''Exits the program, by raising a SystemExit exception
	
	If the "window" argument is provided, the window will be closed
	
	returns None'''
	if window:
		window.close()
	raise SystemExit

def close(window, shutdown = False):
	'''Closes the window, using window.close()
	
	If the "shutdown" argument is provided and True, then a SystemExit exception will be raised
	
	returns None'''
	if shutdown:
		sys_exit(window)
	else:
		window.close()
	
def doNothing():
	'''Standard cleanup function
	
	Used by default for any window that uses a "cleanup" parameter (when the window is closed)
	
	returns None'''
	pass

def createLambda(funct, *variables):
	'''Creates a lambda function in the form of funct(variables)
	
	This is useful when many lambdas have to be created during iterations:
	
	for widget_name in list_of_widget_names:
		widget = Button(text = widget_name, command = lambda: some_function(widget_name))
		
	In this example, the lambda will only be created once, as the last widget_name. Then, this will be applied to every widget.
	To get around this, you can use a function to create the lambda:
	
	for widget_name in list_of_widget_names:
		widget = Button(text = widget_name, command = createLambda(some_function, widget_name))
		
	returns lambda: funct(*variables)'''
	return lambda: funct(*variables)

def findAllWidgets(master, widgetsFound = None):
	'''Returns all of the widgets in a packing instance
	
	This uses a recursive algorithm to find all of the widgets. If a widget is a packing instance,
	such as a Frame or Toplevel, then it searches through that parent's child widgets as well.
	
	findAllWidgets(window) --> list of widgets founds'''
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
			]
			
	returns a list of values, in the order the keys were provided
			
	extractFromDict({"x": 5}, [("x", 2), ("c")]) --> (5, None)
	extractFromDict({"x": 5}, [("c", 8), ("x")]) --> (8, 5)'''
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
		
	Note: Unexpected behavior if the widgets are not of the same parent
	
	returns None'''
	
	padx, pady = extractFromDict(options, [("padx", 5), ("pady", 5)])
	try:
		max_row = max(len(row) for row in widgets if isinstance(row, (list, tuple)))
	except ValueError:
		max_row = 1
	for row_number, row in enumerate(widgets, 1):
		if isinstance(row, (list, tuple)):
			for column_number, widget in enumerate(row, 1):
				if widget:
					widget.grid(row = row_number, column = column_number, padx = padx, pady = pady)
		else:
			row.grid(row = row_number, column = 1, columnspan = max_row, padx = padx, pady = pady)
	
### Internal Base Classes used in multiple inheritance

class BaseWindow(object):
	'''Base class for multiple inheritance of other classes
	
	Not meant to be inherited directly'''
	closed = False
	
	def center(self):
		'''Places the window in the center of the screen
		
		returns None'''
		self.update()
		self.winWidth, self.winHeight = self.winfo_width(), self.winfo_height()
		winOffset = self.winfo_rootx() - self.winfo_x()
		self.w = self.winWidth + winOffset*2
		self.h = self.winHeight + (self.winfo_rooty() - self.winfo_y()) + winOffset
		self.x = (self.winfo_screenwidth() // 2) - (self.w // 2)
		self.y = (self.winfo_screenheight() // 2) - (self.h // 2)
		self.geometry('+{xPos}+{yPos}'.format(xPos = self.x, yPos = self.y))

	def resize(self):
		'''Allows the screen to be resized and moves the widgets to the center
		
		returns None'''
		self.grid_rowconfigure(0, weight = 1)
		self.grid_columnconfigure(0, weight = 1)

	def fullscreen(self, showAll = True):
		'''Makes the window fullscreen
		if the parameter "showAll" is True (default), then the normal window manager settings will be kept
		Otherwise, the window will cover the normal window manager aspects as well.
		
		returns None'''
		self.geometry("{w}x{h}".format(w = SCREEN_WIDTH, h = SCREEN_HEIGHT))
		if not showAll: 
			self.overrideredirect(1)

	def getWindowDimensions(self):
		'''Returns window dimensions
		
		self.getWindowDimensions() --> [WIDTH, HEIGHT]'''
		return self.winfo_width(), self.winfo_height()
		
	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets
		
		Takes the options *widgets, which is a list of formatted widgets, and **options, which are other options
		To see the full documentation on the gridding, refer to the gridWidgets global function
		
		Same as calling gridWidgets(*widgets, **options)
		
		returns None'''
		gridWidgets(*widgets, **options)
		
	def childWidgets(self):
		'''Finds all widgets in the main instance, and returns them as a list
		
		Same as calling findAllWidgets(self)'''
		self.widgetsFound = findAllWidgets(self)
		return self.widgetsFound

	def delAllWidgets(self):
		'''Destroys all widgets associated with this parent
		
		returns None'''
		for widget in self.childWidgets():
			widget.destroy()
		self.update()

	def close(self):
		'''Closes the window by quitting the mainloop and then destroying itself
		It also sets self.closed to True
		returns None'''
		try:
			self.quit()
			self.destroy()
			self.closed = True
		except TclError:
			pass

	def configure(self, **options):
		'''Configures window options
		Preferable to calling self.config(**options), because this function keeps track of all the options
		
		returns None'''
		self.options.update(options)
		self.config(**options)
		
class BaseCustomWindow(object):
	'''Base class that allows for multiple inheritance in Custom Classes
	
	This is meant to be used directly. To create a window that extends this class, follow this pattern:
	
	class MyWindow(BaseCustomWindow):
		def __init__(self, master, other_args):
			self.master = master
			
	The self.master identifies the master widget for this window. All functions in this base class require self.master to be defined.'''
	closed = False
	
	def mainloop(self):
		'''Runs the mainloop on self.master
		
		If the "center" or "resize" options are set to True when the class was initialized,
		the window will be first centered and/or resized, respectively, and then the mainloop will be called.
		
		See Tkinter's documentation on the mainloop for further reference'''
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
		'''Withdraws the window with self.master.withdraw
		
		Similar to other window-removal methods, this function first calls self.cleanup
		
		See Tkinter's documentation on the withdraw method for further reference
		
		returns None'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.withdraw()

	def iconify(self):
		'''Iconifies the window
		
		See Tkinter's documentation on the iconify method for further reference
		
		returns None'''
		self.master.iconify()

	def deiconify(self):
		'''Deiconifies the window, using self.master.deiconify
		
		Like other window-removal methods, this called self.cleanup first.
		
		See Tkinter's documentation on the deiconify method for further reference
		
		returns None'''
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
		'''Destroys the window, with self.master.destroy
		
		The method first calls self.cleanup
		
		See Tkinter's documentation on the destroy method for further reference
		
		returns None'''
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
		'''Quits the mainloop, using self.master.quit
		
		Calls self.cleanup first. See Tkinter's documentation on the quit method for further reference
		
		returns None'''
		try:
			self.cleanup()
		except AttributeError:
			self.cleanup = doNothing
		self.master.quit()
		self.withdraw()

	def close(self):
		'''Closes the window by quitting the mainloop and then destroying itself
		
		See Tkinter's documentation on the quit and destroy methods for further reference
		
		returns None'''
		try:
			self.quit()
			self.destroy()
			self.closed = True
		except TclError:
			pass

	def resize(self):
		'''Resizes the master window, using self.master.resize
		
		Refer to the documentation on BaseWindow.resize for further information
		
		returns None'''
		self.master.resize()

	def center(self):
		'''Centers the window, using self.master.center
		
		Refer to the documentation on BaseWindow.center for further information
		
		returns None'''
		self.master.center()

	def update(self):
		'''Updates the master window, using self.master.update
		
		Refer to the documentation on BaseWindow.update for further information
		
		returns None'''
		self.master.update()

	def protocol(self, name = None, func = None):
		'''Calls wm_protocol and changes "name"s function to "func", using self.master.protocol
		
		Refer to the documentation on BaseWindow.protocol for further information
		
		returns None'''
		self.master.protocol(name, func)

	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets
		
		Uses the global gridWidgets function. See gridWidgets' documentation for further reference.
		
		returns None'''
		gridWidgets(*widgets, **options)
		
	def childWidgets(self):
		'''Returns all widgets attached to this window, using self.master.childWidgets
		
		See the BaseWindow.childWidgets method for further reference.
		
		returns a list of child widgets'''
		return self.master.childWidgets()

	def delAllWidgets(self):
		'''Deletes all widgets associated with this parent widget
		
		returns None'''
		for widget in self.childWidgets():
			widget.destroy()
		self.update()

	def configure(self, **options):
		'''Configures the window to a new set of options, using self.__init__
		
		It automatically handles some of the base classes that inherit from this class, including
		MessageBox, Calltip, Infobox, Prompt, OptionsWindow, and InputWindow
		
		For a list of supported options, view the class's __init__ method'''
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
	'''Base class for Custom Widgets
	
	Can be inherited directly. Follows this pattern:
	
	class MyWidget(BaseCustomWidget):
		def __init__(self, master):
			self.master = master
			self.mainFrame = Frame(self.master)
			
	The self.mainFrame attribute is mandatory --- it is used in all methods'''
	
	def addCalltip(self, **options):
		'''Adds a calltip to the base widget
		
		For further documentation, refer to the Calltip documentation
		
		returns None'''
		self.calltip = Calltip(self, **options)
	
	def grid(self, *args, **kwargs):
		'''Grids the widget, using self.mainFrame.grid
		
		To view a list of options, refer to the Tkinter grid method
		
		returns None'''
		self.mainFrame.grid(*args, **kwargs)
		
	def pack(self, *args, **kwargs):
		'''Packs the widget, using self.mainFrame.pack
		
		Refer to the Tkinter pack method to view a list of options
		
		returns None'''
		self.mainFrame.pack(*args, **kwargs)
		
	def place(self, *args, **kwargs):
		'''Places the widget, using self.mainFrame.place
		
		See the Tkinter place method to view a list of options
		
		returns None'''
		self.mainFrame.place(*args, **kwargs)
			
### Internal classes for disambiguation

class TkBase(Tk):
	'''Mock class for disambiguity --- do not extend directly'''
	pass

class ToplevelBase(Toplevel):
	'''Mock class for disambiguity --- do not extend directly'''
	pass
	
class FrameBase(Frame):
	'''Mock class for disambiguity --- do not extend directly'''
	pass
	
class EntryBase(Entry):
	'''Mock class for disambiguity --- do not extend directly'''
	pass
	
### Inherited classes that add on to existing Tkinter classes
	
class Tk(BaseWindow, TkBase):
	'''Inherited class that adds methods to tk.Tk
	
	This mainly included support for the center and resize methods'''
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
	'''Inherited class that adds methods to tk.Toplevel
	
	This includes support for the resize and center methods
	
	In addition, supplying the "inherit" option will use all options found in the parent'''
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
	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets
		
		Utilizes the global gridWidgets function, so see its documentation for further reference
		
		returns None'''
		gridWidgets(*widgets, **options)
	
	def childWidgets(self):
		'''Finds all widgets in the main parent
		
		Refer to the global findAllWidgets documentation for further reference
		
		returns a list of widgets found in this widget'''
		self.widgetsFound = findAllWidgets(self)
		return self.widgetsFound
		
	def resize(self):
		'''Allows the widget to be resized
		
		returns None'''
		self.grid_rowconfigure(0, weight = 1)
		self.grid_columnconfigure(0, weight = 1)
		
class Entry(EntryBase):
	'''Inherited class that adds methods to tk.Entry
	
	This allows for a "command" parameter, which associates a command with the Entry.
	This command is called every time a key is pressed in the Entry widget.'''
	def __init__(self, master = None, **options):
		self.master = master
		if 'command' in options.keys():
			self.entryCommand = options['command']
			del options['command']
		else:
			self.entryCommand = None
		EntryBase.__init__(self, master, **options)
		if self.entryCommand:
			self.bind("<Key>", lambda event: self.entryCommand())
		
if HAS_PIL:
	class TkImage:
		'''Creates a Tkinter-friendly image that supports most image formats
		
		The "filePath" parameter can either be a file or string, and will be handled accordingly
		
		This requires the PIL package'''
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
			'''Returns the image instance, self.image
			
			self.tkImage() --> self.image'''
			return self.image

		def change(self, filePath):
			'''Changes the image to a new image
			
			uses self.__init__, and returns the image instance (see self.tkImage)
			
			self.change(path) --> self.image'''
			self.__init__(self.master, filePath)
			return self.tkImage()

		def getSize(self):
			'''Returns the size of the image
			
			self.getSize --> (WIDTH, HEIGHT)'''
			return (self.image.width(), self.image.height())

		def getWidth(self):
			'''Returns the width of the image
			
			self.getWidth --> self.width'''
			return self.width

		def getHeight(self):
			'''Returns the height of the image
			
			self.getHeight --> self.height'''
			return self.height
			
### Additional Tkinter wrappers/extensions

class StdoutRedirector(object):
	'''Redirects sys.stdout to the widget
	
	Requires a "widget" parameter, which must be either a Label, Text, or ScrolledWidget instance
	This widget is where the Stdout is redirected to'''
	def __init__(self, widget):
		if not isinstance(widget, (Label, Text, ScrolledText)):
			raise TypeError("Can only use Label or Text widget to redirect sys.stdout")
		self.widget = widget
		text_meths = vars(Text).keys()
		methods = vars(Pack).keys() + vars(Grid).keys() + vars(Place).keys()
		methods = set(methods).difference(text_meths)

		for m in methods:
			if m[0] != '_' and m != 'config' and m != 'configure':
				setattr(self, m, getattr(self.widget, m))
		
	def write(self, text):
		'''Writes to the text widget, using self.widget.insert(END, text)
		
		returns None'''
		self.widget.insert(END, text)
		if hasattr(self.widget, 'see'):
			self.widget.see(END)
		self.widget.update_idletasks()

class EventMenu(Menu):
	'''Creates a Menu on a widget based off of events
	Commands are a list of dictionaries, in the format of {'label': label, 'command': command, 'type': type, 'accelerator': accelerator}
	
	Type of commands available:
		Seperator: {'type': 'separator'}
		Checkbutton: {'label': LABEL, 'command': COMMAND, 'accelerator': ACCELERATOR}
		Radiobutton: {'label': LABEL, 'command': COMMAND, 'accelerator': ACCELERATOR}
		Command: {'label': LABEL, 'command': COMMAND, 'accelerator': ACCELERATOR}
		
	Supported options;
		binding: what binding to use for opening the event menu (by default, <Button-3>, a right click)
		tearoff: whether or not to use tearoff for the menu (see the Tkinter Menu's reference on tearoff)'''
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
			if _type == SEPARATOR:
				self.add_separator()
			elif _type == CHECKBUTTON:
				self.add_checkbutton(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
			elif _type == RADIOBUTTON:
				self.add_radiobutton(label = d.get("label"), command = d.get('command'), accelerator = d.get("accelerator"), variable = self.var, value = d.get("label"))
			elif _type == COMMAND:
				self.add_command(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
			elif _type == MENU:
				self.add_cascade(label = d.get("label"), menu = d.get("menu"))
		self.widget.bind(self.binding, lambda event: self.show(event))

	def show(self, event):
		'''Shows the window
		
		Should not be called directly, but instead will be bound to the event'''
		self.post(event.x_root, event.y_root)
		
class HyperlinkManager:
	'''Support for Hyperlinks in a Text widget
	Supported options:
		underline - underlines the hyperlinks (defaults to True)
		inactiveColor - initial, normal color (defaults to blue)
		activeColor - color when cursor hovers on hyperlink (defaults to red)
		activatedColor - color when hyperlink has been clicked (defaults to purple)'''
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
		'''Resets all links
		
		returns None'''
		self.links = {}

	def add(self, action):
		'''Adds a link to the Hyperlink
		should not be called directly'''
		tag = "hyper-%d" % len(self.links)
		self.links[tag] = action
		return "hyper", tag

	def _enter(self, event):
		'''Internal method, for when the cursor enters the hyperlink'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.text.tag_config(current_tag, foreground = self.activeColor)
		self.text.config(cursor="hand2")

	def _leave(self, event):
		'''Internal method, for when the cursor leaves the hyperlink'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.text.tag_config(current_tag, foreground = self.activatedColor if (current_tag in self.clicked) else self.inactiveColor)
		self.text.config(cursor="")

	def _click(self, event):
		'''Internal method, for when the hyperlink is clicked'''
		current_tag = self.text.tag_names(CURRENT)[1]
		self.clicked.append(current_tag)
		self.text.tag_config(current_tag, foreground = self.activatedColor)
		for tag in self.text.tag_names(CURRENT):
			if tag[:6] == "hyper-":
				self.links[tag]()
				return
				
class ScrolledText(Text):
	'''Creates a Text widget with a Scrollbar on the side
	
	Supports standard Text options'''
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
	'''Creates a Vertical Label widget, by setting the wraplength to 1
	
	Supports all of the standard Label options'''
	def __init__(self, master, *args, **kwargs):
		if 'wraplength' not in kwargs.keys():
			kwargs['wraplength'] = 1
		Label.__init__(self, master, *args, **kwargs)
		
class CheckButton(Checkbutton):
	'''Checkbutton wrapper
	
	Supports standard Checkbutton arguments '''
	def __init__(self, master = None, **options):
		if 'variable' in options.keys():
			del options['variable']
		if 'default' in options.keys():
			default = options['default']
			del options['default']
		else:
			default = False
		self.buttonVariable = BooleanVar(master, default)
		Checkbutton.__init__(self, master, variable = self.buttonVariable, **options)
		
	def get(self):
		'''Gets the current checkbutton value, using self.buttonVariable.get'''
		return self.buttonVariable.get()
		
	def set(self, value):
		'''Sets the current checkbutton value, to either True or False
		
		if "value" is not a Boolean, it is converted to one'''
		self.buttonVariable.set(bool(value))
		
	def toggle(self):
		'''Toggles the checkbutton on/off
		
		If the current value is True, then it becomes False, and vice versa.'''
		self.buttonVariable.set(not self.buttonVariable.get())