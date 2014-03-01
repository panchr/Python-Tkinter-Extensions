# coding=utf-8
# tk/latex/LatexText.py
# Rushy Panchal
# v1.0

'''Provides the main Text wrapper for Tkinter Latex displays'''

try: from Tkinter import *
except ImportError: from tkinter import *
import re
from tk.latex import *
from latexConstants import *

subscript_pattern = re.compile("<sub>(.+)</sub>", IGNORECASE)
superscript_pattern = re.compile("<sup>(.+)</sup>", IGNORECASE)
division_pattern = re.compile("<num>(.+)</num><div>(.+)</div>", IGNORECASE)

class LatexText(Text):
	'''Latex-type display of Text'''
	def __init__(self, master = None, cnf = {},*args, **kwargs):
		Text.__init__(self, master, cnf, *args, **kwargs)
		self.text = None
		self.tag_configure("subscript", offset = -4)
		self.tag_configure("superscript", offset = 4)
		# create the appropiate tags - for Fractions, have it multiline in smaller font size OR use subscripts for numerator and superscripts for denominator?
	
	def insert(self, index, text):
		'''Inserts the selected text in Latex-format at the given index'''
		if not isinstance(text, CompiledLatex):
			text = Latex(text).compile()
		self.text = text
		for match in subscript_pattern.finditer(self.text):
			if match:
				self.insertSubscript(match.start(), match.group(1))
		for match in superscript_pattern.finditer(self.text):
			if match:
				self.insertSuperscript(match.start(), match.group(1))
		# have to find method for Fractions
		
	def insertSubscript(self, index, text):
		'''Internal method - Inserts text as a subscript at the given index'''
		Text.insert(self, index, text, "subscript")
		
	def insertSuperscript(self, index, text):
		'''Internal method - Inserts text as a superscript at the given index'''
		Text.insert(self, index, text, "superscript")
		
	def insertFraction(self, index, num, denom):
		'''Internal method - inserts a Fraction (of numerator/denominator at the given index'''
		pass