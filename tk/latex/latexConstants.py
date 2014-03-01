# coding=utf-8
# tk/latex/latexConstants.py
# Rushy Panchal
# v1.0

'''Provides the constants that are used in the various tk.latex modules.
Not intended to be imported directly. Instead, import tk.latex.'''

try: from Tkconstants import *
except ImportError: from tkinter.constants import *

### Regex Constants
DOTALL = 16
I = 2
IGNORECASE = 2
L = 4
LOCALE = 4
M = 8
MULTILINE = 8
S = 16
U = 32
UNICODE = 32
VERBOSE = 64
X = 64

### Mathematical Symbols

PLUS_OR_MINUS = u'±'
LESS_OR_EQUAL = u'≤'
GREATER_OR_EQUAL = u'≥'
EQUAL = '='
NOT_EQUAL = u'≠'
APPROXIMATE = u'≈'

### Greek Letters
ALPHA = u'Α'
LOWER_ALPHA = u'α'
BETA = u'Β'
LOWER_BETA = u'β'
GAMMA = u'Γ '
LOWER_GAMMA = u'γ'
DELTA = u'Δ'
LOWER_DELTA = u'δ'
EPSILON = u'Ε'
LOWER_EPSILON = u'ε'
ZETA = u'Ζ'
LOWER_ZETA = u'ζ'
ETA = u'Η'
LOWER_ETA = u'η'
THETA = u'Θ'
LOWER_THETA = u'θ'
IOTA = u'Ι'
LOWER_IOTA = u'ι'
KAPPA = u'Κ'
LOWER_KAPPA = u'κ'
LAMBDA = u'Λ'
LOWER_LAMBDA = u'λ'
MU = u'Μ'
LOWER_MU = u'μ'
NU = u'Ν'
LOWER_NU = u'ν'
XI = u'Ξ'
LOWER_XI = u'ξ'
OMICRON = u'Ο'
LOWER_OMICRON = u'ο'
PI = u'Π'
LOWER_PI = u'π'
RHO = u'Ρ'
LOWER_RHO = u'ρ'
SIGMA = u'Σ'
LOWER_SIGMA = u'σ'
TAU = u'Τ'
LOWER_TAU = u'τ'
UPSILON = u'Υ'
LOWER_UPSILON = u'υ'
PHI = u'Φ'
LOWER_PHI = u'φ'
CHI = u'Χ'
LOWER_CHI = u'χ'
PSI = u'Ψ'
LOWER_PSI = u'ψ'
OMEGA = u'Ω'
LOWER_OMEGA = u'ω'
