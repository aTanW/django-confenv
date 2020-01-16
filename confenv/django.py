#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# confenv/django.py - maintain program configuration in environment variables
#   with django-specific additions
# (c) 2019 Vitaly Protsko <me@protsko.expert>
# Licensed under GPLv3
#
# code is a rework of django-environ Copyright (c) 2013-2017, Daniele Faraglia
#

'''
confenv.django allows you to store application configuration in environment
variables, with optional initialization from named file.

'''

__all__ = ('Env', )

VERSION = '0.9.5'
__author__ = 'Vitaly Protsko'
__version__ = tuple(VERSION.split('.'))


#
# >> adopt to Django version

from pkgutil import find_loader

if not find_loader('django'):
  raise 'No django module found.'

from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ImproperlyConfigured

if DJANGO_VERSION < (2, 0):
  DJANGO_POSTGRES = 'django.db.backends.postgresql_psycopg2'
else:
  DJANGO_POSTGRES = 'django.db.backends.postgresql'

if find_loader('redis_cache'):
  DJANGO_REDIS = 'redis_cache.RedisCache'
else:
  DJANGO_REDIS = 'django_redis.cache.RedisCache'


#
# >> adopt to python version

from confenv import pyCompat

urlparselib, quote, unquote_plus = pyCompat

urlparse = urlparselib.urlparse
urlunparse = urlparselib.urlunparse
ParseResult = urlparselib.ParseResult
parse_qs = urlparselib.parse_qs


#
# >> main

from ast import literal_eval
from confenv import Env as BaseEnv

class Env(BaseEnv):

  # "public"
  exception = ImproperlyConfigured

  defenv_db = 'DATABASE_URL'
  defenv_cache = 'CACHE_URL'
  defenv_email = 'EMAIL_URL'
  defenv_search = 'SEARCH_URL'

  # "private"
  urltype = ParseResult

  driver_db = {
    'postgres': DJANGO_POSTGRES,
    'postgresql': DJANGO_POSTGRES,
    'psql': DJANGO_POSTGRES,
    'pgsql': DJANGO_POSTGRES,
    'postgis': 'django.contrib.gis.db.backends.postgis',
    'mysql': 'django.db.backends.mysql',
    'mysql2': 'django.db.backends.mysql',
    'mysql-connector': 'mysql.connector.django',
    'mysqlgis': 'django.contrib.gis.db.backends.mysql',
    'mssql': 'sql_server.pyodbc',
    'oracle': 'django.db.backends.oracle',
    'pyodbc': 'sql_server.pyodbc',
    'redshift': 'django_redshift_backend',
    'spatialite': 'django.contrib.gis.db.backends.spatialite',
    'sqlite': 'django.db.backends.sqlite3',
    'ldap': 'ldapdb.backends.ldap',
  }
  defopts_db = ['CONN_MAX_AGE', 'ATOMIC_REQUESTS', 'AUTOCOMMIT']

  driver_cache = {
    'dbcache': 'django.core.cache.backends.db.DatabaseCache',
    'dummycache': 'django.core.cache.backends.dummy.DummyCache',
    'filecache': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmemcache': 'django.core.cache.backends.locmem.LocMemCache',
    'memcache': 'django.core.cache.backends.memcached.MemcachedCache',
    'pymemcache': 'django.core.cache.backends.memcached.PyLibMCCache',
    'rediscache': DJANGO_REDIS,
    'redis': DJANGO_REDIS,
  }
  defopts_cache = ['TIMEOUT', 'KEY_PREFIX', 'VERSION', 'KEY_FUNCTION', 'BINARY']

  driver_email = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'smtp+tls': 'django.core.mail.backends.smtp.EmailBackend',
    'smtp+ssl': 'django.core.mail.backends.smtp.EmailBackend',
    'consolemail': 'django.core.mail.backends.console.EmailBackend',
    'filemail': 'django.core.mail.backends.filebased.EmailBackend',
    'memorymail': 'django.core.mail.backends.locmem.EmailBackend',
    'dummymail': 'django.core.mail.backends.dummy.EmailBackend'
  }
  defopts_email = ['EMAIL_USE_TLS', 'EMAIL_USE_SSL']

  driver_search = {
    "elasticsearch": "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
    "elasticsearch2": "haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine",
    "solr": "haystack.backends.solr_backend.SolrEngine",
    "whoosh": "haystack.backends.whoosh_backend.WhooshEngine",
    "xapian": "haystack.backends.xapian_backend.XapianEngine",
    "simple": "haystack.backends.simple_backend.SimpleEngine",
  }


  # >> constructor
  def __init__(self, **defaults):
    BaseEnv.__init__(self, **defaults)


  # >> "api"

  def db_url(self, var=defenv_db, default=BaseEnv.nodata, engine=None):
    """Returns a config dictionary, defaulting to DATABASE_URL.
    :rtype: dict
    """
    return self.genconf_db(self(var, default=default), engine=engine)
  db = db_url

  def cache_url(self, var=defenv_cache, default=BaseEnv.nodata, backend=None):
    """Returns a config dictionary, defaulting to CACHE_URL.
    :rtype: dict
    """
    return self.genconf_cache(self.url(var, default=default), backend=backend)
  cache = cache_url

  def email_url(self, var=defenv_email, default=BaseEnv.nodata, backend=None):
    """Returns a config dictionary, defaulting to EMAIL_URL.
    :rtype: dict
    """
    return self.genconf_email(self.url(var, default=default), backend=backend)
  email = email_url

  def search_url(self, var=defenv_search, default=BaseEnv.nodata, engine=None):
    """Returns a config dictionary, defaulting to SEARCH_URL.
    :rtype: dict
    """
    return self.genconf_search(self.url(var, default=default), engine=engine)
  search = search_url


  # >> service

  @staticmethod
  def _cast(value):
    try:
      return ast.literal_eval(value)
    except ValueError:
      return value

  @staticmethod
  def _cast_int(v):
    if hasattr(v, 'isdigit') and v.isdigit():
      return int(v)
    else:
      return v

  @staticmethod
  def _cast_urlstr(v):
    if isinstance(v, str):
      return unquote_plus(v)
    else:
      return v


  # >> library

  @classmethod
  def genconf_db(cls, url, engine=None):
    """Idea from DJ-Database-URL, parse an arbitrary Database URL.
    :param url:
    :param engine:
    :rtype: dict
    """

    if not isinstance(url, cls.urltype):
      # special case
      if url == 'sqlite://:memory:':
        return {'ENGINE': cls.driver_db['sqlite'], 'NAME': ':memory:'}

      url = urlparse(url)

    # remove query
    path = url.path[1:]
    path = unquote_plus(path.split('?', 2)[0])

    cName = path
    cHost = url.hostname
    cPort = cls._cast_int(url.port) if url.port else None

    if url.scheme == 'sqlite':
      cName = path or ':memory:'
      if url.netloc:
        from warnings import warn
        warn('SQLite URL contains host component ' + url.netloc + ', it will be ignored', stacklevel=3)

    elif url.scheme == 'ldap':
      cName = url.scheme + '://' + url.hostname
      if url.port:
        cName += ':' + url.port

    elif url.scheme == 'postgres' and path.startswith('/'):
      cHost, cName = path.rsplit('/', 1)

    elif url.scheme == 'oracle':
      if not path:
        cName = cHost
        cHost = None

      if cPort:
        cPort = url.port

    result = {
      'NAME': cName or '',
      'HOST': cHost or '',
      'USER': cls._cast_urlstr(url.username) or '',
      'PASSWORD': cls._cast_urlstr(url.password) or '',
    }

    if cPort:
      result['PORT'] = cPort

    if not engine:
      engine = url.scheme

    if not engine in cls.driver_db:
      from warnings import warn
      warn('Can not detect DB engine name from url')

    else:
      result['ENGINE'] = cls.driver_db[engine]

    if url.query:
      resopts = {}
      for key, val in parse_qs(url.query).items():
        ukey = key.upper()
        if ukey in cls.defopts_db:
          result[ukey] = cls._cast(val[0])
        else:
          resopts[key] = cls._cast_int(val[0])

      if len(resopts) > 0:
        result['OPTIONS'] = resopts

    return result


  @classmethod
  def genconf_cache(cls, url, backend=None):
    """Idea from DJ-Cache-URL, parse an arbitrary Cache URL.
    :param url:
    :param backend:
    :rtype: dict
    """
    url = urlparse(url) if not isinstance(url, cls.urltype) else url

    if url.scheme == 'filecache':
      cLoc = url.netloc + url.path

    elif url.scheme.startswith('redis'):
      if url.hostname:
        scheme = url.scheme.replace('cache', '')
      else:
        scheme = 'unix'
      _tmp = [scheme + '://' + loc + url.path for loc in url.netloc.split(',')]
      cLoc = _tmp[0] if len(_tmp) == 1 else _tmp

    elif url.path and url.scheme in ['memcache', 'pymemcache']:
      cLoc = 'unix:' + url.path

    else:
      cLoc = url.netloc.split(',')
      if len(cLoc) == 1:
        cLoc = cLoc[0]

    result = {
      'LOCATION': cLoc,
      'BACKEND': backend if backend else cls.driver_cache[url.scheme],
    }

    if url.query:
      resopts = {}
      for key, val in parse_qs(url.query).items():
        ukey = key.upper()
        if ukey in cls.defopts_cache:
          result[ukey] = cls._cast(val[0])
        else:
          resopts[ukey] = cls._cast(val[0])

      if len(resopts) > 0:
        result['OPTIONS'] = resopts

    return result


  @classmethod
  def genconf_email(cls, url, backend=None):
    """Parse an arbitrary e-mail URL.
    :param url:
    :param backend:
    :rtype: dict
    """
    url = urlparse(url) if not isinstance(url, cls.urltype) else url

    if not backend:
      if url.scheme in cls.driver_email:
        backend = cls.driver_email[url.scheme]
      else:
        raise cls.exception('Unknown e-mail scheme "' + url.scheme +'"')

    path = url.path[1:]
    path = unquote_plus(path.split('?', 2)[0])

    result = {
      'EMAIL_BACKEND': backend,
      'EMAIL_FILE_PATH': path,
      'EMAIL_HOST_USER': cls._cast_urlstr(url.username),
      'EMAIL_HOST_PASSWORD': cls._cast_urlstr(url.password),
      'EMAIL_HOST': url.hostname,
      'EMAIL_PORT': cls._cast_int(url.port),
    }

    if url.scheme in ('smtps', 'smtp+tls'):
      result['EMAIL_USE_TLS'] = True
    elif url.scheme == 'smtp+ssl':
      result['EMAIL_USE_SSL'] = True

    if url.query:
      resopts = {}
      for key, val in parse_qs(url.query).items():
        ukey = key.upper()
        if ukey in cls.defopts_email:
          result[ukey] = cls._cast(val[0])
        else:
          resopts[ukey] = cls._cast(val[0])

      if len(resopts) > 0:
        result['OPTIONS'] = resopts

    return result


  @classmethod
  def genconf_search(cls, url, engine=None):
    """Parse an arbitrary search URL.
    :param url:
    :param engine:
    :rtype: dict
    """
    url = urlparse(url) if not isinstance(url, cls.urltype) else url

    if url.scheme not in cls.driver_search:
      raise cls.exception('Unknown search scheme ' + url.scheme)

    result = {
      'ENGINE': engine if engine else cls.driver_search[url.scheme],
    }

    if url.query:
      resopts = parse_qs(url.query)
      if 'EXCLUDED_INDEXES' in resopts:
        result['EXCLUDED_INDEXES'] = resopts['EXCLUDED_INDEXES'][0].split(',')
      if 'INCLUDE_SPELLING' in resopts:
        result['INCLUDE_SPELLING'] = cls.parse_value(resopts['INCLUDE_SPELLING'][0], bool)
      if 'BATCH_SIZE' in resopts:
        result['BATCH_SIZE'] = cls.parse_value(resopts['BATCH_SIZE'][0], int)

    if url.scheme == 'simple':
      return result

    path = url.path[1:]
    path = unquote_plus(path.split('?', 2)[0])
    path = path.rstrip('/')

    if url.scheme == 'solr':
      result['URL'] = urlunparse(('http',) + url[1:2] + (path,) + ('', '', ''))

      if url.query:
        if 'KWARGS' in resopts:
          result['KWARGS'] = resopts['KWARGS'][0]
        if 'TIMEOUT' in resopts:
          result['TIMEOUT'] = cls.parse_value(resopts['TIMEOUT'][0], int)

      return result


    if url.scheme.startswith('elasticsearch'):
      _tmp = path.rsplit('/', 1)
      if len(_tmp) > 1:
        path = '/'.join(_tmp[:-1])
        index = _tmp[-1]
      else:
        path = ''
        index = _tmp[0]
      result['URL'] = urlunparse(('http',) + url[1:2] + (path,) + ('', '', ''))
      result['INDEX_NAME'] = index

      if url.query:
        if 'KWARGS' in resopts:
          result['KWARGS'] = resopts['KWARGS'][0]
        if 'TIMEOUT' in resopts:
          result['TIMEOUT'] = cls.parse_value(resopts['TIMEOUT'][0], int)

      return result

    result['PATH'] = '/' + path

    if url.query:
      if url.scheme == 'whoosh':
        if 'STORAGE' in resopts:
          result['STORAGE'] = resopts['STORAGE'][0]
        if 'POST_LIMIT' in resopts:
          result['POST_LIMIT'] = cls.parse_value(resopts['POST_LIMIT'][0], int)
      elif url.scheme == 'xapian':
        if 'FLAGS' in resopts:
          result['FLAGS'] = resopts['FLAGS'][0]

    return result


# >> init

def _addurlschemes(schemes):
  for method in dir(urlparselib):
    if method.startswith('uses_'):
      for item in schemes:
        getattr(urlparselib, method).append(item)

_addurlschemes(Env.driver_db.keys())
_addurlschemes(Env.driver_cache.keys())
_addurlschemes(Env.driver_email.keys())
_addurlschemes(Env.driver_search.keys())


# EOF confenv/django.py
