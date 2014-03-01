# coding=utf-8
# tk/latex/ttkLatexText.py
# Rushy Panchal
# v1.0

'''Provides the main Text wrapper for ttk Latex displays'''

try:
	from Tkinter import *
	from ttk import *
except ImportError:
	from tkinter import *
	from tkinter.ttk import *
	
import re
