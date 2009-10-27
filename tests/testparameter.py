#!/usr/bin/env python
"""Tests for refinableobj module."""

import unittest

from diffpy.srfit.fitbase.parameter import *

class TestParameter(unittest.TestCase):

    def testSetValue(self):
        """Test initialization."""
        l = Parameter("l")

        l.setValue(3.14)
        self.assertAlmostEqual(3.14, l.getValue())

        # Try array
        import numpy
        x = numpy.arange(0, 10, 0.1)
        l.setValue(x)
        self.assertTrue( l.getValue() is x )
        self.assertTrue( l.value is x )

        # Change the array
        y = numpy.arange(0, 10, 0.5)
        l.value = y
        self.assertTrue( l.getValue() is y )
        self.assertTrue( l.value is y )

        # Back to scalar
        l.setValue(1.01)
        self.assertAlmostEqual(1.01, l.getValue())
        self.assertAlmostEqual(1.01, l.value)
        return

class TestParameterProxy(unittest.TestCase):

    def testProxy(self):
        """Test the ParameterProxy class."""
        l = Parameter("l", 3.14)

        # Try Accessor adaptation
        la = ParameterProxy("l2", l)

        self.assertEqual("l2", la.name)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.value = 2.3
        self.assertEqual(l.getValue(), la.getValue())

        # Change the proxy
        la.value = 3.2
        self.assertEqual(l.getValue(), la.getValue())

        return

class TestParameterWrapper(unittest.TestCase):

    def testWrapper(self):
        """Test the adapter.

        This adapts a Parameter to the Parameter interface. :)
        """
        l = Parameter("l", 3.14)

        # Try Accessor adaptation
        la = ParameterWrapper("l", l, getter = Parameter.getValue, setter =
                Parameter.setValue)

        self.assertEqual(l.name, la.name)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.setValue(2.3)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the adapter
        la.setValue(3.2)
        self.assertEqual(l.getValue(), la.getValue())

        # Try Attribute adaptation
        la = ParameterWrapper("l", l, attr = "value")

        self.assertEqual(l.name, la.name)
        self.assertEqual("value", la.attr)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the parameter
        l.setValue(2.3)
        self.assertEqual(l.getValue(), la.getValue())

        # Change the adapter
        la.setValue(3.2)
        self.assertEqual(l.getValue(), la.getValue())

        return

if __name__ == "__main__":

    unittest.main()

