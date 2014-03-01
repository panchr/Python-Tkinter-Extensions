# tk/graphTools.py
# Rushy Panchal
# v1.1

'''Provides various classes and methods to create graphical representations of functions (and polynomial maps)'''

from __future__ import division
try: 
	import Tkinter as tk
except ImportError: 
	import tkinter as tk
	xrange = range
from tk.graphics import *
import threading
import random
import inspect
import cmath
import types
import re

### Constants

LOCAL = "local"
GLOBAL = "global"
X = "x"
Y = "y"

### Main Classes

class Function(object):
	'''Creates a parsable representation of a function'''
	def __init__(self, function):
		self.funct_str = False
		self.variables = {}
		if isinstance(function, str):
			function = ''.join(function.split(' ')).replace('^', '**')
			pattern = re.compile("([0-9]+|[a-z])(?=[a-z\(])", re.IGNORECASE)
			pattern2 = re.compile("([\)])([0-9]+|[a-z])", re.IGNORECASE)
			function = pattern2.sub('\\1*\\2', pattern.sub('\\1*', function))
			self.funct_str = function
			self.function = lambda **variables: eval(function, {"__builtins__": None}, variables)
		elif isinstance(function, (types.FunctionType, types.LambdaType)):
			self.function = function
		else:
			raise TypeError("function can only be a string or callable")
			
	def createVariable(self, *names):
		'''Creates the variable(s)'''
		for name in names:
			self.setVariable(name, 0)
	
	def setVariable(self, name, value = 0):
		'''Sets the variable to the value'''
		self.variables[name] = value
		
	def delVariable(self, *names):
		'''Deletes the variable(s)'''
		for name in names:
			del self.variables[name]
			
	def evaluate(self, **variables):
		'''Evaluates the function by plugging the variables'''
		if "variable" in variables.keys():
			def_value = variables["variable"]
			all_variables = [s for s in self.funct_str if s.isalpha()] if self.funct_str else inspect.getargspec(self.function)
			for v in all_variables:
				if v not in variables.keys(): 
					variables[v] = def_value
			del variables["variable"]
		if not variables:
			variables = self.variables.copy()
		else:
			self.variables = variables.copy()
		return self.function(**variables)
		
	def graph(self, window):
		'''Graphs the function on the window'''
		if not isinstance(window, Graph):
			raise TypeError("window must be a valid Graph object")
		window.graph(self)

class PlaneIteration:
	'''Creates a generator of numbers on the plane'''
	def __init__(self, xStart = 0, xStop = 11, xStep = 1, yStart = 0, yStop = 11, yStep = 1, **options):
		self.xStart, self.xStop, self.xStep, self.yStart, self.yStop, self.yStep, self.options = xStart, xStop, xStep, yStart, yStop, yStep, options
		self.master = self.options.get('master')
		self.buffer = self.options.get('buffer', X)
		self.buffer_action = self.options.get('buffer_action', self.master.flush if self.master else lambda: None)
		self.buffer_every = self.options.get('buffer_every', 1)
		self.iter_amount = 0
		if not self.master: 
			self.buffer = None
			self.buffer_action = lambda *args: None
		
	def __iter__(self):
		'''Allows iteration over the object'''
		if self.buffer == X:
			for x in decRange(self.xStart, self.xStop, self.xStep):
				if self.iter_amount % self.buffer_every == 0:
					self.buffer_action()
				self.iter_amount += 1
				for y in decRange(self.yStart, self.yStop, self.yStep):
					yield (x, y)
		elif self.buffer == Y:
			for x in decRange(self.xStart, self.xStop, self.xStep):
				for y in decRange(self.yStart, self.yStop, self.yStep):
					if self.iter_amount % self.buffer_every == 0:
						self.buffer_action()
					self.iter_amount += 1
					yield (x, y)
		
class Pixel(object):
	'''Allows for pixels with specific attributes'''
	def __init__(self, x, y, color = 'black'):
		self.x, self.y = x, y
		self.color = color
		
	def plot(self, graph, color = None):
		'''Draws the pixel on the graph'''
		if color:
			if isinstance(graph, ComplexGraph):
				graph.plot(complex(self.x, self.y), color)
			else:
				graph.plot(self.x, self.y, color)
		else:
			if isinstance(graph, ComplexGraph):
				graph.plot(complex(self.x, self.y), self.color)
			else:
				graph.plot(self.x, self.y, self.color)
		
class Graph(GraphWin):
	'''Class to graph a function
	Accepts the following keyword arguments:
	width, height, autoflush, xMin, xMax, yMin, yMax, background'''
	def __init__(self, master = None, function = None, **options):
		if not master:
			master = tk.Tk()
		if function and not isinstance(function, Function):
			function = Function(function)
		self.master, self.function, self.options = master, function, options
		self.width, self.height, self.autoflush = self.options.get('width', 200), self.options.get('height', 200), self.options.get('autoflush', True)
		self.xMin, self.xMax, self.yMin, self.yMax = self.options.get('xMin', -100), self.options.get('xMax', 100), self.options.get('yMin', -100), self.options.get('yMax', 100)
		self.background, self.save_image = self.options.get('background', 'white'), self.options.get('save_image', None)
		self.update = self.options.get('update', lambda *args: None)
		GraphWin.__init__(self, self.master, self.width, self.height, self.autoflush, save_image = self.save_image)
		self.setBackground(self.background)
		self.graphed, self.axes_drawn, self.xAxis, self.yAxis, self.variables, self.axes_args, self.graph_args = False, False, None, None, {}, [], []
		self.defaultZoom = {'coords': [self.xMin, self.yMin, self.xMax, self.yMax], 'center': [0, 0]}
		self.setCoords(self.xMin, self.yMin, self.xMax, self.yMax)
		try:
			self.graph_dict = {'graph': self.graph, 'bifurcation': self.bifurcation, 'timeseries': self.timeseries, 'cobweb': self.cobweb, 'custom': None}
		except AttributeError:
			self.graph_dict = {'graph': self.graph}
		if self.function:
			try:
				self.graph()
			except (AttributeError, NameError, TypeError):
				pass
		
	def drawAxes(self, addLabels = True, lineLen = 0.2, interval = None, color = 'black'):
		'''Draws axes on the graph'''
		self.axes_args = [addLabels, lineLen, interval]
		x_pos = self.yMax - self.yMin
		y_pos = self.xMax - self.xMin
		drawAxis(self, Point(self.xMin, 0), Point(self.xMax, 0), addLabels, lineLen, interval if interval else y_pos / 10, type = 'x', color = color)
		drawAxis(self, Point(0, self.yMin), Point(0, self.yMax), addLabels, lineLen, interval if interval else x_pos / 10, type = 'y', color = color)
		self.axes_drawn = True
		
	def getMousePosition(self):
		'''Returns the (x, y) coordinate (in custom coordinates if the mouse is in the graph area) of the current mouse position'''
		x, y = self.winfo_pointerxy()
		if self.containsPixel(x, y, GLOBAL):
			return self.translate(x, y, GLOBAL)
		return x, y
		 
	def setCoords(self, x1, y1, x2, y2, default = False):
		'''Sets the coordinates of the main graph'''
		self.xMin, self.yMin, self.xMax, self.yMax = x1, y1, x2, y2
		GraphWin.setCoords(self, self.xMin, self.yMin, self.xMax, self.yMax)
		if default:
			self.defaultZoom['coords'] = [self.xMin, self.yMin, self.xMax, self.yMax]
			self.defaultZoom['center'] = self.getCenter()
		
	def findDistance(self, x1, y1, x2, y2):
		'''Finds the distance between two points'''
		return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
		
	def findDistancePoint(self, p1, p2):
		'''Finds the distance between two points on an axis'''
		return self.findDistance(p1, 0, p2, 0)
		
	def findDistanceAxis(self, axis = X):
		'''Finds the distance between the axisMax and the axisMin'''
		if axis == X:
			point_a, point_b = self.xMin, self.xMax
		else:
			point_a, point_b = self.yMin, self.yMax
		return abs(point_a - point_b)
		
	def translateLength(self, length, axis = X):
		'''Translates a pixel length into custom length'''
		ratio = self.findDistanceAxis(axis) / (self.width if axis == X else self.height)
		return ratio * length
		
	def resetZoom(self, redraw = False):
		'''Resets the zoom to the default, initial values'''
		coords = self.defaultZoom['coords']
		if redraw:
			self.setCoords(*coords)
			self.refresh()
		else:
			ratioX = self.findDistancePoint(coords[0], coords[2]) / self.findDistanceAxis(X)
			ratioY = self.findDistancePoint(coords[1], coords[3]) / self.findDistanceAxis(Y)
			self.zoom(ratioX ** -1, ratioY ** -1, *self.defaultZoom['center'])
	
	def zoom(self, ratioX = 1, ratioY = 1, centerX = None, centerY = None, scale = True):
		'''Zooms in or out on the graph (at a centered point) as a ratio of the current value'''
		center = self.translateCustom(*self.getCenter())
		newCenter = self.translateCustom(centerX, centerY)
		centerX, centerY = center[0] if centerX is None else centerX, center[1] if centerY is None else centerY
		xShift, yShift = abs(self.xMax - self.xMin), abs(self.yMax - self.yMin)
		xShiftPixel, yShiftPixel = (self.width - (ratioX + 1) * self.width / 2) - ratioX * (newCenter[0] - center[0]), (self.height - (ratioY + 1) * self.height / 2) - ratioY * (newCenter[1] - center[1])
		xMin, yMin = centerX - xShift / (ratioX * 2), centerY -  yShift / (ratioY * 2)
		xMax, yMax = centerX + xShift / (ratioX * 2), centerY + yShift / (ratioY * 2)
		self.setCoords(xMin, yMin, xMax, yMax)
		if scale:
			self.scale("all", 0, 0, ratioX, ratioY)
			self.move("all", xShiftPixel, yShiftPixel)
		else:
			self.refresh()
		
	def refresh(self, redrawGraph = True):
		'''Refreshes the graph - use if set new coords'''
		self.clear()
		if self.axes_drawn:
			self.drawAxes(*self.axes_args)
		if self.graphed and redrawGraph:
			if self.graph_dict['custom']:
				self.graph_dict['custom']()
			else:
				self.graph_dict[self.graphed](*self.graph_args[:-1], **self.graph_args[-1])
				self.update()
		
	def setCustomGraph(self, function):
		'''Sets the custom graphing function'''
		self.graph = function
		self.graph_dict['custom'] = function
		
	def getCenter(self):
		'''Gets the center of the graph, as a tuple object'''
		x_range, y_range = self.findDistanceAxis(X), self.findDistanceAxis(Y)
		half_x, half_y = x_range / 2, y_range / 2
		return (self.xMax - half_x, self.yMax - half_y)
	
	def __contains__(self, xy):
		'''Returns whether or not the (x, y) tuple pair (as custom coordinates) is in the graph bounds'''
		return self.contains(*xy)
		
	def contains(self, x, y):
		'''Returns whether or not the (x, y) pair (as custom coordinates) is in the graph bounds'''
		return (self.xMin <= x <= self.xMax) and (self.yMin <= y <= self.yMax)
	
	def containsPixel(self, x, y, mode = LOCAL):
		'''Returns whether or not the (x, y) pair (as pixel coordinates) is in the graph bounds'''
		if mode == GLOBAL:
			root_x = self.winfo_rootx()
			root_y = self.winfo_rooty()
			in_bound = (root_x <= x <= self.width + root_x) and (root_y <= y <= self.height + root_y)
		else:
			in_bound = (0 <= x <= self.width) and (0 <= y <= self.height)
		return in_bound
	
	def createVariable(self, *names):
		'''Creates the variable(s)'''
		for name in names:
			self.setVariable(name, 0)
	
	def setVariable(self, name, value = 0):
		'''Sets the variable to the value'''
		self.variables[name] = value
		try:
			self.function.setVariable(name, value)
		except AttributeError:
			pass
		
	def setMainVariable(self, name):
		'''Sets the main variable'''
		self.main_variable = name
		if name not in self.variables.keys():
			self.createVariable(name)
		
	def setFunction(self, function):
		'''Sets the main function'''
		if not isinstance(function, Function):
			function = Function(function)
		self.function = function
		
	def delVariable(self, *names):
		'''Deletes the variable(s)'''
		for name in names:
			del self.variables[name]
			try:
				self.function.delVariable(name)
			except AttributeError:
				pass
	
	def plot(self, x, y, color = 'black'):
		'''Plots a point on the graph'''
		if self.contains(x, y):
			GraphWin.plot(self, x, y, color)
	
	def plotPoint(self, x, y, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) at the given (x, y) coordinate'''
		if self.contains(x, y):
			if not radius:
				radius = (self.xMax - self.xMin) / ratio
			xLength = self.xMax - self.xMin
			yLength = self.yMax - self.yMin
			yAdjust = yLength / xLength
			yRadius = radius * yAdjust
			point = Oval(Point(x - radius, y - yRadius), Point(x + radius, y + yRadius))
			point.setOutline(color)
			point.setFill(color)
			point.draw(self)
			return point
	
	def evaluate(self):
		'''Returns the evaluation of the function'''
		return self.function.evaluate(**self.variables)
	
	def graph(self, function = None, values = [], **options):
		'''Graphs the function'''
		self.graph_args = [function, values, options]
		interval, color = options.get('interval', (self.xMax - self.xMin) / 1000), options.get('color', 'red')
		update_function, use_threading = options.get('update', lambda *args: None), options.get('thread', False)
		if function or (not self.function):
			if not isinstance(function, Function):
				function = Function(function)
			self.function = function
		if self.function:
			total = self.xMax - self.xMin
			if not values:
				values = decRange(self.xMin, self.xMax, interval)
				oldX = self.xMin
			else:
				oldX = values[0]
			self.setVariable(self.main_variable, oldX)
			oldY = self.function.evaluate(**self.variables)
			if use_threading:
				def thread_process():
					points = []
					for x in inter(values):
						self.setVariable(self.main_variable, x)
						y = self.function.evaluate(**self.variables)
						points.append([(x, y), (oldX, oldY)])
						oldX, oldY = x, y
					self.points = points
				thread = threading.Thread(target = thread_process, args = ())
				return thread
			for x in iter(values):
				try:
					self.setVariable(self.main_variable, x)
					y = self.function.evaluate(**self.variables)
					line = Line(Point(oldX, oldY), Point(x, y))
					line.setOutline(color)
					try:
						line.draw(self)
					except GraphicsError:
						break
					oldX, oldY = x, y
					update_function(x, y, x / total)
				except ZeroDivisionError:
					circle = Circle(Point(x, y), interval * 10)
					circle.setOutline(color)
					circle.draw(self)
			self.graphed = 'graph'

class ComplexGraph(Graph):
	'''Wrapper to the Graph class that allows for the graphing of Complex numbers'''
	def __contains__(self, z):
		'''Returns whether or not z is on the graph'''
		return self.contains(z.real, z.imag)
	
	def plot(self, z, color = 'red'):
		'''Plots a point (pixel) of the Cartesian coordinate (z.real, z.imaginary)'''
		Graph.plot(self, z.real, z.imag, color)
	
	def plotPoint(self, z, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) of the Cartesian coordinate (z.real, z.imaginary)'''
		x, y = z.real, z.imag
		Graph.plotPoint(self, x, y, color, radius, ratio)

	def plotPolarPoint(self, r, theta, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) at the given Polar coordinate (r, theta)'''
		Graph.plotPoint(self, r, theta, color, radius, ratio)
 
	def plotPolar(self, r, theta, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) as a Cartesian coordinate'''
		z = cmath.rect(r, theta)
		self.plotPoint(z, color, radius, ratio)

class PolynomialMap(Graph):
	'''Wrapper to the Graph class that adds additional methods for graphing Polynomial Mappings'''
	def cobweb(self, function = None, starting_value = None, iterations = 100, **options):
		'''Graphs the function as a cobweb diagram'''
		self.graph_args = [function, starting_value, iterations, options]
		color, fp_line_color = options.get('color', 'red'), options.get('fp_line_color', 'blue')
		update_function, use_threading = options.get('update', lambda *args: None), options.get('thread', False)
		if function or (not self.function):
			if not isinstance(function, Function):
				function = Function(function)
			self.function = function
		if self.function:
			fp_line = Line(Point(self.xMin, self.xMin), Point(self.xMax, self.xMax))
			fp_line.setOutline(fp_line_color)
			fp_line.draw(self)
			if not starting_value:
				starting_value = random.uniform(0, 1)
			n = starting_value
			if use_threading:
				def thread_process():
					points = []
					for iteration in xrange(iterations):
						starting_n = n
						self.setVariable(self.main_variable, n)
						n = self.function.evaluate(**self.variables)
						points.append([(starting_n, n), (starting_n, starting_n)])
					self.points = points
				thread = threading.Thread(target = thread_process, args = ())
				return thread
			for iteration in xrange(iterations):
				starting_n = n
				self.setVariable(self.main_variable, n)
				n = self.function.evaluate(**self.variables)
				line = Line(Point(starting_n, n), Point(starting_n, starting_n))
				line.setOutline(color)
				line.draw(self)
				second_line = Line(Point(starting_n, n), Point(n, n))
				second_line.setOutline(color)
				second_line.draw(self)
				update_function(starting_n, n, iteration / iterations)
			self.graphed = 'cobweb'
	
	def timeseries(self, function = None, starting_value = None, iterations = 1000, **options):
		'''Creates a time series graph of the function'''
		self.graph_args = [function, starting_value, iterations, options]
		interval, color = options.get('interval', (self.xMax - self.xMin) / 1000), options.get('color', 'red')
		update_function, use_threading = options.get('update', lambda *args: None), options.get('thread', False)
		if function or (not self.function):
			if not isinstance(function, Function):
				function = Function(function)
			self.function = function
		if self.function:
			if not starting_value:
				starting_value = random.uniform(0, 1)
			self.setVariable(self.main_variable, starting_value)
			x = starting_value
			if use_threading:
				def thread_process():
					points = []
					for iteration in xrange(iterations):
						starting_x = x
						self.setVariable(self.main_variable, x)
						x = self.function.evaluate(**self.variables)
						points.append((iteration, x))
					self.points = points
				thread = threading.Thread(target = thread_process, args = ())
				return thread
			points = []
			for iteration in xrange(iterations):
				try:
					starting_x = x
					self.setVariable(self.main_variable, x)
					x = self.function.evaluate(**self.variables)
					self.plotPoint(iteration, x, color)
					update_function(starting_x, x, iteration / iterations)
					points.append((iteration, x))
				except ZeroDivisionError:
					circle = Circle(Point(x, y), interval * 10)
					circle.setOutline(color)
					circle.draw(self)
			self.points = points
			self.graphed = 'timeseries'
	
	def bifurcation(self, function = None, **options):
		'''Creates the bifurcation diagram of the function'''
		self.graph_args = [function, options]
		roundoff, iter_variable, start, stop, iterations = options.get('roundoff', 5), options.get('iter_variable'), options.get('start', 0), options.get('stop', 4), options.get('iterations', 1000)
		max_period, transient_length, verify, color = options.get('max_period', 256),  options.get('transient_length', 1000), options.get('verify', lambda item:
	True), options.get('color', 'red')
		update_function, use_threading, update_amount = options.get('update', lambda *args: None), options.get('thread', False), options.get('autoflushUpdateRatio', 100)
		if function or (not self.function):
			if not isinstance(function, Function):
				function = Function(function)
			self.function = function
		if self.function:
			self.createVariable(iter_variable)
			total = stop - start
			offset = 0.5 if use_threading else 1
			def thread_process():
				points = []
				for value in decRange(start, stop, total / iterations):
					self.setVariable(iter_variable, value)
					x = random.uniform(0, 1)
					self.setVariable(self.main_variable, x)
					for iteration in xrange(transient_length):
						x = self.function.evaluate(**self.variables)
						self.setVariable(self.main_variable, x)
					values = []
					for iteration in xrange(max_period + 1):
						x = self.function.evaluate(**self.variables)
						self.setVariable(self.main_variable, x)
						values.append(x)
					values = map(lambda n: round(n, roundoff), values)
					toPlot = filter(verify, list(set(values)))
					for fixed_point in toPlot:
						points.append((value, fixed_point))
					update_function(0, 0, value * offset / total)
				self.points = points
				return points
			if use_threading: 
				thread = threading.Thread(target = thread_process, args = ())
				return thread
			else:
				points = thread_process()
				total = len(points)
				update_amount = int(total / update_amount)
				for n, point in enumerate(points, 1):
					x, y = point
					self.plot(x, y, color = color)
					update_function(0, 0, n * offset / total)
					if n % update_amount == 0 and not self.autoflush:
						self.update()
			self.graphed = 'bifurcation'
				
class GraphGroup:
	'''Creates multiple graphs with the same function'''
	def __init__(self, *graphs):
		for graph in graphs:
			if not isinstance(graph, Graph):
				raise TypeError("All graphs must be a Graph instance")
		self.graphs = list(graphs)
	
	def add(self, *graphs):
		'''Adds *graphs to self.graphs'''
		self.graphs.extend(list(graphs))

	def iter_graphs(self, function, *args, **kwargs):
		'''Internal function: calls the function, using the provided arguments, for every graph'''
		for graph in self.graphs:
			function(graph, *args, **kwargs)
	
	@staticmethod
	def create(number, master, function = None, **options):
		'''Creates 'number' of Graphs'''
		graphs = []
		for i in xrange(number):
			graphs.append(Graph(master, function, **options))
		return [GraphGroup(*graphs)] + graphs
	
	def grid(self, *args, **kwargs):
		'''Grids the graphs'''
		self.iter_graphs(Graph.grid, *args, **kwargs)
	
	def pack(self, *args, **kwargs):
		'''Packs the graphs'''
		self.iter_graphs(Graph.pack, *args, **kwargs)
	
	def setCoords(self, x1, y1, x2, y2, default = False):
		'''Sets the coordinates for the graphs'''
		self.iter_graphs(Graph.setCoords, x1, y1, x2, y2, default)
	
	def resetZoom(self):
		'''Resets the zoom for the graphs'''
		self.iter_graphs(Graph.resetZoom)
	
	def zoom(self, ratioX = None, ratioY = None):
		'''Changes the zoom for the graphs'''
		self.iter_graphs(Graph.zoom, ratioX, ratioY)
	
	def drawAxes(self, addLabels = True, lineLen = 0.2, interval = None, color = 'black'):
		'''Draws axes on the graphs'''
		self.iter_graphs(Graph.drawAxes, addLabels, lineLen, interval, color)
	
	def plot(self, x, y, color = 'red'):
		'''Plots a point at the (x, y) coordinate on the graphs'''
		self.iter_graphs(Graph.plot, x, y, color)
	
	def plotPoint(self, x, y, color = 'red', radius = None, ratio = 250):
		'''Plots a point (Circle) at the (x, y) coordinate on the graphs'''
		self.iter_graphs(Graph.plotPoint, x, y, color, radius, ratio)
	
	def setFunction(self, function):
		'''Sets the function for the graphs'''
		self.iter_graphs(Graph.setFunction, function)
	
	def createVariable(self, *names):
		'''Creates the variable(s) for the graphs'''
		self.iter_graphs(Graph.createVariable, *names)
	
	def setVariable(self, name, value = 0):
		'''Sets the variable to the value for the graphs'''
		self.iter_graphs(Graph.setVariable, name, value)
		
	def setMainVariable(self, name):
		'''Sets the main variable for the graphs'''
		self.iter_graphs(Graph.setMainVariable, name)
		
	def delVariable(self, *names):
		'''Deletes the variable(s) for the graphs'''
		self.iter_graphs(Graph.delVariable, *names)
			
	def graph(self, function = None, values = [], **options):
		'''Graphs the function on the graphs'''
		self.iter_graphs(Graph.graph, function, values, **options)
			
	def configure(self, *args, **kwargs):
		'''Configures the graphs'''
		self.iter_graphs(Graph.configure, *args, **kwargs)
		self.update()
			
	def update(self):
		'''Updates the graphs'''
		self.iter_graphs(Graph.update)
			
	def clear(self):
		'''Clears the graphs'''
		self.iter_graphs(Graph.clear)

class ComplexGraphGroup(GraphGroup):
	'''Adds functions to the GraphGroup class to make it compatible with ComplexGraph instances'''
	@staticmethod
	def create(number, master, function = None, **options):
			'''Creates 'number' of Complex Graphs'''
			graphs = [ComplexGraph(master, function, **options) for iteration in xrange(number)]
			return [ComplexGraphGroup(*graphs)] + graphs

	def plot(self, z, color = 'red'):
		'''Plots a point (pixel) of the Cartesian coordinate (z.real, z.imag) on the graphs'''
		self.iter_graphs(ComplexGraph.plot, z, color)
	
	def plotPoint(self, z, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) of the Cartesian coordinate (z.real, z.imaginary) on the graphs'''
		self.iter_graphs(ComplexGraph.plotPoint, z, color, radius, ratio)

	def plotPolar(self, r, theta, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) at the given Polar coordinate (r, theta) on the graphs'''
		self.iter_graphs(ComplexGraph.plotPolar, r, theta, color, radius, ratio)

	def plotPolarPoint(self, r, theta, color = 'red', radius = None, ratio = 250):
		'''Plots a point (circle) as a Cartesian coordinate on the graphs '''
		self.iter_graphs(ComplexGraph.plotPolarPoint, r, theta, color, radius, ratio)
		
class PolynomialMapGroup(GraphGroup):
	'''Adds functions to the GraphGroup class to make it compatible with PolynomialMap instances'''
	@staticmethod
	def create(number, master, function = None, **options):
		'''Creates 'number' of Polynomial Maps'''
		graphs = [PolynomialMap(master, function, **options) for iteration in xrange(number)]
		return [PolynomialMapGroup(*graphs)] + graphs
	
	def cobweb(self, function = None, starting_value = None, iterations = 100, **options):
		'''Creates the cobweb diagram for the Polynomial Maps'''
		self.iter_graphs(PolynomialMap.cobweb, function, starting_value, iterations, **options)
		
	def timeseries(self, function = None, starting_value = None, iterations = 1000, **options):
		'''Creates the time series graph for the Polynomial Maps'''
		self.iter_graphs(PolynomialMap.timeseries, function, starting_value, iterations, **options)
			
	def bifurcation(self, function = None, **options):
		'''Creates the bifurcation diagrams for the maps'''
		self.iter_graphs(PolynomialMap.bifurcation, function, **options)
		
class ColorScheme:
	'''Creates a color scheming method for Graphs'''
	def __init__(self, master):
		self.master = master
		self.current = None
		self.current_number = 0
		self.schemes = {}
		
	def addScheme(self, function, name = None):
		'''Adds a coloring scheme'''
		if not name: 
			self.current_number += 1
			name = self.current_number
		self.schemes[name] = function
		if not self.current:
			self.current = function
		
	def addSchemes(self, *schemes, **named_schemes):
		'''Adds schemes as a list [scheme1, scheme2, ...] or as a dictionary {name1: scheme1, name2: scheme2, ...}'''
		for scheme in schemes:
			self.addScheme(scheme)
		for name, scheme in named_schemes.items():
			self.addScheme(scheme, name)
		
	def setScheme(self, name):
		'''Sets the current scheme'''
		self.current = self.schemes[name]
		
	def getColor(self, *variables):
		'''Returns the color based on the current scheme'''
		return self.current(*variables)
			
### Additional Functions

def drawAxis(window, min_point, max_point, label = False, lineLen = None, interval = None, placePoint = None, type = 'x', color = 'black'):
	'''Creates an axis with optional labels
	window is a GraphWin object, the points are Point objects, and the label is a Boolean
	returns a Line object'''
	truncate = lambda s, length: s[:length]
	axis = Line(min_point, max_point)
	try:
		xLength, yLength = window.xMax - window.xMin, window.yMax - window.yMin
		yAdjust = yLength / xLength
		axis.setWidth(yAdjust)
	except AttributeError as e:
		pass
	axis.setOutline(color)
	axis.draw(window)
	if label:
		if type == 'x':
			xMin, xMax = min_point.getX(), max_point.getX()
		else:
			xMin, xMax = min_point.getY(), max_point.getY()
		if not interval:
			interval = (xMax - xMin) / 100
		if not lineLen:
			lineLen = window.height / 100
		if not placePoint:
			placePoint = 0 - (xMax - xMin) / 100
		axisLabels = []
		for n in decRange(xMin, xMax):
			line= Line(Point(n, -lineLen), Point(n, lineLen))
			line.setOutline(color)
			axisLabels.append(line)
			try: 
				if n % interval == 0:
					if type == 'x':
						text = Text(Point(n, placePoint), truncate(str(n), 5))
					else:
						text = Text(Point(placePoint, n), truncate(str(n), 5))
					text.setTextColor(color)
					axisLabels.append(text)
			except ZeroDivisionError:
				interval = 1
		drawAll(window, *axisLabels)
		axis.labels = axisLabels
	return axis
	
def decRange(start = 0, stop = 11, step = 1):
	'''Returns a generator of numbers from start [,stop, step]'''
	results, roundN = [], len(str(step)) - 2
	if roundN < 0:
		roundN = 0
	while start < stop:
		start += step
		yield round(start, roundN)

def planeIteration(xStart = 0, xStop = 0, xStep = 1, yStart = 0, yStop = 0, yStep = 1):
	'''Returns a generator of numbers on the plane'''
	for x in decRange(xStart, xStop, xStep):
		for y in decRange(yStart, yStop, yStep):
			yield (x, y)