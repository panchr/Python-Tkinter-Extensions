# coding=utf-8
# tk/latex/Symbols.py
# Rushy Panchal
# v1.0

'''Provides the main basis of the text-processing part of the latex subpackage.
Not intended to be imported directly. Instead, import tk.latex.'''

from latexConstants import *
import re

### Main classes

class Replace:
	'''Internal class for Regex substitutions'''
	def __init__(self, pattern, replacement, *flags):
		self.pattern = re.compile(pattern, *flags)
		self.replacement = replacement
	
	def __call__(self, string):
		'''Returns the replaced string'''
		return self.pattern.sub(self.replacement, string)

class SimpleReplace:
	'''Internal class for String substitutions'''
	def __init__(self, replacement, *patterns):
		self.patterns = patterns
		self.replacement = replacement

	def __call__(self, text):
		'''Returns the replaced string'''
		new_text = text
		for pattern in self.patterns:
			new_text = new_text.replace(pattern, self.replacement)
		return new_text

class BaseSymbol:
	'''Internal base class for all Symbols'''
	def compile(self, text):
		'''Returns tk.LatexText readable text'''
		return self.replacer(text)

	def __call__(self, text):
		'''Returns the replaced string'''
		return self.compile(text)

class MathematicalSymbol(BaseSymbol):
	'''Main class for mathematical symbols'''
	def __init__(self, symbol, *commands):
		self.replacer = SimpleReplace(symbol, *commands)
		
class GreekLetter(BaseSymbol):
	'''Main class for Greek Letters'''
	def __init__(self, symbol, *commands):
		self.replacer = SimpleReplace(symbol, *commands)
