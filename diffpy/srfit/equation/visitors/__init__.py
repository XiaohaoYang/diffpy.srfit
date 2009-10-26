########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Visitors that perform on Literal trees.

Visitors are designed to traverse and extract infromation from Literal trees
(diffpy.srfit.equation.literals). Visitors are useful for validating, printing
and extracting Argument literals from the Literal tree.

The Literal-Visitor relationship is that described by the Visitor pattern
(http://en.wikipedia.org/wiki/Visitor_pattern).

"""

# package version
from diffpy.srfit.version import __version__

from .argfinder import ArgFinder
from .printer import Printer
from .validator import Validator
from .swapper import Swapper

def getArgs(literal, getconsts = True):
    """Get the Arguments of a Literal tree.

    getconsts   --  If True (default), then Arguments designated as constant
                    are also retrieved.

    Returns a list of Arguments searched for depth-first.
    
    """
    v = ArgFinder(getconsts)
    return literal.identify(v)

def prettyPrint(literal):
    """Print a Literal tree."""
    v = Printer()
    print literal.identify(v)
    return

def validate(literal):
    """Validate a Literal tree.

    Raises ValueError if the tree contains errors.

    """
    v = Validator()
    errors = literal.identify(v)
    if errors:
        m = "Errors found in Literal tree '%s'\n"%literal
        m += "\n".join(errors)
        raise ValueError(m)
    return

def swap(literal, oldlit, newlit):
    """Swap one literal for another in a Literal tree.

    Corrections are done in-place unless literal is oldlit, in which case the
    return value is newlit.

    Returns the literal tree with oldlit swapped for newlit.

    """

    if literal is oldlit:
        return newlit

    v = Swapper(oldlit, newlit)
    literal.identify(v)

    return literal

