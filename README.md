parameterize
============

*a Python implementation of [SRFI 39][]*

 [SRFI 39]: http://srfi.schemers.org/srfi-39/srfi-39.html
 
[![Build Status](https://travis-ci.org/agrif/parameterize.svg)](https://travis-ci.org/agrif/parameterize)

*parameterize* implements optional dynamic scope and parameter objects
in Python. It's a spiritual implementation of parameters from Scheme,
as outlined in [SRFI 39][]. If you know what that means, awesome! If
not, read on.

### Requirements

*parameterize* should work, by itself, on Python 2.7 or later
 (including Python 3).

Parameter Objects
-----------------

Basically, parameter objects hold a single value. They are meant to be
declared as global variables, so that the values they contain can be
accessed anywhere. However, parameter objects have a neat trick: they
have a context manager, `parameterize()`, that lets you override the
parameter's value for a single piece of code. Any changes to the
parameter that happen within this code block can't escape it, and
can't affect other threads of execution.

So, parameters are sort of halfway between global variables and local
variables. They're accessable from anywhere, and modifiable from
anywhere, but modifications are always contained completely within
their `parameterize()` block.

Motivating Example
------------------

In Python, the `sys.stdout` global variable can be overridden to point to any file-like object to redirect output from built-in output primitives like `print()`. So, there's a nice hacky way to redirect the output of a function:

~~~~{.py}
with open('output.txt', 'w') as f:
    oldstdout = sys.stdout
    sys.stdout = f
	something_that_prints_a_lot()
	sys.stdout = oldstdout
~~~~

This is definitely a hack, though. It can be made a little bit nicer
by wrapping the replacement code into a context manager, but it's hard
to write a context manager that works for any variable like this (what
if we wanted to redirect `sys.stderr` instead?). Also, this has issues
with threading: if another thread tries to write to `stdout` while
`something_that_prints_a_lot()` is running, it'll end up in
`output.txt`.

*parameterize* and Parameter objects solve all these little problems
 for you. All we need to do is create an `stdout` parameter (with the
 initial value of `sys.stdout`), and replace `sys.stdout` with a proxy
 object that always points to the value of this parameter:

~~~~{.py}
import parameterize
import sys

# create our parameter and proxy object
stdoutp = parameterize.Parameter(sys.stdout)
sys.stdout = stdoutp.proxy()

print('before')
with open('output.txt', 'w') as f:
    with stdoutp.parameterize(f):
	    print('inside')
print('after')
~~~~

This code will print "before" and "after" to the console, and "inside"
to `output.txt`. The mutation of `sys.stdout` only appears within the
`with stdoutp.parameterize` block, and plays nicely with other
threads.

This sort of pattern (where there's some global context that affects
possibly deeply-nested functions, without passing this context through
the call chain) is also very common in web frameworks, where code
handling a response needs access to the request data, but may not have
been passed it directly. Werkzeug calls them
[context locals][werkzeug], and Flask calls it an
[application context][flask]. *parameterize* is a stand-alone way to
do this outside of these frameworks.

 [werkzeug]: http://werkzeug.pocoo.org/docs/local/
 [flask]: http://flask.pocoo.org/docs/appcontext/#app-context

Incidentally, the above example about replacing `sys.stdout` with a
parameter is exactly how R7RS Scheme handles IO redirection.

API
---

*parameterize* is a small module. To create a parameter object, use
 `Parameter(default, converter)`. `default` sets the initial value,
 and defaults to `None` when not provided. `converter` is a function
 that is called whenever the parameter is set, and should return a
 validated or converted value. If `converter` is not supplied, it
 defaults to doing nothing.

Parameter objects have a `get()` method, and a `set(v)` method, to get
and set the value contained by the object. As a convenience, if you
have a parameter object `p`, `p()` is the same as `p.get()`, and
`p(v)` is the same as `p.set(v)`.

Parameter objects also have `parameterize(v)`, a context manager that
sets the parameter to `v` within its block, and prevents all changes
to the parameter within that block from escaping. This is *the big
deal* about *parameterize*, and what seperates parameters from normal
global variables.

If the parameter value is an object, you can call `proxy()` to get an
object that will act like the object contained within the parameter,
and track any changes made to that value. This proxying mechanism is a
work in progress, and is probably more magic than you need. Still, it
is useful sometimes. Patches *very* welcome.

License
-------

*parameterize* is distributed under the MIT License. See `LICENSE.txt`
for details.
