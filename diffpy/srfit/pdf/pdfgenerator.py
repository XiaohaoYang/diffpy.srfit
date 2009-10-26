#!/usr/bin/env python
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
"""PDF profile generator.

The PDFGenerator class can take a diffpy.Structure of
pyobjcryst.crystal.Crystal object and calculate the crystal PDF from it. The
passed structure object is wrapped in a StructureParameter set, which makes its
attributes refinable. See the class definition for more details and the
examples for its use.

"""

import numpy

from diffpy.srfit.fitbase import ProfileGenerator
from diffpy.srfit.fitbase.parameter import ParameterWrapper
from diffpy.srfit.structure import struToParameterSet
from diffpy.srreal.pdf_ext import PDFCalculator

# FIXME - Parameter creation will have to be smarter once deeper calculator
# configuration is enabled.
# FIXME - Need to decouple the non-structural parameters from the
# diffpy.Structure object, otherwise, we can't share the structural
# ParameterSet between different Generators.

__all__ = ["PDFGenerator"]

class PDFGenerator(ProfileGenerator):
    """A class for calculating the PDF from a single crystal structure.

    This works with diffpy.Structure.Structure and pyobjcryst.crystal.Crystal
    instances. Note that the managed Parameters are not created until the
    structure is added.

    Attributes:
    _calc   --  PDFCalculator instance for calculating the PDF
    _phase  --  The structure ParameterSets used to calculate the profile.
    _lastr  --  The last value of r over which the PDF was calculated. This is
                used to configure the calculator when r changes.

    Managed Parameters:
    scale   --  Scale factor
    delta1  --  Linear peak broadening term
    delta2  --  Quadratic peak broadening term
    qbroad  --  Resolution peak broadening term
    qdamp   --  Resolution peak dampening term

    Managed ParameterSets:
    The structure ParameterSet (BaseStructure instance) used to calculate the
    profile is named by the user.

    Usable Metadata:
    stype   --  The scattering type "X" for x-ray, "N" for neutron (see
                'setScatteringType').
    qmax    --  The maximum scattering vector used to generate the PDF (see
                setQmax).
    scale   --  See Managed Parameters.
    delta1  --  See Managed Parameters.
    delta2  --  See Managed Parameters.
    qbroad  --  See Managed Parameters.
    qdamp   --  See Managed Parameters.



    """

    def __init__(self, name = "pdf"):
        """Initialize the generator.
        
        """
        ProfileGenerator.__init__(self, name)

        self._calc = PDFCalculator()
        self.setScatteringType("N")
        self.setQmax(0.0)

        self._phase = None

        self.meta = {}

        # The last value of r we evaluated over
        self._lastr = None

        return

    def processMetaData(self):
        """Process the metadata once it gets set."""
        ProfileGenerator.processMetaData(self)
        stype = self.meta.get("stype")
        if stype is not None:
            self.setScatteringType(stype)

        qmax = self.meta.get("qmax")
        if qmax is not None:
            self.setQmax(qmax)

        parnames = ['delta1', 'delta2', 'qbroad', 'qdamp']

        for name in parnames:
            val = self.meta.get(name)
            if val is not None:
                par = self.get(name)
                par.setValue(val)

        scale = self.meta.get('scale')
        if scale is not None:
            self.scale.setValue(scale)

        return

    def setScatteringType(self, type = "X"):
        """Set the scattering type.
        
        type    --   "X" for x-ray or "N" for neutron

        Raises ValueError if type is not "X" or "N"

        """
        type = type.upper()
        if type not in ("X", "N"):
            raise ValueError("Unknown scattering type '%s'"%type)

        self.meta["stype"] = type

        self._calc.setScatteringFactorTable(type)

        return
    
    def getScatteringType(self):
        """Get the scattering type. See 'setScatteringType'."""
        return self._calc.getRadiationType()

    def setQmax(self, qmax):
        """Set the qmax value."""
        self._calc._setDoubleAttr("qmax", qmax)
        self.meta["qmax"] = qmax
        return

    def getQmax(self):
        """Get the qmax value."""
        self._calc._getDoubleAttr("qmax")
        return

    def setQmin(self, qmin):
        """Set the qmin value.

        This has no effect on the crystal PDF.
        
        """
        self._calc._setDoubleAttr("qmin", qmin)
        self.meta["qmin"] = qmin
        return

    def getQmin(self):
        """Get the qmin value."""
        self._calc._getDoubleAttr("qmin")
        return

    def setPhase(self, stru = None, name = None, parset = None):
        """Add a phase to the calculated structure.

        This creates a StructureParSet or ObjCrystParSet that adapts stru to a
        ParameterSet interface. See those classes (located in
        diffpy.srfit.structure) for how they are used. The resulting
        ParameterSet will be managed by this generator.

        stru    --  diffpy.Structure.Structure or pyobjcryst.crystal.Crystal
                    instance. Default None.
        name    --  A name to give the structure. If name is None (default),
                    then the name will be set as "phase".
        parset  --  A ParameterSet that hoolds the structural information. This
                    can be used to share the phase between multiple
                    PDFGenerators, and have the changes in one reflect in
                    another. If both stru and parset are specified, only parset
                    is used. Default None. 

        Raises ValueError if neither stru nor parset is specified.

        """

        if name is None:
            name = "phase"

        if stru is None and parset is None:
            raise ValueError("One of stru or parset must be specified")

        if parset is None:
            parset = struToParameterSet(stru, name)

        self._phase = parset

        # Check if the structure is a diffpy.Structure.PDFFitStructure
        # instance.
        from diffpy.Structure import Structure
        if isinstance(stru, Structure) and hasattr(stru, "pdffit"):
            self.__wrapPDFFitPars()
        else:
            self.__wrapPars()

        # Put this ParameterSet in the ProfileGenerator.
        self.addParameterSet(parset)
        return

    def __wrapPars(self):
        """Wrap the Parameters.

        This wraps the parameters provided by the PDFCalculator as SrFit
        Parameters.

        """
        parnames = ['delta1', 'delta2', 'qbroad', 'scale', 'qdamp']

        for pname in parnames:
            getter = self._calc.__class__._getDoubleAttr
            setter = self._calc.__class__._setDoubleAttr
            self.addParameter(
                ParameterWrapper(pname, self._calc, getter, setter, pname)
                )
        return

    def __wrapPDFFitPars(self):
        """Wrap the Parameters in a pdffit-aware structure.

        This wraps the parameters provided in a pdffit-aware diffpy.Structure
        object. The DiffpyStructureAdapter (customPQConfig) looks to the
        structure for the parameter values, so we must modify them at that
        level, rather than at the PDFCalculator level. This is an inconsistency
        that should probably be fixed.

        """
        pdfparnames = ['delta1', 'delta2', 'scale']

        for pname in pdfparnames:
            getter = dict.__getitem__
            setter = dict.__setitem__
            self.addParameter(
                ParameterWrapper(pname, self._phase.stru.pdffit, getter,
                    setter, pname)
                )

        parnames = ['qbroad', 'qdamp']
        for pname in parnames:
            getter = self._calc.__class__._getDoubleAttr
            setter = self._calc.__class__._setDoubleAttr
            self.addParameter(
                ParameterWrapper(pname, self._calc, getter, setter)
                )

        return


    def __prepare(self, r):
        """Prepare the calculator when a new r-value is passed."""
        # TODO - Should we handle non-uniform data?
        self._lastr = r
        self._calc._setDoubleAttr('rstep', r[1] - r[0])
        self._calc._setDoubleAttr('rmin', r[0])
        precision = self._calc._getDoubleAttr("peakprecision")
        self._calc._setDoubleAttr('rmax', r[-1] + precision)
        return

    def __call__(self, r):
        """Calculate the PDF.

        This ProfileGenerator will be used in a fit equation that will be
        optimized to fit some data.  By the time this function is evaluated,
        the crystal has been updated by the optimizer via the ObjCrystParSet
        created in setCrystal. Thus, we need only call pdf with the internal
        structure object.

        """
        if r is not self._lastr:
            self.__prepare(r)

        self._calc.eval(self._phase.stru)

        return self._calc.getPDF()

# End class PDFGenerator
