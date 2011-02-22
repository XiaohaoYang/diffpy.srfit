#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2011 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Function for restraining the value of an equation."""

__all__ = ["restrain"]

def restrain(eq, lb, ub = None, sig = 1):
    """Restrain an equation between bounds.

    The output is a restraint equation that is meant to be passed to residual.

    eq  --  A node whose value to restrain. This must evaluate to a scalar.
    lb  --  The lower bound on the value of eq (float or Node). 
    ub  --  The upper bound on the value of eq (float or Node). If ub is None,
            then it is set equal to lb.
    sig --  Uncertainty on the bounds (float or Node).

    Returns the vector restraint equation:
    resv = max(0, lb - val, val - ub)/sig

    """
    from diffpy.srfit.fit.functions import maximum_
    if ub is None: ub = lb
    resv = maximum_(lb - eq, maximum_(0, eq - ub)) / sig
    resv.name = "restraint"
    return resv

__id__ = "$Id$"
