# setup.py
# Rushy Panchal
# v1.0

from distutils.core import setup
import distutils.command.bdist as bdist
import shutil
import os

def main():
	'''Sets up tk'''
	long_description = '''This is an extension for Tkinter, written purely in Python.
	It supports both Python 2.7 and Python 3.3.
	It includes additional classes, widgets, and graphical tools.'''

	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Object Oriented',
		'Topic :: Software Development :: User Interfaces ',
		'License :: OSI-Approved Open Source :: GNU General Public License version 3.0 (GPLv3)',
		'License :: OSI Approved :: Python Software Foundation License',
		'Intended Audience :: by End-User Class :: Developers',
		'Operating System :: Grouping and Descriptive Categories :: OS Independent (Written in an interpreted language)',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Programming Language :: Tcl',
		'User Interface :: Grouping and Descriptive Categories (UI) :: Project is a graphics toolkit ',
		'User Interface :: Toolkits/Libraries :: Tk',
		]

	setup_options = {
		'name': 'tk',
		'version': '1.0',
		'description': 'Graphics package that supplements native Tkinter',
		'long_description': long_description,
		'author': 'Rushy Panchal',
		'author_email': 'panchr@d-e.org',
		'packages': ['tk', 'tk.latex'],
		'url': "https://sourceforge.net/projects/python-tkinter-extra/",
		'license': 'General Public License version 3.0',
		'classifiers': classifiers,
		'package_data': {'': ['README.txt', 'gpl-3.0.txt']},
		'include_package_data': True,
		}

	try:
		shutil.rmtree('tk')
	except (IOError, WindowsError):
		pass
	shutil.copytree('.', 'tk')
		
	setup(**setup_options)