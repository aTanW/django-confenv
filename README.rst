
django-confenv
==============

**django-confenv** purpose - make django settings.py (or any other Python
project config) persistent, while real setup is done from file(s)
with simple "env=value" format or OS environment variables. Also, this
technics is known as `Twelve-factor methodology`_ or 12factor_ method.

NOTE, that, despite name, you can use django-confenv in *ANY* Python
project, without activating any django-related stuff.

**django-confenv** is heavily reconstructed version of django-environ_
by `Daniele Faraglia`_ and `other authors`_. Differences from that code are:

  - higher speed (sometimes much higher)
  - smaller code
  - smaller footprint
  - django-related stuff moved to module
  - more functionality in .env file(s) search/selection
  - some improvements/speedups in 'api'
  - separated basic tests for base and django functionality

**django-confenv** is (C) 2019,2020 Vitaly Protsko <me@protsko.expert>
Released under GPLv3. If you need this code under other license, please,
contact the author.


Quick usage
-----------

Get Env

.. code-block:: python

    # base functionality class
    from confenv import Env

for Django projects

.. code-block:: python

    # Env with django species
    from confenv.django import Env

Next, "configure" Env itself

.. code-block:: python

    # Set exception to be raised in case of error
    # For Django it is set to ImproperlyConfigured
    #Env.exception = Exception

    # Get default configuration file name from named
    #   environemt variable
    # Default: CONFENV_PROFILE
    Env.defconf_key = 'BIGPROJECT_CONFNAME'

    # Set env file name to be read, instead of name,
    #   defined in env var named in Env.defconf_key
    # filename + '.env' will also be checked, if
    #   file with plain filename not found
    # File will be searched in directory where calling
    #   Env class instantiation program resides if
    #   Env.filepath is None
    # Default: '.env'
    Env.filename = 'default.conf'

    # Search for file Env.filename or file '.env' in this
    #   path, if set.
    # If name in Env.filename is absolute, filepath will
    #   not be prepended (will be ignored).
    # If this file path is not absolute the directory where
    #   calling Env class instantiation program resides will
    #   be prepended.
    # Default: None
    Env.filepath = '..'

    # Set dict to operate on
    # Default: os.environ
    #Env.data = dict()


Collect all changeable values in file, parseable also by shell:

.. code-block:: sh

    #
    # default.conf
    #

    # put settings in environment variables
    DEBUG=1

    # you can use simple variable substitution. Remember, that
    #   this interpreter is not a shell. This works only if you
    #   start value from '$<varname>'. In that case variable
    #   will be substituted by value of the variable, found in
    #   previous asignments or in Env.data dictionary. Resolving
    #   recursion depth is not limited.
    CACHEDIR=$HOME/.cache


You can define
  type and default value for parameters you use in you project by
  defining a "scheme" directly as parameters, or as a dictionary.
  For example, to define variable DEBUG as boolean parameter with
  default 'False' value, you can use either form:

.. code-block:: python

    # directly in parameters
    env = Env(DEBUG=(bool, False), CACHEDIR=(str, ))

    # or as a prepared list of kwargs:
    kwl = {
      'DEBUG': (bool, False),
      'CACHEDIR': (str, ),
    }

    env = Env(**kwl)


Full list of supported types you can find later in this file.

.. code-block:: python

    # now use it in your program

    # WARNING:
    #   If you dont pass the default value to converter
    #   or miss it in Env class's parameters ("schema"),
    #   Env will require the variable to exist in OS
    #   environment (precisely, in Env.data dict),
    #   otherwise Env.exception will be thrown.

    # this will assign True to variable debug, if
    #   environment variable DEBUG value in
    #   ('true', 'on', 'ok', 'y', 'yes', 'yea', '1')
    #   Other value or variable absence will assign
    #   False value.
    DEBUG = env('DEBUG')

    # you can directly point Env to conversion you
    #   need to be done with value of env var by
    #   calling corresponding method directly
    SERVER = env.url('SERVER', 'http://www.example.com')

    # this will assign instance of ParseResult from
    #   urllib.parse with pre-parsed URL, for the default
    #   value in example above it will be
    #   ParseResult(scheme='http', netloc='www.example.com', path='', params='', query='', fragment='')
    #
    #   NB: all other conversions return expected type,
    #     not an instance of side class

    # use substituted var, but back it with default value
    CACHE = env('CACHEDIR', '/var/cache')

    # complex json is also not a problem
    PARAMS = env.json('PARAMETERS', "{'par1':'val1', 'par2': {'def': 1, 'set': 2}, 'par3': [1, 2]}")

    # this will assign default dictionary to
    #   variable PARAMS if PARAMETERS is absent in
    #   env file or in OS environment variables


Supported types
---------------

Here is all supported data types collected in example
.env file and code to use it in your programs.

.. code-block:: sh

    #
    # myappconf.env
    #

    # NB: Quotes for us are optional, value counted
    #   from character after the equal sign, except
    #   when surrounded by quotes, in which case
    #   they are stripped.
    #   There is limitation: variable assignments
    #   must be written in one line. Continuations
    #   are not supported.

    # bool variable, accepting values
    #   true on ok y yes yea 1
    #   as True, any other value as False.
    #   You can use "export" keyword before variable
    #   name and maintain one place of configuration
    #   for application and accompanying shell scripts
    export DEBUG=no

    # str variable
    #   Any sequence of characters. This is effectively
    #   the same, as unicode type, look below for
    #   declaration example(s)
    SERVERNAME="Our service server"

    # bytes variable
    #   Sequence of any characters, that can be
    #   decoded by .encode('utf8') method. Or you can
    #   pass encoding directly to convertor method
    #   with parameter: env.bytes('VAR', encoding='utf16')
    WELCOMEMSG=Добро пожаловать!

    # integer variable
    PORT=1234

    # float variable
    MAXAVGLOAD=5.5

    # list variable
    LISTENIP=127.0.0.1,192.168.1.1,10.0.0.1

    # tuple variable
    #   value type in this case will be str
    ENDPOINTS=(start,read,calculate,write,stop)

    # dict variable #1
    #   In this case all values are strings and
    #   here is no need to declare "schema" for
    #   this variant.
    USERACL=root=admin,jdoe=operator,john=user

    # dict variable #2
    #   This dictionary variant needs declaration
    #   to properly convert values, it can be done
    #   in Env class instantiation parameters.
    COEFFICIENT=a=10.11;b=5;result=unknown

    # json variable
    #   This type can be used for complex setup
    #   of something (like menu) or for any other
    #   kind of structured (initialization?) data.
    MENUEXTRA={"ExtraItem1": {"display": "&Cook Coffee", "handler": "cooker", "allow": "ALL"}}

    # url variable
    #   This can be used for pointing to any kind
    #   of resources, allowed schemes are as in
    #   urllib.
    EXTLOGO=http://image.bigproject.com/biglogo.jpg


There is additional convertors for django applications.
  They pesent only in Env, imported from confenv.django
  module.

.. code-block:: sh

    #
    # djangosite.env
    #

    # Database URL
    #   This variable value can be parsed as database
    #   configuration for django project. Env will
    #   automatically select appropriate django driver
    #   for database type pointed by url scheme.
    #   Recognized schemes are:
    #     postgres, postgresql, pgsql, postgis, mysql,
    #     mysql2, mysql-connector, mysqlgis, mssql, oracle,
    #     pyodbc, redshift, spatialite, sqlite, ldap
    MAINDB_URL=pgsql://dbuser:dbpass@db.example.com:5432/bigproject?AUTOCOMMIT=True

    # Cache URL
    #   You can point django to cache resource(-s) as url
    #   Recognized schemes are:
    #     dbcache, dummycache, filecache, locmemcache,
    #     memcache, pymemcache, rediscache, redis
    CACHE_URL=locmemcache://
    MEMCACHE_URL=memcache://localhost:12345

    # E-Mail URL
    #   Django's e-mail submitting parameters
    #   Recognized schemes are:
    #     smtp, smtps, smtp+tls, smtp+ssl, consolemail,
    #     filemail, memorymail, dummymail
    MAINMAIL=smtp+tls://senduser:accesspw@mta.example.com:587

    # Search URL
    #   This otional feature uses drivers from django-haystack
    #   to find that needle.
    #   Recognized schemes are:
    #     elasticsearch, elasticsearch2, solr, whoosh,
    #     xapian, simple
    SEARCHENGINE=solr://search.example.com:8983/solr/bigproject?q=*.*


You can use all power of Env without any types declarations.
  Env instance has methods for direct variable conversion.
  But, I'm shure, you want stricter value type definitions,
  that gives more chances in bug hunting.
  Also, you always can use direct call to instance to get
  plain value backed by default.

NB: Here is nuance with naming variable type in declarations
  and in call to convertors. Types from this list:

    str, bool, int, float, list, tuple, dict

  you can point directly, as they are build-in and this
  identifiers are known for interpreter. Types

    url, json, unicode, bytes

  you can use only by quoting their names, as shown below.
  Althrough, you can quote names of all types, including ones from
  first list, if you do not remember well which ones are built-in.
  ;-)

.. code-block:: python

    from confenv import Env
    Env.filename = 'myappconf'

    kwl = {
      # if you dont give default value, you can get an exception
      #   from Env in case if variable not present in Env.data
      'DEBUG': (bool, False),

      # you can completely omit declaration of variables
      #   with str value type - it is default
      #'SERVERNAME': (str, ),
      #   or, which is equivalent, you can declare it as
      'SERVERNAME': ('unicode', ),

      # we'll comment out this declaration to demonstrate direct
      #   convertor calls later
      #'WELCOMEMSG': ('bytes', 'Welcome !'),

      'PORT': (int, ),
      'MAXAVGLOAD': (float, ),

      # quoted type name also works
      'LISTENIP': ('list', ),

      # items for this tuple are of type str
      'ENDPOINTS': (tuple, ),

      # default type of values str
      'USERACL': (dict, {'ALL': 'deny'} ),

      # default value type is str
      'COEFFICIENT': ({'value': str, 'cast': {'a': float, 'b': int} }, {'result': 'NaN'}),

      'MENUEXTRA': ('json', ),
      'EXTLOGO': ('url', ),
    }

    env = Env(**kwl)

    # store values from environment in program configuration items
    #

    flagDebug = env('DEBUG')
    # assigned value bool False

    textServer = env('SERVERNAME', 'Default service')
    # assigned value str 'Our service server'

    # in-line conversion
    textWelcome = env.bytes('WELCOMEMSG', 'Welcome !')
    # assigned value str 'Добро пожаловать!'

    paramPort = env('PORT', 4321)
    # assigned value int 1234

    paramLoad = env('MAXAVGLOAD', 10.0)
    # assigned value float 5.5

    paramListen = env('LISTENIP', [ '0.0.0.0' ])
    # assigned value [ '127.0.0.1', '192.168.1.1', '10.0.0.1' ]

    progServices = env('ENDPOINTS', ('start', 'stop'))
    # assigned value tuple('start', 'read', 'calculate', 'write', 'stop')

    paramACL = env('USERACL')
    # assigned value {'root': 'admin', 'jdoe': 'operator', 'john': 'user'}

    paramMUL = env('COEFFICIENT')
    # assigned value { 'a': 10.11, 'b': 5, 'result': 'unknown' }

    menuExtra = env('MENUEXTRA')
    # assigned value { 'ExtraItem1': { 'display': '&Cook Coffee', 'handler': 'cooker', 'allow': 'ALL' } }

    urlLogo = env('EXTLOGO')
    # assigned value ParseResult(scheme='http', netloc='image.bigproject.com', path='/biglogo.jpg', params='', query='', fragment='')


For django project settings.py Env can generate complete configuration
dictionaries for database, cache, e-mail and search functions to include
it into standard django config structures.

.. code-block:: python

    # settings.py
    #
    # This file can be "static", all changeable information
    # resides in ../myappconf.env and ../djangosite.env

    # get django-specific Env
    from confenv.django import Env

    # set path to .env's to directory, where manage.py reside
    Env.filepath = '..'

    # expecting, that you place example .env files 'myappconf'
    # and 'djangosite' in appropriate dir
    Env.filename = 'myappconf'

    # django Env's version have place to hold variable names
    # to read database, cache, e-mail and search URLs default
    # values from
    # They are class members with this default values:
    #Env.defenv_db = 'DATABASE_URL'
    #Env.defenv_cache = 'CACHE_URL'
    #Env.defenv_email = 'EMAIL_URL'
    #Env.defenv_search = 'SEARCH_URL'

    # search for database config here by default
    Env.defenv_db = 'MAINDB_URL'

    env = Env()

    # load additional configuration
    env.readfile(filename='djangosite')

    DEBUG = env.bool('DEBUG', True)

    # ...

    # databases config
    DATABASES = {
      # config will be read from MAINDB_URL
      'default': env.db_url(),
    }

    CACHES = {
      # this cache config will be read from CACHE_URL
      'default': env.cache_url(),

      # second cache config
      'quick': env.cache('MEMCACHE_URL'),
    }

    # This will require MAINMAIL key to be existent
    #   in Env.data dict
    EMAIL_CONFIG = env.email_url('MAINMAIL')
    vars().update(EMAIL_CONFIG)

    # django's search extension
    HAYSTACK_CONNECTIONS = {
      'default': env.search_url('SEARCHENGINE', 'simple://'),
    }


Installation
------------

This package can be installed from standard Python packages
source pypi.org

.. code-block:: sh

    pip install django-confenv


Credits
-------

This code is (c) Vitaly Protsko <me@protsko.expert>, under GPLv3.

This work is based on django-environ_ (c) `Daniele Faraglia`_
which includes work from `other authors`_ .

.. _12factor: http://www.12factor.net/
.. _`Twelve-factor methodology`: http://www.12factor.net/
.. _django-environ: https://github.com/joke2k/django-environ
.. _`Daniele Faraglia`: https://daniele.faraglia.info
.. _`other authors`: https://github.com/joke2k/django-environ/blob/develop/AUTHORS.rst
