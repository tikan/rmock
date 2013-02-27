=======
Rmock
=======

remote (server) mocks library

Installation
============
You should clone project repo and run **python setup.py install** in main directory.

Dependencies
============
Library was tested on python2.7/unix systems.

Examples
========
Here`s a basic usage example. More will be added later, you can also see look into tests directory.

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
Tests use `nose <http://somethingaboutorange.com/mrl/projects/nose/>` and are located in tests directory.
Before running tests dependecies should be installed, using **pip install -r requirements.txt**

