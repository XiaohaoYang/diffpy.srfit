#!/usr/bin/env python
# FIXME - need printing

class Visitor(object):
    """Abstract class for all visitors to a tree of nodes.

    See implemented visitors for examples of use.

    """

    def onParameter(self, obj):
        """Process an Argument node."""
        raise NotImplementedError

    def onOperator(self, obj):
        """Process an Operator node."""
        raise NotImplementedError

    def onContainer(self, obj):
        """Process a Container node."""
        raise NotImplementedError

# End class Visitor

class FilterGetter(Visitor):
    """Get nodes according to a filter."""

    def __init__(self, filt):
        self.filt = filt
        self.vals = set()
        return

    def onParameter(self, obj):
        if self.filt(obj):
            self.vals.add(obj)
        if obj._constraint is not None:
            obj._constraint._identify(self)
        return

    def onOperator(self, obj):
        if self.filt(obj):
            self.vals.add(obj)
        for arg in obj._args:
            arg._identify(self)
        for arg in obj._kw.values():
            arg._identify(self)
        return

    def onContainer(self, obj):
        if self.filt(obj):
            self.vals.add(obj)
        for arg in obj.adapters:
            arg._identify(self)
        return

# End class FilterGetter

def _identity(obj):
    return True

class ParameterGetter(Visitor):
    """Get parameters from a tree of nodes, with an optional filter."""

    def __init__(self, filt = None):
        self.filt = filt
        if self.filt is None:
            self.filt = _identity
        self.vals = set()
        return

    def onParameter(self, obj):
        if self.filt(obj):
            self.vals.add(obj)
        if obj._constraint is not None:
            obj._constraint._identify(self)
        return

    def onOperator(self, obj):
        for arg in obj._args:
            arg._identify(self)
        for arg in obj._kw.values():
            arg._identify(self)
        return

    def onContainer(self, obj):
        for arg in obj.adapters:
            arg._identify(self)
        return

# End class ParameterGetter

class NodeFinder(Visitor):
    """Find a node within a tree of nodes.

    After operating on a tree, the 'found' attribute will indicate whether the
    node was found in the tree.
    
    """

    def __init__(self, node):
        """Initialize the finder.

        node    --  The node to find.

        """
        self._node = node
        self.found = False
        return

    def onParameter(self, obj):
        if obj is self._node: self.found = True
        if self.found: return
        if obj._constraint is not None:
            obj._constraint._identify(self)
        return

    def onOperator(self, obj):
        if obj is self._node: self.found = True
        if self.found: return
        for arg in obj._args:
            arg._identify(self)
        for arg in obj._kw.values():
            arg._identify(self)
        return

    def onContainer(self, obj):
        if obj is self._node: self.found = True
        if self.found: return
        for arg in obj.adapters:
            arg._identify(self)
        return

# End class NodeFinder

from diffpy.srfit.adapters import nodes
class Printer(Visitor):
    """Printer for printing a tree of nodes.

    Attributes:
    output  --  The output generated by the printer.

    """

    _infix = { 
            nodes.add : "+",
            nodes.subtract : "-",
            nodes.multiply : "*",
            nodes.divide : "/",
            nodes.power : "**",
            }
    _unary = {
            nodes.negative : "-",
            }

    def __init__(self):
        """Initialize."""
        self.reset()
        return

    def reset(self):
        """Reset the output string."""
        self.output = ""
        return

    def onParameter(self, obj):
        if obj.name is None or obj.name.startswith("_"):
            self.output += str(obj.value)
        else:
            self.output += str(obj.name)
        return

    def onContainer(self, obj):
        self.onParameter(obj)
        return

    def onOperator(self, obj):
        instr = self.output
        self.output = ""

        # Deal with infix and unary operations
        if obj._unbound in self.__class__._infix:
            self._onInfix(obj)
        elif obj._unbound in self.__class__._unary:
            self._onUnary(obj)
        else:
            instr += str(obj.name)
            numargs = 0
            for arg in obj._args:
                if numargs != 0: self.output += ", "
                arg._identify(self)
                numargs += 1
            for kw, arg in obj._kw.items():
                if numargs != 0: self.output += ", %s = "%kw
                arg._identify(self)

        if not (self.output.startswith("(") and self.output.endswith(")")):
            self.output = "(%s)"%self.output
        self.output = instr + self.output
        return

    def _onInfix(self, op):
        """Process infix operators."""
        symbol = self.__class__._infix[op._unbound]
        op._args[0]._identify(self)
        self.output += " %s "%symbol
        op._args[1]._identify(self)
        return

    def _onUnary(self, op):
        """Process unary operators."""
        symbol = self.__class__._unary[op._unbound]
        self.output += symbol
        op._args[0]._identify(self)
        return
