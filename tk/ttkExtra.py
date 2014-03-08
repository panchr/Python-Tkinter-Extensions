# tk/ttkExtra.py
# Rushy Panchal
# v2.0

'''ttkExtra adds on to existing ttk classes and functions
By doing so, it is easier to accomplish common tasks, such as centering a Tk() or Toplevel() instance
It also creates custom, frequently used classes'''

### Change Log:
	# v1.0: Initial Release: Addition of methods onto existing Tkinter classes via inheritance
	# v1.1: Additonal classes added, each inheriting from a base class
		#1.11: Even more classes and bug fixes: window closing was closing every other widget
	# v2.0: Switch over to ttk for themed widgets

from tk.tkBase import *
try:
	# Python 2.x
	from ttk import *
	import tkFont
except ImportError:
	# Python 3.x
	from io import IOBase as file
	from tkinter.ttk import *
	import tkinter.font as tkFont
import webbrowser

### Constants

root = Tk()
root.withdraw()
screenDim = (root.winfo_screenwidth(), root.winfo_screenheight())
SCREENDIM = {"width": screenDim[0], "w": screenDim[0], "height": screenDim[1], "h": screenDim[1]}

### Functions to be used in advanced GUI-building

def configureStyle(style, label = None, **options):
	'''Configures the style with label to options, disregarding invalid options'''
	inherit = options.get('inherit', True)
	if inherit in options.keys():
		del options['inherit']
	_options = {k: v for k, v in options.items() if (k and v)}
	main_style = label.split('.')[-1]
	main_options = style.configure(main_style)
	if inherit:
		main_options.update(_options)
	style.configure(label, **main_options)

def createBaseStyles(master, font = "Helvetica 12"):
	'''Creates the base style instances and returns them as a dictionary'''
	label_style, button_style, radiobutton_style, entry_style, scale_style = Style(master), Style(master), Style(master), Style(master), Style(master)
	checkbutton_style, menubutton_style = Style(master), Style(master)
	all_styles = {"Label": label_style, "Button": button_style, "Entry": entry_style, "Radiobutton": radiobutton_style, "Checkbutton": checkbutton_style, "Scale": scale_style,
	"Menubutton": menubutton_style}
	label_style.configure("TLabel", font = font, foreground = "black", justify = CENTER)
	button_style.configure("TButton", font = font, foreground = "black", background = "white")
	button_style.configure("Quit.TButton", font = font, foreground = "red")
	radiobutton_style.configure("TRadiobutton", font = font, foreground = "black", indicatoron = True)
	checkbutton_style.configure("TCheckbutton", font = font, foreground = "black")
	entry_style.configure("TEntry", font = font, foreground = "black", background = "white", justify = CENTER)
	scale_style.configure("Hoizontal.TScale", font = font, foreground = "blue", background = "white", orient = HORIZONTAL)
	menubutton_style.configure("TMenubutton", font = font, foreground = "black")
	master.styles = all_styles
	return all_styles

### Base Styles

DEFAULT_FACE = "Calibri 10"
ALL_STYLES = createBaseStyles(root)
LABEL_STYLE, BUTTON_STYLE, RADIOBUTTON_STYLE, MENUBUTTON_STYLE = ALL_STYLES["Label"], ALL_STYLES["Button"], ALL_STYLES["Radiobutton"], ALL_STYLES["Menubutton"]
ENTRY_STYLE, SCALE_STYLE, CHECKBUTTON_STYLE = ALL_STYLES["Entry"], ALL_STYLES["Scale"], ALL_STYLES["Checkbutton"]

### Extensions onto original classes

class EntryBase(Entry):
	'''Mock class for disambiguity'''
	pass
	
class FrameBase(Frame):
	'''Mock class for disambiguity'''
	pass
	
class Entry(EntryBase):
	'''Inherited class that adds methods to tk.Entry'''
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

class Frame(FrameBase):
	'''Inherited class that adds methods to tk.Frame'''
	def gridWidgets(self, *widgets, **options):
		'''Grids all of the widgets'''
		gridWidgets(*widgets, **options)
	
	def childWidgets(self):
		'''Finds all widgets in the main instance'''
		self.widgetsFound = findAllWidgets(self)
		return self.widgetsFound
		
	def resize(self):
		'''Allows the widget to be resized'''
		self.grid_rowconfigure(0, weight = 1)
		self.grid_columnconfigure(0, weight = 1)
			
### Additional wrapper classes
			
class MessageBox(BaseCustomWindow):
	'''Creates a simple message box
	Supported options:
	title, message, font, fg, bg, justify, wrap, resize, button, command, buttonFg, buttonBg, width, buttonFont, offsetX, offsetY, cleanup'''
	def __init__(self, master = None, message = "", **options):
		if not master: 
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.options = master, options
		self.message, self.fg, self.bg, self.font, self.justify = options.get('message', message), options.get('fg'), options.get('bg'), options.get('font'), options.get('justify', CENTER)
		self.button, self.command, self.width, self.buttonFont = options.get('button', 'Ok'), options.get('command', self.close), options.get('width', 10), options.get('buttonFont')
		self.buttonFg, self.buttonBg, self.shouldResize, self.shouldCenter = options.get('buttonFg'), options.get('buttonBg'), options.get('resize', True), options.get('center', True)
		self.offsetX, self.offsetY, self.cleanup, self.wrap = options.get('offsetX', 25), options.get('offsetY', 25), options.get('cleanup', doNothing), options.get('wrap')
		self.master.title(self.options.get('title', ''))
		self.mainFrame = Frame(self.master)
		configureStyle(self.master.styles["Label"], "Message.TLabel", foreground = self.fg, background = self.bg, font = self.font, justify = self.justify)
		configureStyle(self.master.styles["Button"], "Message.TButton", font = self.buttonFont, foreground = self.buttonFg, background = self.buttonBg)
		if self.message:
			num_lines = self.message.count('\n')
			if (num_lines > 5) or self.wrap:
				if num_lines >= 15:
					num_lines = 15
				else:
					num_lines += 2
				if not self.wrap:
					self.wrap = WORD
				self.messageLabel = ScrolledText(self.mainFrame, font = self.font, wrap = self.wrap, height = num_lines)
				self.messageLabel.insert(END, self.message)
				self.messageLabel.configure(state = DISABLED)
			else:
				self.messageLabel = Label(self.mainFrame, text = self.message, style = "Message.TLabel")
			self.messageLabel.grid(row = 1)
			if isinstance(self.button, Button):
				self.mainButton = self.button
			else:
				self.mainButton = Button(self.mainFrame, text = self.button, command = self.command, style = "Message.TButton", width = self.width)
			self.mainButton.grid(row = 2, pady = 5)
		self.master.bind("<Return>", (lambda event: self.mainButton.invoke()))
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

class Tooltip(BaseCustomWindow):
	'''Creates a window similar to IDLE's tool-tips
	Supported options:
	widget, text, fg, bg, background, font, delay, event = binding, events = bindings, leave, offsetX, offset, condition, cleanup
	
	Argument Notes: condition is a BooleanVar instance'''
	def __init__(self, widget, **options):
		self.options, self.widget = options, widget
		self.text, self.delay, self.fg, self.bg, self.font = self.options.get('text', ''), self.options.get('delay', 500), self.options.get('fg'), self.options.get('bg'), self.options.get('font')
		self.event, self.leave = self.options.get('event', self.options.get("binding", "<Enter>")), self.options.get("leave", "<Leave>"), 
		self.condition, self.background = self.options.get('condition', None), self.options.get('background', '')
		if not self.condition:
			self.condition = BooleanVar(self.widget, True)
		self.events = self.options.get('events', self.options.get('bindings', [self.event]))
		self.offsetX, self.offsetY, self.cleanup = self.options.get('offsetX', 0), self.options.get('offsetY', 0), self.options.get('cleanup', doNothing)
		self.master = None
		try:
			style = widget.master.styles["Label"]
		except AttributeError:
			style = LABEL_STYLE
		configureStyle(style, "Calltip.TLabel", foreground = self.fg, background = self.bg, font = self.font)
		for binding in self.events:
			self.widget.bind(binding, lambda event: self.show(event), True)
		self.widget.bind(self.leave, lambda event: self.hide(), True)

	def show(self, event):
		'''Shows the tooltip'''
		if self.condition.get() and not self.master:
			self.master = Toplevel(self.widget)
			self.master.wm_overrideredirect(1)
			self.label = Label(self.master, text = self.text, style = "Calltip.TLabel")
			self.label.configure(background = self.background)
			self.label.pack()
			self.label.update()
			try:
				self.x, self.y, self.posX, self.posY = self.label.winfo_width(), self.label.winfo_height(), self.widget.winfo_rootx(), self.widget.winfo_rooty()
			except TclError:
				return
			self.master.geometry("{xSize}x{ySize}+{x}+{y}".format(xSize = self.x, ySize = self.y, x = event.x_root + self.offsetX, y = event.y_root + self.offsetY))
			if self.delay: 
				try:
					self.master.after(self.delay, lambda: self.hide())
				except TclError:
					pass
		
	def hide(self):
		'''Hides the tooltip'''
		if self.master:
			self.master.withdraw()
			self.master.destroy()
			self.master = None
			
	@staticmethod
	def add(widget, **options):
		'''Creates a tooltip on the widget, using the specified options'''
		return Tooltip(widget, **options)

class Calltip(Tooltip):
	'''Maintained for backwards-compatibility'''
	pass
			
class Infobox(BaseCustomWindow):
	'''Creates an information box, based on a widget
	Supported options:
	title, text, fg, bg, font, events, delay, widget, offsetX, offsetY, width, height, cleanup'''
	def __init__(self, widget = None, **options):
		self.options = options
		self.title, self.text, self.fg, self.bg, self.w, self.h = options.get('title', 'Information'), options.get('text', ''), options.get('fg'), options.get('bg'), options.get('width'), options.get('height')
		self.font, self.events = options.get('font'), options.get('events', ["<Double-Button-1>"])
		self.delay, self.widget, self.offsetX, self.offsetY, self.cleanup = options.get('delay', 100), widget, options.get('offsetX', 0), options.get('offsetY', 0), options.get('cleanup', doNothing)
		if self.widget is None:
			self.window = MessageBox(title = self.title, message = self.text, fg = self.fg, bg = self.bg)
		else:
			self.window = Toplevel()
			createBaseStyles(self.window, self.font)
			self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
			self.window.title(self.title)
			configureStyle(self.window.styles["Label"], "Infobox.TLabel", foreground = self.fg, background = self.bg, font = self.font)
			self.label = Label(self.window, text = self.text, style = "Infobox.TLabel")
			self.label.pack()
			self.window.update()
			self.xPos, self.yPos = self.widget.winfo_rootx() + 25, self.widget.winfo_rooty() + 25
			if self.w is None:
				self.w = self.label.winfo_width()
			if self.h is None:
				self.h = self.label.winfo_height()
			x, y = self.w, self.h
			self.window.geometry("{x}x{y}+{x1}+{y1}".format(x = x, y = y, x1 = self.xPos, y1 = self.yPos))
			self.window.withdraw()
			for event in self.events:
				self.widget.bind(event, (lambda e: self.show(e)))
			self.window.protocol("WM_DELETE_WINDOW", self.quit)

	def show(self, event):
		'''Show the infobox'''
		self.window.deiconify()
		self.window.update()
		x, y = event.x_root, event.y_root
		if screenDim[0] - x < self.w:
			x = screenDim[0] - self.w - 25
		if screenDim[1] - y < self.h:
			y = screenDim[1] - self.h - 25
		self.window.geometry("+{x}+{y}".format(x = x + self.offsetX, y = y + self.offsetY))
		if self.delay:
			self.window.after(self.delay, self.window.withdraw)

class Prompt(BaseCustomWindow):
	'''Creates a basic prompt with a question, with Buttons representing each option
	Supported options:
	title, fg, bg, font, buttonSize, buttonFont, exitCommand = quitCommand, cleanup, defaultButton, defaultBinding, maxRow, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", *choices, **options):
		if not master:
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.fg, self.bg, self.font = self.options.get('title', ''), self.options.get('fg'), self.options.get('bg'), self.options.get('font')
		self.buttonSize, self.buttonFont, self.defaultButton =  self.options.get('buttonSize', 10), self.options.get('buttonFont', (10,)), self.options.get('defaultButton', choices[0])
		self.defaultBinding, self.maxRow = self.options.get('defaultBinding', "<Return>"), self.options.get('maxRow', 5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.shouldCenter, self.shouldResize = self.options.get('center', True), self.options.get('resize', True)
		self.offsetX, self.offsetY, self.cleanup = self.options.get('offsetX', 25), self.options.get('offsetY', 25), options.get('cleanup', doNothing)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		self.choice = StringVar(self.buttonFrame)
		configureStyle(self.master.styles["Label"], "Prompt.TLabel", font = self.font, foreground = self.fg, background = self.bg)
		configureStyle(self.master.styles["Button"], "Prompt.TButton", font = self.buttonFont)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, style = "Prompt.TLabel")
		row, column = 1, 1
		for choice in choices:
			choiceButton = Button(self.buttonFrame, text = choice, width = self.buttonSize, style = "Prompt.TButton", command = createLambda(self.setOption, choice))
			choiceButton.grid(row = row, column = column, padx = 5)
			if choice == self.defaultButton:
				self.master.bind(self.defaultBinding, self.createBinding(choiceButton))
				choiceButton.configure(default = ACTIVE)
			if column % self.maxRow == 0:
				row += 1
				column = 1
			else:
				column += 1
		self.quitButton = Button(self.buttonFrame, text = 'Quit', style = "Quit.TButton", width = self.buttonSize, command = self.exitCommand)
		if column % self.maxRow == 0:
			self.quitButton.grid(row = row, column = column, padx = 5)
		else:
			self.quitButton.grid(row = row, column = column + 1, padx = 5)
		self.promptLabel.grid(row = 1, padx = 5, pady = 5)
		self.buttonFrame.grid(row = 2, padx = 5, pady = 5)
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

	def createBinding(self, button):
		return lambda event: button.invoke()

	def get(self):
		'''Returns the selected value'''
		return self.choice.get()

	def setOption(self, option):
		'''Sets the option and destroys the Prompt: only to be used internally'''
		self.choice.set(option)
		self.destroy()

class OptionsWindow(BaseCustomWindow):
	'''Creates an Options window with a question, with Radiobuttons representing each option
	Supported options:
	title, fg, bg, font, optionSize, optionFont, defaultOption, binding, maxRow, indicatoron, exitCommand = quitCommand, cleanup, okText = goText, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", *choices, **options):
		if not master:
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.font, self.fg, self.bg = self.options.get('title', ''), self.options.get('font'), self.options.get('fg'), self.options.get('bg')
		self.optionSize, self.optionFont, self.defaultOption =  self.options.get('optionSize', 10), self.options.get('optionFont'), self.options.get('defaultOption', self.choices[0])
		self.binding, self.maxRow = self.options.get('binding', "<Double-Button-1>"), self.options.get('maxRow', 5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.goText, self.shouldCenter, self.shouldResize = self.options.get('goText', self.options.get('okText', 'Go')), self.options.get('center', True), self.options.get('resize', True)
		self.offsetX, self.offsetY, self.indicatoron, self.cleanup = self.options.get('offsetX', 25), self.options.get('offsetY', 25), self.options.get('indicatoron', True), self.options.get('cleanup', doNothing)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame, self.lastButtonFrame = Frame(self.mainFrame), Frame(self.mainFrame)
		configureStyle(self.master.styles["Label"], "Options.TLabel", font = self.font)
		configureStyle(self.master.styles["Radiobutton"], "Options.TRadiobutton", font = self.optionFont, indicatoron = self.indicatoron)
		configureStyle(self.master.styles["Button"], "Options.TButton", font = self.optionFont)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, style = "Options.TLabel")
		self.choice = StringVar(self.buttonFrame, value = None)
		row, column = 1, 1
		for choice in choices:
			choiceButton = Radiobutton(self.buttonFrame, text = choice, width = self.optionSize, style = "Options.TRadiobutton", variable = self.choice, value = choice)
			choiceButton.grid(row = row, column = column, padx = 5)
			choiceButton.bind(self.binding, self.createBinding(choiceButton))
			if choice == self.defaultOption:
				choiceButton.invoke()
			if column % self.maxRow == 0:
				row += 1
				column = 1
			else:
				column += 1
		self.goButton = Button(self.lastButtonFrame, text = self.goText, width = self.optionSize, style = "Options.TButton", command = self.destroy)
		self.quitButton = Button(self.lastButtonFrame, text = 'Quit', width = self.optionSize, command = self.exitCommand, style = "Quit.TButton")
		self.master.bind("<Return>", lambda event: self.goButton.invoke())
		self.goButton.grid(row = 1, column = 1, padx = 5)
		self.quitButton.grid(row = 1, column = 2, padx = 5)
		self.promptLabel.grid(row = 1, padx = 5, pady = 5)
		self.buttonFrame.grid(row = 2, padx = 5, pady = 5)
		self.lastButtonFrame.grid(row = 3, padx = 5, pady = 5)
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

	def get(self):
		'''Returns the selected value'''
		return self.choice.get()

	def selectAndQuit(self, button):
		'''Selects the button and quits the window'''
		button.invoke()
		self.destroy()

	def createBinding(self, button):
		'''Creates an event-driven binding'''
		return lambda event: self.selectAndQuit(button)

class MultipleOptionsWindow(BaseCustomWindow):
	'''Creates a window with checkboxes representing multiple options
	Supported options:
	title, fg, bg, font, binding, buttonFont, maxRow, exitCommand = quitCommand, cleanup, okText = goText, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", *choices, **options):	
		if not master: 
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.font, self.binding, self.buttonFont = self.options.get('title', ''), self.options.get('font', (10,)), self.options.get('binding', "<Return>"), self.options.get('buttonFont', (10,))
		self.fg, self.bg, self.maxRow = self.options.get('fg'), self.options.get('bg'), self.options.get('maxRow' ,5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.goText, self.cleanup, self.shouldCenter = self.options.get('goText', self.options.get('okText', 'Go')), self.options.get('cleanup', doNothing), self.options.get('center', True)
		self.shouldResize, self.offsetX, self.offsetY = self.options.get('resize', True), self.options.get('offsetX', 25), self.options.get('offsetY', 25)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		configureStyle(self.master.styles["Label"], "MultOptions.TLabel", foreground = self.fg, background = self.bg, font = self.font)
		configureStyle(self.master.styles["Checkbutton"], "Checkbutton.MultOptions.TCheckbutton", font = self.buttonFont)
		configureStyle(self.master.styles["Button"], "Button.MultOptions.TButton", font = self.font, foreground = self.fg, background = self.fg)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, style = "Checkbutton.MultOptions.TCheckbutton")
		self.promptLabel.grid(row = 1, pady = 5)
		self.variables, self.hasQuit = {}, False
		row, column = 1, 1
		for choice in self.choices:
			checkVar = IntVar()
			checkButton = Checkbutton(self.buttonFrame, text = choice, onvalue = True, offvalue = False, variable = checkVar, style = "MultOptions.TCheckbutton")
			checkButton.grid(row = row, column = column)
			checkButton.invoke()
			checkButton.invoke()
			self.variables[choice] = checkVar
			if row % self.maxRow == 0:
				column += 1
				row = 1
			else:
				row += 1
		self.okButton = Button(self.mainFrame, text = self.goText, command = self.exitCommand, style = "Button.MultOptions.TButton")
		self.quitButton = Button(self.mainFrame, text = "Quit", command = self.quitCommand, style = "Quit.TButton")
		self.buttonFrame.grid(row = 2, pady = 5)
		self.okButton.grid(row = 3, pady = 5)
		self.quitButton.grid(row = 4, pady = 5)
		self.mainFrame.grid(row = 1, column = 1, padx = self.offsetX, pady = self.offsetY)
		
	def quitCommand(self):
		'''Indicates that the user has quit the program'''
		self.hasQuit = True
		self.okButton.invoke()
		
	def get(self):
		'''Returns the user's input'''
		return {choice: value.get() for choice, value in self.variables.items()} if not self.hasQuit else {}
		
class InputWindow(BaseCustomWindow):
	'''Creates an Entry Window with a prompt and space to enter input
	Supported options:
	title, fg, bg, font, binding, type, show, to, from_, defaultValue, resolution, width, buttonFont, exitCommand = quitCommand, cleanup, okText = goText, buttonWidth, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", **options):
		if not master:
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.prompt, self.options = master, prompt, options
		self.title, self.font, self.binding, self.entryType = self.options.get('title', ''), self.options.get('font', (10,)), self.options.get('binding', "<Return>"), self.options.get('type', str)
		self.bg, self.fg = self.options.get('bg'), self.options.get('fg')
		self.exitCommand, self.buttonFont = self.options.get('exitCommand', self.options.get('quitCommand', self.close)), self.options.get('buttonFont', (10,))
		self.goText, self.width, self.buttonWidth = self.options.get('okText', self.options.get('goText', 'Go')), self.options.get('width', 25), self.options.get('buttonWidth', 10)
		self.shouldCenter, self.shouldResize, self.offsetX, self.offsetY = self.options.get('center', True), self.options.get('resize', True),self.options.get('offsetX', 25), self.options.get('offsetY', 25)
		self.fromWhat, self.toWhat, self.defaultValue, self.cleanup = self.options.get('from_', 0), self.options.get('to', 100), self.options.get('defaultValue'), self.options.get('cleanup', doNothing)
		self.resolution, self.show = self.options.get('resolution', 1), self.options.get('show', None)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		configureStyle(self.master.styles["Label"], "Input.TLabel", font = self.font, foreground = self.fg, background = self.bg)
		configureStyle(self.master.styles["Entry"], "Input.TEntry", font = self.font)
		configureStyle(self.master.styles["Scale"], "Input.Horizontal.TScale", font = self.font, foreground = self.fg, background = self.bg)
		configureStyle(self.master.styles["Button"], "Input.TButton", font = self.buttonFont)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, style = "Input.TLabel")
		self.promptLabel.grid(row = 1, pady = 5)
		if self.entryType == str:
			if (self.defaultValue is None) or not isinstance(self.defaultValue, str):
				self.defaultValue = ''
			self.entry = StringVar(self.mainFrame, value = self.defaultValue)
			self.entryBox = Entry(self.mainFrame, width = self.width, style = "Input.TEntry", textvariable = self.entry, show = self.show, justify = CENTER)
			self.entryBox.grid(row = 2, pady = 5)
		elif self.entryType == int:
			self.entry = IntVar(self.mainFrame)
			self.entryLabel = Label(self.mainFrame, style = "Input.TLabel", textvariable = self.entry)
			self.entrySlider = Scale(self.mainFrame, style = "Input.Horizontal.TScale", variable = self.entry, from_ = self.fromWhat, to = self.toWhat, length = self.width, orient = HORIZONTAL, command = lambda e:
	self.entry.set(type(self.resolution)(self.resolution * round(float(self.entry.get()) / self.resolution))))
			if (self.defaultValue is None) or not isinstance(self.defaultValue, (int, float)):
				self.defaultValue = float(self.toWhat - self.fromWhat) / 2
			self.entrySlider.set(self.defaultValue)
			self.entryLabel.grid(row = 2, pady = 5)
			self.entrySlider.grid(row = 3, pady = 5)
		self.goButton = Button(self.buttonFrame, text = self.goText, style = "Input.TButton", width = self.buttonWidth, command = self.quit)
		self.quitButton = Button(self.buttonFrame, text = 'Quit', style = "Quit.TButton", width = self.buttonWidth, command = self.exitCommand)
		self.master.bind(self.binding, lambda event: self.goButton.invoke())
		self.goButton.grid(row = 1, column = 1, padx = 5)
		self.quitButton.grid(row = 1, column = 2, padx = 5)
		self.buttonFrame.grid(row = 4, pady = 5)
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

	def get(self):
		'''Returns the selected value'''
		return self.entry.get()

class LabelledScale(BaseCustomWidget):
	'''Creates a Scale with a Label attached to it
	Supported options:
	font, fg, bg, command, edit, orientation, length, from_, to, type, default, round, binding
	
	Notes on arguments:
		command must return an integer, floating-point number, or Boolean'''
	def __init__(self, master = None, **options):
		if not master:
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.options = master, options
		self.mainFrame = Frame(self.master)
		self.font, self.command, self.edit = self.options.get('font', ''), self.options.get('command', lambda *args: True), self.options.get('edit', False)
		self.fg, self.bg, self.orientation = self.options.get('fg', 'black'), self.options.get('bg', ''), self.options.get('orientation', HORIZONTAL)
		self.to, self.from_, self.binding = self.options.get('to', 10), self.options.get('from_', 0), self.options.get('binding', "<Double-1>")
		self.type, self.round, default = self.options.get('type', int), self.options.get('round', 3), self.options.get('default', self.from_)
		self.length, self.step = self.options.get('length', 100), self.options.get('step', 1 if self.type == int else 0.1)
		self.var = IntVar(self.master) if self.type == int else DoubleVar(self.master)
		self.text_var = StringVar(self.master)
		self.setVar(None, default)
		configureStyle(self.master.styles['Label'], "ScaleLabel.TLabel", font = self.font, foreground = self.fg, background = self.bg)
		self.widget_state = Label
		self.label = Label(self.mainFrame, textvariable = self.text_var, style = "ScaleLabel.TLabel")
		if self.edit:
			self.label.bind(self.binding, self.changeWidget)
			self.entry = Entry(self.mainFrame, justify = CENTER, text = self.var.get())
			self.entry.bind("<Return>")
		self.slider = Scale(self.mainFrame, variable = self.var, command = lambda event: self.setVar(event) + self.command(event), orient = self.orientation, to = self.to, from_ = self.from_, length = self.length)
		self.label.grid(row = 1)
		self.slider.grid(row = 2, pady = 5)
		
	def changeWidget(self, event):
		'''Changes the Label to an entry to allow for editing (or vice versa)'''
		if self.edit:
			if self.widget_state == Label:
				self.label.grid_forget()
				self.entry.bind("<Return>", self.setVar)
				self.entry.grid(row = 1)
				self.widget_state = Entry
			else:
				self.entry.grid_forget()
				self.label = Label(self.mainFrame, textvariable = self.var, style = "ScaleLabel.TLabel")
				self.label.bind("<Double-1>", self.setVar)
				self.label.grid(row = 1)
				self.widget_state = Label
		return True
		
	def setVar(self, event, value = None):
		'''Sets the variable
		Uses value as an override if provided'''
		if value is None:
			value = self.var.get() if isinstance(event, str) else float(self.entry.get())
		if value < self.from_:
			value = self.from_
		elif value > self.to:
			value = self.to
		value = self.type(round(self.step * round(float(value) / self.step), self.round))
		self.var.set(value)
		self.text_var.set(value)
		if isinstance(event, Event):
			self.changeWidget(event)
		return True
		
	def get(self):
		'''Returns the current value'''
		return self.var.get()
	
class Hyperlink(Label):
	'''Uses a Label widget as a hyperlink
	Supported options:
	link, font, command, underline, justify, activeColor, activatedColor, inactiveColor, bindings'''
	def __init__(self, master = None, text = '', **options):
		if not master:
			master = Toplevel()
		if not hasattr(master, 'styles'):
			createBaseStyles(master)
		self.master, self.text, self.options = master, text, options
		self.bindings, self.underline, self.justify = self.options.get('bindings', []), self.options.get('underline', True), self.options.get('justify', CENTER)
		self.link, self.activeColor, self.activatedColor = self.options.get('link'), self.options.get('activeColor', 'red'), self.options.get('activatedColor', 'purple')
		self.inactiveColor, self.command = self.options.get('inactiveColor', 'blue'), self.options.get('command', lambda: webbrowser.open_new_tab(self.link))
		label_style = self.master.styles["Label"]
		configureStyle(label_style, "HyperlinkInactive.TLabel", font = self.font, foreground = self.inactiveColor, justify = self.justify)
		configureStyle(label_style, "HyperlinkActive.TLabel", font = self.font, foreground = self.activeColor, justify = self.justify)
		configureStyle(label_style, "HyperlinkActivated.TLabel", font = self.font, foreground = self.activatedColor, justify = self.justify)
		Label.__init__(self, self.master, text = self.text, style = "HyperlinkInactive.TLabel")
		self.bind("<Enter>", lambda event: self.configure(style = "HyperlinkActivated.TLabel"))
		self.bind("<Leave>", lambda event: self.configure(style = "HyperlinkInactive.TLabel"))
		self.bind("<1>", lambda event: self.click())
		self.hyperFont = tkFont.Font(self, self.cget("font"))
		self.hyperFont.configure(underline = self.underline)
		self.configure(style = "HyperlinkInactive.TLabel")
		for binding in self.bindings:
			self.bind(binding, lambda event: self.click())

	def click(self):
		self.command()
		self.configure(style = "HyperlinkActivated.TLabel")

class Statusbar:
	'''Wrapper on ttk's Progressbar'''
	def __init__(self, master = None, **options):
		if not master: 
			master = Toplevel()
		self.mainFrame = Frame(master)
		self.master, self.options = master, options
		self.addText, self.truncate, self.value, self.mainVar, self.textPercent = self.options.get('addText', True), self.options.get('truncate', 3), 0, IntVar(self.mainFrame, 0), self.options.get('textPercent', True)
		self.textPercent = ' %' if self.textPercent else ''
		for option, default in zip(['orient', 'length', 'maximum'], [HORIZONTAL, 200, 200]):
			if not self.options.get(option): 
				self.options[option] = default
		for option in ('barFill', 'addText', 'truncate'):
			if option in self.options:
				del self.options[option]
		self.progressbar = Progressbar(self.mainFrame, variable = self.mainVar, **self.options)
		self.progressbar.grid(row = 1)
		self.offset = self.options['length'] / 100
		if self.addText:
			self.text = Label(self.mainFrame, text = str(self.value) + self.textPercent, style = "TLabel")
			self.text.grid(row = 2)

	def change(self, value):
		'''Adds to the current value as a percent'''
		if (self.value + value) <= self.options['maximum']:
			self.setValue(self.value + value)

	def setValue(self, value):
		'''Sets the current value as a percent'''
		self.mainVar.set(value * self.offset)
		self.value = round(value, self.truncate)
		if self.addText:
			self.text.configure(text = str(self.value) + self.textPercent)
		
	def grid(self, *args, **kwargs):
		'''Grids the widget'''
		self.mainFrame.grid(*args, **kwargs)

	def pack(self, *args, **kwargs):
		'''Packs the widget'''
		self.mainFrame.pack(*args, **kwargs)
		
	def place(self, *args, **kwargs):
		'''Places the widget'''
		self.mainFrame.place(*args, **kwargs)
		
class EventMenu(Menu):
	'''Creates a Menu on a widget based off of events
	Commands are in the format [{'label': label, 'command': command, 'type': type, 'accelerator': accelerator}, ...]
	For separators, simply use {'type': 'separator'}'''
	def __init__(self, widget, commands, *args, **options):
		self.widget, self.master, self.options, self.commands, self.event = widget, widget.master, options, commands, None
		self.binding = self.options.get('binding')
		if self.binding:
			del self.options['binding']
		else:
			self.binding = "<Button-3>"
		if not "tearoff" in self.options.keys():
			self.options["tearoff"] = False
		Menu.__init__(self, self.widget, *args, **self.options)
		self.var = StringVar(self, value = '')
		for d in self.commands:
			self.addItem(**d)
		self.widget.bind(self.binding, lambda event: self.show(event))

	def setCommands(self, commands):
		'''Sets the commands'''
		self.delete(0, END)
		self.commands = commands
		for d in self.commands:
			self.addItem(**d)
		
	def addItem(self, **options):
		'''Adds a item to the menu'''
		d = options
		_type = d.get('type')
		if _type == SEPARATOR:
			self.add_separator()
		elif _type == CHECKBUTTON:
			self.add_checkbutton(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
		elif _type == RADIOBUTTON:
			self.add_radiobutton(label = d.get("label"), command = d.get('command'), accelerator = d.get("accelerator", variable = self.var, value = d.get("label")))
		elif _type == COMMAND:
			self.add_command(label = d.get("label"), command = d.get("command"), accelerator = d.get("accelerator"))
	
	def show(self, event):
		'''Shows the window'''
		self.event = event
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
		methods = list(vars(Pack).keys()) + list(vars(Grid).keys()) + list(vars(Place).keys())
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
		
class CheckButton(Checkbutton):
	'''Checkbutton wrapper'''
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
		'''Gets the current checkbutton value'''
		return self.buttonVariable.get()
		
	def set(self, value):
		'''Sets the current checkbutton value'''
		self.buttonVariable.set(value)
		
	def toggle(self):
		'''Toggles the checkbutton on/off'''
		self.buttonVariable.set(not self.buttonVariable.get())
		
class CodeEditor(ScrolledText):
	'''Implements a Code-editor-type widget, with syntax highlighting'''
	def __init__(self, master = None, **options):
		self.master = master
		if 'syntaxcolors' in options.keys():
			self.colors = options['syntaxcolors']
			del options['syntaxcolors']
		else:
			self.colors = {"keyword": "orange", "object": "purple", "operator": "red", "variable": "blue", "string": "green"}
		ScrolledText.__init__(self, master, **options)
		self.bind("<Control-a>", lambda event: self.selectAll())
		for syntax in ("keyword", "object", "operator", "variable", "string"):
			self.tag_configure(syntax, foreground = self.colors[syntax])
		
		
	def highlight(self):
		'''Highlights all of the syntax'''
		self.tag_words("keyword", *PY_KEYWORDS)
		self.tag_words("object", *PY_OBJECTS)
		self.tag_words("operator", *PY_OPERATORS)
		
	def selectAll(self):
		'''Selects all of the text'''
		self.tag_add("sel", "1.0", END)
		
	def tag_words(self, tag, *words):
		'''Applies the tag to the words'''
		for word in words:
			index = "1.0"
			while index:
				pattern = "( |\()({word})( |\))".format(word = word) # only want to find this word, surrounded by a space, " ", or a parenthesis --- no partial words
				# pattern = word
				index = self.search(pattern, index, END, regexp = True)
				if index:
					line, char = index.split('.')
					endIndex = "{line}.{char}".format(line = line, char = int(char) + len(word))
					self.tag_add(tag, index, endIndex)
					index = endIndex