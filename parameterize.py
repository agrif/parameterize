import threading
import collections
import weakref
import contextlib

class Environment(collections.MutableMapping):
    """A dictionary-like object with scoping semantics."""
    def __init__(self, d, parent=None):
        self._parent = parent
        self._data = d
    
    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        if self._parent is not None:
            return self._parent[key]
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        if key in self._data or self._parent is None:
            self._data[key] = value
        else:
            self._parent[key] = value
    
    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
        elif self._parent is not None:
            del self._parent[key]
        else:
            raise KeyError(key)
    
    def __iter__(self):
        for k in self._data:
            yield k
        if self._parent is not None:
            for k in self._parent:
                if k not in self._data:
                    yield k
    
    def __len__(self):
        return len(list(iter(self)))

# default to using thread-locals for our execution context local storage
# and use it to store the current dynamic environment
_context_local = threading.local()
# the global environment uses weak key refs, so that when parameters
# are destroyed, their global entries are removed
_context_local.dynamic_environment = Environment(weakref.WeakKeyDictionary())

def set_context_locals(ctx):
    """Sets the context-local storage object used by parameterize. It
    should be an object with settable attributes with
    execution-context-dependent values. The default implementation
    uses threading.local().
    """
    global _context_local
    ctx.dynamic_environment = _context_local.dynamic_environment
    _context_local = ctx

class EnvironmentProxy(collections.MutableMapping):
    """A dictionary-like object that proxies the current dynamic
    environment, and provides a way to create a sub-environment via
    create().
    """
    def __getitem__(self, key):
        return _context_local.dynamic_environment[key]
    def __setitem__(self, key, value):
        _context_local.dynamic_environment[key] = value
    def __delitem__(self, key):
        del _context_local.dynamic_environment[key]
    def __iter__(self):
        return iter(_context_local.dynamic_environment)
    def __len__(self):
        return len(_context_local.dynamic_environment)
    
    @contextlib.contextmanager
    def create(self, data):
        """Use this context manager to execute code inside a new dynamic
        environment, inheriting from the current one. The argument
        should be a dictionary mapping keys to their values, which
        will be used to seed the new environment.
        """
        oldenv = _context_local.dynamic_environment
        newenv = Environment(data, parent=oldenv)
        _context_local.dynamic_environment = newenv
        try:
            yield
        finally:
            _context_local.dynamic_environment = oldenv

# our entry point to the dynamic environment from here on out
dynamic_environment = EnvironmentProxy()

class ParameterProxy(object):
    """An object that forwards attribute lookups to a parameterized
    value. You can create one of these with param.proxy().

    """
    def __init__(self, p):
        self.p = p
    
    def __getattr__(self, name):
        return getattr(self.p.get(), name)

class Parameter(object):
    """A parameter object, represeting a binding location in the dynamic
    environment. You can use p.get() to get the current value, or
    p.set(v) to set it. Also available are p() and p(v) to get and
    set, respectively. You can use the p.parameterize(v) context
    manager to execute code in a sub-environment where p has been set
    to v, and where all changes to the value of p cannot escape the
    code block.
    """
    def __init__(self, default=None, converter=lambda x: x):
        """Create a new parameter object, with the given default value and
        converter. The converter will be called every time the
        parameter is set.
        """
        dynamic_environment[self] = converter(default)
        self._converter = converter
    
    def get(self):
        """Get the parameter value."""
        return dynamic_environment[self]
    
    def set(self, value):
        """Set the parameter value."""
        dynamic_environment[self] = self._converter(value)
    
    def __call__(self, *args):
        """Provides the p() and p(v) shortcuts for get() and set(v)."""
        if len(args) == 0:
            return self.get()
        elif len(args) == 1:
            return self.set(args[0])
        else:
            # 1 or 2 since self counts as an argument
            raise TypeError("__call__() requires either 1 or 2 arguments")
    
    def proxy(self):
        """Return a proxy object that forwards all attribute accessors to the
        value of this parameter.
        """
        return ParameterProxy(self)
    
    @contextlib.contextmanager
    def parameterize(self, value):
        """This context manager runs its code block inside a dynamic
        environment where the parameter has been set to value. Changes
        to this parameter cannot escape the code block.
        """
        with dynamic_environment.create({self: self._converter(value)}):
            yield
