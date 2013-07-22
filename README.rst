=======
Rmock
=======

The ``rmock`` is a python library for writing server mocks, with API inspired by `mock <http://www.voidspace.org.uk/python/mock/>`_ package.
It`s designed to be used mainly in unit and functional testing.
Http, memcache, smtp and pop3 protocols are implemented now, more will come out later.

Installation
============
You should clone project repo and run **python setup.py install** in main directory.

Dependencies
============
Library was tested on python2.7 under Linux systems.

Examples
========
Here`s a basic usage example. More will be added later, you can also look into tests directory.

.. code:: python

	>>> import rmock
	>>> import urllib2
	>>> http_mock = rmock.run("http", port=37666)
	>>> http_mock
	rmock(name= runner=http(port=37666 slug=))
	>>> http_mock.function.return_value = "function result"
	>>> url = 'http://localhost:37666/function?param=value'
	>>> result = urllib2.urlopen(url).read()
	>>> result
	'function result'
	>>> assert result == "function result"
	>>> http_mock.function.calls
	[call(funcname=function args=() kwargs={'param': 'value'})]
	>>> http_mock.function.assert_called_with(param='value')

Testing
============
Tests use `nose <http://somethingaboutorange.com/mrl/projects/nose/>`_ and are located in *tests* directory.
Before running them dependencies should be installed.
They are stored in *tests/requirements.txt*, in format suitable for **pip install -r** command.

Documentation
=============
More detailed documentation will come out in near future.
For now, tests are self-documenting and could be good source of usage examples.

