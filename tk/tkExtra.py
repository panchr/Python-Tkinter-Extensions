# tk/tkExtra.py
# Rushy Panchal
# v1.11

'''tkExtra adds on to existing ttk classes and functions.
By doing so, it is easier to accomplish common tasks.
It also creates custom, frequently used classes that extend existing Tkinter classes.

Other features include:
	- Automatic gridding of widgets in a structured format
	- Generation of Base Styles for a main window
	- Simple style naming and configuration
	- Tooltip support for any widget
	- Extensions onto existing Tkinter classes
	- Custom windows and widgets for common tasks
	
This module uses the standard Tkinter package.'''

### Change Log:
	# v1.0: Initial Release: Addition of methods onto existing Tkinter classes via inheritance
	# v1.1: Additonal classes added, each inheriting from a base class
		#1.11: Even more classes and bug fixes: window closing was closing every other widget

try:
	from tk.tkBase import *
	import tkFont
except ImportError: 
	from tk.tkBase import *
	from io import IOBase as file
	import tkinter.font as tkFont
import webbrowser

### Additional wrapper classes

class MessageBox(BaseCustomWindow):
	'''Creates a simple message box
	Supported options:
	title, message, font, fg, bg, resize, button, command, buttonFg, buttonBg, width, buttonFont, offsetX, offsetY, cleanup'''
	def __init__(self, master = None, message = "", **options):
		self.title, self.message, self.fg, self.bg, self.font = options.get('title'), options.get('message'), options.get('fg'), options.get('bg'), options.get('font', ('', 10))
		self.button, self.command, self.width, self.buttonFont = options.get('button', 'Ok'), options.get('command', master.quit), options.get('width'), options.get('buttonFont')
		self.buttonFg, self.buttonBg, self.shouldResize, self.shouldCenter = options.get('buttonFg'), options.get('buttonBg'), options.get('resize', True), options.get('center', True)
		self.offsetX, self.offsetY, self.cleanup = options.get('offsetX', 25), options.get('offsetY', 25), options.get('cleanup', doNothing)
		self.options = options
		root = master
		if root is None:
			root = Tk()
		master = Toplevel(root, resize= self.resize, center = self.center)
		root.withdraw()
		master.title(self.title)
		self.master, self.mainFrame = master, Frame(master)
		self.master.configure(bg = self.bg)
		if self.message:
			self.messageLabel = Label(self.mainFrame, text = self.message, font = self.font, fg = self.fg)
			self.messageLabel.grid(row = 1)
			if isinstance(self.button, Button):
				self.mainButton = self.button
			else:
				self.mainButton = Button(self.mainFrame, text = self.button, command = self.command)
				self.mainButton.configure(font = self.buttonFont, width = self.width, fg = self.buttonFg, bg = self.buttonBg)
			self.mainButton.grid(row = 2)
		self.master.bind("<Return>", (lambda event: self.mainButton.invoke()))
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

class Tooltip:
	'''Creates a window similar to IDLE's tool-tips
	Supported options:
	widget, text, fg, bg, font, delay, event = binding, events = bindings, leave, offsetX, offset, cleanup'''
	def __init__(self, widget, **options):
		self.options, self.widget = options, widget
		self.text, self.delay, self.fg, self.bg, self.font = options.get('text', ''), options.get('delay', 500), options.get('fg'), options.get('bg'), options.get('font', ('', 10))
		self.event, self.leave = options.get('event', self.options.get("binding", "<Enter>")), self.options.get("leave", "<Leave>")
		self.events = self.options.get('events', self.options.get('bindings', [self.event]))
		self.offsetX, self.offsetY, self.cleanup = options.get('offsetX', 0), options.get('offsetY', 0), options.get('cleanup', doNothing)
		self.master = Toplevel(self.widget)
		self.master.wm_overrideredirect(1)
		self.label = Label(self.master, text = self.text)
		self.label.pack()
		self.label.update()
		self.x, self.y, self.posX, self.posY = self.label.winfo_width(), self.label.winfo_height(), self.widget.winfo_rootx(), self.widget.winfo_rooty()
		self.master.geometry("{xSize}x{ySize}+{x}+{y}".format(xSize = self.x, ySize = self.y, x = self.posX, y = self.posY))
		self.master.withdraw()
		for binding in self.events:
			self.widget.bind(binding, lambda event: self.show(event))
		self.widget.bind(self.leave, lambda event: self.master.withdraw())
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

	def show(self, event):
		'''Shows the tooltip'''
		self.master.deiconify()
		self.master.update()
		self.master.geometry("+{x}+{y}".format(x = event.x_root + self.offsetX, y = event.y_root + self.offsetY))
		if self.delay: self.master.after(self.delay, lambda: self.master.withdraw())
		
class Calltip(Tooltip):
	'''Maintained for backwards-compatibility'''
	pass

class Infobox:
	'''Creates an information box, based on a widget
	Supported options:
	title, text, fg, bg, font, events, delay, widget, offsetX, offsetY, width, height, cleanup'''
	def __init__(self, widget = None, **options):
		self.options = options
		self.title, self.text, self.fg, self.bg, self.w, self.h = options.get('title', 'Information'), options.get('text', ''), options.get('fg'), options.get('bg'), options.get('width'), options.get('height')
		self.font, self.events = options.get('font', ('', 10)), options.get('events', ["<Double-Button-1>"])
		self.delay, self.widget, self.offsetX, self.offsetY, self.cleanup = options.get('delay', 100), widget, options.get('offsetX', 0), options.get('offsetY', 0), options.get('cleanup', doNothing)
		if self.widget is None:
			self.window = MessageBox(title = self.title, message = self.text, fg = self.fg, bg = self.bg)
		else:
			self.window = Toplevel()
			self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
			self.window.title(self.title)
			self.label = Label(self.window, text = self.text, fg = self.fg, bg = self.bg, font = self.font)
			self.label.pack()
			self.window.update()
			self.xPos, self.yPos = self.widget.winfo_rootx() + 25, self.widget.winfo_rooty() + 25
			if self.w is None: self.w = self.label.winfo_width()
			if self.h is None: self.h = self.label.winfo_height()
			x, y = self.w, self.h
			self.window.geometry("{x}x{y}+{x1}+{y1}".format(x = x, y = y, x1 = self.xPos, y1 = self.yPos))
			self.window.withdraw()
			for event in self.events:
				self.widget.bind(event, (lambda e: self.show(e)))
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

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
		if self.delay: self.window.after(self.delay, self.window.withdraw)

class Prompt(BaseCustomWindow):
	'''Creates a basic prompt with a question, with Buttons representing each option
	Supported options:
	title, font, buttonSize, buttonFont, exitCommand = quitCommand, cleanup, defaultButton, defaultBinding, maxRow, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", *choices, **options):
		if not master:
			master = Tk()
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.font = self.options.get('title', ''), self.options.get('font', ('', 10))
		self.buttonSize, self.buttonFont, self.defaultButton =  self.options.get('buttonSize', 10), self.options.get('buttonFont', (10,)), self.options.get('defaultButton', choices[0])
		self.defaultBinding, self.maxRow = self.options.get('defaultBinding', "<Return>"), self.options.get('maxRow', 5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.shouldCenter, self.shouldResize = self.options.get('center', True), self.options.get('resize', True)
		self.offsetX, self.offsetY, self.cleanup = self.options.get('offsetX', 25), self.options.get('offsetY', 25), options.get('cleanup', doNothing)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		self.choice = StringVar(self.buttonFrame)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, font = self.font)
		row, column = 1, 1
		for choice in choices:
			choiceButton = Button(self.buttonFrame, text = choice, width = self.buttonSize, font = self.buttonFont, command = createLambda(self.setOption, choice))
			choiceButton.grid(row = row, column = column, padx = 5)
			if choice == self.defaultButton:
				self.master.bind(self.defaultBinding, self.createBinding(choiceButton))
				choiceButton.configure(default = ACTIVE)
			if column % self.maxRow == 0:
				row += 1
				column = 1
			else:
				column += 1
		self.quitButton = Button(self.buttonFrame, text = 'Quit', fg = 'red', width = self.buttonSize, font = self.buttonFont, command = self.exitCommand)
		if column % self.maxRow == 0: self.quitButton.grid(row = row, column = column, padx = 5)
		else: self.quitButton.grid(row = row, column = column + 1, padx = 5)
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
	title, font, optionSize, optionFont, defaultOption, binding, maxRow, indicatoron, exitCommand = quitCommand, cleanup, okText = goText, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", *choices, **options):
		if not master:
			master = Tk()
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.font = self.options.get('title', ''), self.option.get('font', ('', 10))
		self.optionSize, self.optionFont, self.defaultOption =  self.options.get('optionSize', 10), self.options.get('optionFont', (10,)), self.options.get('defaultOption', choices[0])
		self.binding, self.maxRow = self.options.get('binding', "<Double-Button-1>"), self.options.get('maxRow', 5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.goText, self.shouldCenter, self.shouldResize = self.options.get('goText', self.options.get('okText', 'Go')), options.get('center', True), self.options.get('resize', True)
		self.offsetX, self.offsetY, self.indicatoron, self.cleanup = self.options.get('offsetX', 25), self.options.get('offsetY', 25), self.options.get('indicatoron', True), self.options.get('cleanup', doNothing)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame, self.lastButtonFrame = Frame(self.mainFrame), Frame(self.mainFrame)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, font = self.font)
		self.choice = StringVar(self.buttonFrame, value = None)
		row, column = 1, 1
		for choice in choices:
			choiceButton = Radiobutton(self.buttonFrame, text = choice, width = self.optionSize, font = self.optionFont, variable = self.choice, value = choice, indicatoron = self.indicatoron)
			choiceButton.grid(row = row, column = column, padx = 5)
			choiceButton.bind(self.binding, self.createBinding(choiceButton))
			if choice == self.defaultOption:
				choiceButton.select()
			if column % self.maxRow == 0:
				row += 1
				column = 1
			else:
				column += 1
		self.goButton = Button(self.lastButtonFrame, text = self.goText, width = self.optionSize, font = self.optionFont, default = ACTIVE, command = self.destroy)
		self.quitButton = Button(self.lastButtonFrame, text = 'Quit', fg = 'red', width = self.optionSize, font = self.optionFont, command = self.exitCommand)
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
		button.select()
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
			master = Tk()
		self.master, self.prompt, self.choices, self.options = master, prompt, choices, options
		self.title, self.font, self.binding, self.buttonFont = self.options.get('title', ''), self.options.get('font', (10,)), self.options.get('binding', "<Return>"), self.options.get('buttonFont', (10,))
		self.fg, self.bg, self.maxRow = self.options.get('fg'), self.options.get('bg'), self.options.get('maxRow' ,5)
		self.exitCommand = self.options.get('exitCommand', self.options.get('quitCommand', self.quit))
		self.goText, self.cleanup, self.shouldCenter = self.options.get('goText', self.options.get('okText', 'Go')), self.options.get('cleanup', doNothing), self.options.get('center', True)
		self.shouldResize, self.offsetX, self.offsetY = self.options.get('resize', True), self.options.get('offsetX', 25), self.options.get('offsetY', 25)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, font = self.font, foreground = self.fg, background = self.bg)
		self.promptLabel.grid(row = 1, pady = 5)
		self.variables = {}
		row, column = 1, 1
		for choice in self.choices:
			checkVar = IntVar()
			checkButton = Checkbutton(self.buttonFrame, text = choice, font = self.buttonFont, onvalue = True, offvalue = False, variable = checkVar)
			checkButton.grid(row = row, column = column)
			self.variables[choice] = checkVar
			if row % self.maxRow == 0:
				column += 1
				row = 1
			else:
				row += 1
		self.okButton = Button(self.buttonFrame, text = self.okText, command = self.exitCommand, font = self.font, foreground = self.fg, background = self.bg)
		self.buttonFrame.grid(row = 2, pady = 5)
		self.okButton.grid(row = 3, pady = 5)
		self.mainFrame.grid(row = 1, column = 1, padx = self.offsetX, pady = self.offsetY)
		
	def get(self):
		return {choice: value.get() for choice, value in self.variables.items()}
		
class InputWindow(BaseCustomWindow):
	'''Creates an Entry Window with a prompt and space to enter input
	Supported options:
	title, font, binding, type, to, from, defaultValue, width, buttonFont, exitCommand = quitCommand, cleanup, okText = goText, buttonWidth, center, resize, offsetX, offsetY'''
	def __init__(self, master = None, prompt = "", **options):
		if not master:
			master = Tk()
		self.master, self.prompt, self.options = master, prompt, options
		self.title, self.font, self.binding, self.entryType = self.options.get('title', ''), self.options.get('font', (10,)), self.options.get('binding', "<Return>"), self.options.get('type', str)
		self.exitCommand, self.buttonFont = self.options.get('exitCommand', self.options.get('quitCommand', self.quit)), self.options.get('buttonFont', (10,))
		self.goText, self.width, self.buttonWidth = self.options.get('okText', self.options.get('goText', 'Go')), self.options.get('width', 25), self.options.get('buttonWidth', 10)
		self.shouldCenter, self.shouldResize, self.offsetX, self.offsetY = self.options.get('center', True), self.options.get('resize', True),self.options.get('offsetX', 25), self.options.get('offsetY', 25)
		self.fromWhat, self.toWhat, self.defaultValue, self.cleanup = self.options.get('from_', 0), self.options.get('to', 100), self.options.get('defaultValue'), self.options.get('cleanup', doNothing)
		self.master.title(self.title)
		self.mainFrame = Frame(self.master)
		self.buttonFrame = Frame(self.mainFrame)
		self.promptLabel = Label(self.mainFrame, text = self.prompt, font = self.font)
		self.promptLabel.grid(row = 1, pady = 5)
		if self.entryType == str:
			if (self.defaultValue is None) or not isinstance(self.defaultValue, str): self.defaultValue = ''
			self.entry = StringVar(self.mainFrame, value = self.defaultValue)
			self.entryBox = Entry(self.mainFrame, width = self.width, justify = CENTER, textvariable = self.entry)
			self.entryBox.grid(row = 2, pady = 5)
		elif self.entryType == int:
			self.entry = IntVar(self.mainFrame)
			self.entrySlider = Scale(self.mainFrame, font = self.font, variable = self.entry, orient = HORIZONTAL, from_ = self.fromWhat, to = self.toWhat, resolution = 1, length = self.width)
			if (self.defaultValue is None) or not isinstance(self.defaultValue, (int, float)): self.defaultValue = float(self.toWhat - self.fromWhat) / 2
			self.entrySlider.set(self.defaultValue)
			self.entrySlider.grid(row = 2, pady = 5)
		self.goButton = Button(self.buttonFrame, text = self.goText, font = self.buttonFont, width = self.buttonWidth, default = ACTIVE, command = self.quit)
		self.quitButton = Button(self.buttonFrame, text = 'Quit', fg = 'red', font = self.buttonFont, width = self.buttonWidth, command = self.exitCommand)
		self.master.bind(self.binding, lambda event: self.goButton.invoke())
		self.goButton.grid(row = 1, column = 1, padx = 5)
		self.quitButton.grid(row = 1, column = 2, padx = 5)
		self.buttonFrame.grid(row = 3, pady = 5)
		self.mainFrame.grid(padx = self.offsetX, pady = self.offsetY)
		self.master.protocol("WM_DELETE_WINDOW", self.quit)

	def get(self):
		'''Returns the selected value'''
		return self.entry.get()

class Hyperlink(Label):
	'''Uses a Label widget as a hyperlink
	Supported options:
	link, command, underline, justify, activeColor, activatedColor, inactiveColor, bindings'''
	def __init__(self, master = None, text = '', **options):
		if not master:
			master = Tk()
		self.master, self.text, self.options = master, text, options
		self.bindings, self.underline, self.justify = self.options.get('bindings', []), self.options.get('underline', True), self.options.get('justify', CENTER)
		self.link, self.activeColor, self.activatedColor = self.options.get('link'), self.options.get('activeColor', 'red'), self.options.get('activatedColor', 'purple')
		self.inactiveColor, self.command = self.options.get('inactiveColor', 'blue'), self.options.get('command', lambda: webbrowser.open_new_tab(self.link))
		Label.__init__(self, self.master, text = self.text, fg = self.inactiveColor, justify = self.justify)
		self.bind("<Enter>", lambda event: self.configure(fg = self.activeColor))
		self.bind("<Leave>", lambda event: self.configure(fg = self.inactiveColor))
		self.bind("<1>", lambda event: self.click())
		self.hyperFont = tkFont.Font(self, self.cget("font"))
		self.hyperFont.configure(underline = self.underline)
		self.configure(font = self.hyperFont)
		for binding in self.bindings:
			self.bind(binding, lambda event: self.click())

	def click(self):
		self.command()
		self.configure(fg = self.activatedColor)

class Statusbar(Canvas):
	'''Creates a Statusbar widget'''
	def __init__(self, master = None, **options):
		if not master: master = Tk()
		self.master, self.options = master, options
		self.barFill, self.addText, self.truncate, self.value = self.options.get('barFill', 'red'), self.options.get('addText', True), self.options.get('truncate', 3), 0
		for option in ('barFill', 'addText', 'truncate'):
			if option in self.options: del self.options[option]
		Canvas.__init__(self, master, **self.options)
		self.offset = self.winfo_reqwidth() / 100
		self.height = self.winfo_reqwidth()
		self.bar = self.create_rectangle(0, 0, self.value, self.height, fill = self.barFill)
		if self.addText: self.text = self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2, text = '0%')

	def setValue(self, value):
		'''Sets the value of the status bar as a percent'''
		if value <= 100:
			self.value = round(value * self.offset, self.truncate)
			self.coords(self.bar, 0, 0, self.value, self.height)
			if self.addText: self.itemconfigure(self.text, text = str(self.value/self.offset) + '%')

	def change(self, value):
		'''Changes the value as a percent'''
		if (self.value + value) <= 100:
			self.value = round(self.value + (value * self.offset), self.truncate)
			self.coords(self.bar, 0, 0, self.value, self.height)
			if self.addText: self.itemconfigure(self.text, text = str(self.value/self.offset) + '%')

	def configure(self, **options):
		self.options.update(options)
		self.__init__(self.master, **self.options)