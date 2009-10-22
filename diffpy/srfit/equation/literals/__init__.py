
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
"""Building blocks for defining a state-aware equation

Literals are the building blocks for equations. Literals are composed into
equation trees (or Literal trees) that can be evaluated or have other actions
performed on them by Visitors (in diffpy.srfit.equation.visitors). The
Literal-Visitor relationship is that described by the Visitor pattern
(http://en.wikipedia.org/wiki/Visitor_pattern).

The simplest Literal is the Argument, which holds the name and value of a
equation variable.  Operators are Literals that are used to compose other
Literals. Once an Operator is evaluated, it has a value that it can pass to
other operators. Hence, a network or tree of Literals can be composed that
evaluate as an equation. 

"""

# package version
from diffpy.srfit.version import __version__

# Import the operators

from .argument import Argument
from .operators import Operator
from .operators import AdditionOperator
from .operators import SubtractionOperator
from .operators import MultiplicationOperator
from .operators import DivisionOperator
from .operators import ExponentiationOperator
from .operators import RemainderOperator
from .operators import NegationOperator
from .operators import ConvolutionOperator
from .operators import UFuncOperator

# Try some optimizations on these classes
try:
    import psyco
    psyco.profile()
except ImportError:
    pass
