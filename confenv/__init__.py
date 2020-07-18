#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# confenv/__init__.py - maintain program configuration in environment variables
# (c) 2019 Vitaly Protsko <me@protsko.expert>
# Licensed under GPLv3
#
# code is a rework of django-environ Copyright (c) 2013-2017, Daniele Faraglia
#

'''
confenv allows you to store application configuration in environment
variables, with optional initialization from named file.

'''

__all__ = ('Env', 'Path', 'pyCompat', )

VERSION = '1.0.0'
__author__ = 'Vitaly Protsko'
__version__ = tuple(VERSION.split('.'))


#
# >> imports

import os
from collections.abc import Iterable


#
# >> compatibility

from sys import version_info as pyVersion

if pyVersion[0] == 2:
  import urlparse as urlparselib
  from urllib import quote, unquote_plus

elif pyVersion[0] == 3:
  import urllib.parse as urlparselib
  quote = urlparselib.quote
  unquote_plus = urlparselib.unquote_plus
  basestring = str

urlparse = urlparselib.urlparse
urlunparse = urlparselib.urlunparse
ParseResult = urlparselib.ParseResult
parse_qs = urlparselib.parse_qs

pyCompat = (urlparselib, quote, unquote_plus, )


#
# >> "library"

from pkgutil import find_loader

if find_loader('simplejson'):
  import simplejson as json
else:
  import json


#
# >> subroutine

# Impossibly overengeneered piece of code, program in the name of the program.
# Keeping it here only for compatibility.

class Path(object):

  # "public"
  exception = Exception

  # >>
  @staticmethod
  def _absolute_join(base, *paths, **kwargs):
    absolute_path = os.path.abspath(os.path.join(base, *paths))
    if kwargs.get('required', False) and not os.path.exists(absolute_path):
      raise exception("Create required path: " + absolute_path)
    return absolute_path


  def __init__(self, start='', *paths, **kwargs):
    super(Path, self).__init__()

    if kwargs.get('is_file', False):
      start = os.path.dirname(start)

    self.__root__ = self._absolute_join(start, *paths, **kwargs)


  # >> "api"
  def __call__(self, *paths, **kwargs):
    """Retrieve the absolute path, with appended paths
    :param paths: List of sub path of self.root
    :param kwargs: required=False
    """
    return self._absolute_join(self.__root__, *paths, **kwargs)

  @property
  def root(self):
    'Current directory for this Path'
    return self.__root__

  def path(self, *paths, **kwargs):
    """Create new Path based on self.root and provided paths.
    :param paths: List of sub paths
    :param kwargs: required=False
    :rtype: Path
    """
    return self.__class__(self.__root__, *paths, **kwargs)

  def file(self, name, *args, **kwargs):
    """Open a file.
    :param name: Filename appended to self.root
    :param args: passed to open()
    :param kwargs: passed to open()
    :rtype: file
    """
    return open(self(name), *args, **kwargs)

  def __getitem__(self, *args, **kwargs):
    return self.__str__().__getitem__(*args, **kwargs)

  def __eq__(self, other):
    return self.__root__ == other.__root__

  def __ne__(self, other):
    return not self.__eq__(other)

  def __add__(self, other):
    return Path(self.__root__, other if not isinstance(other, Path) else other.__root__)

  def __sub__(self, other):
    if isinstance(other, int):
      return self.path('../' * other)

    elif isinstance(other, basestring):
      if self.__root__.endswith(other):
        return Path(self.__root__.rstrip(other))

    raise TypeError(
      "unsupported operand type(s) for '{self}' and '{other}' "
      "unless value of {self} ends with value of {other}".format(
        self=type(self), other=type(other)
      )
    )

  def __invert__(self):
    return self.path('..')

  def __contains__(self, item):
    base_path = self.__root__
    if len(base_path) > 1:
      base_path = os.path.join(base_path, '')
    return item.__root__.startswith(base_path)

  def rfind(self, *args, **kwargs):
    return self.__str__().rfind(*args, **kwargs)

  def find(self, *args, **kwargs):
    return self.__str__().find(*args, **kwargs)


  def __repr__(self):
    return "<Path: " + self.__root__ + ">"

  def __str__(self):
    return self.__root__

  def __unicode__(self):
    return self.__str__()

  __fspath__ = __str__


#
# >> main

class NoValue(object):
  def __repr__(self):
    return '<' + self.__class__.__name__ + '>'


class Env(object):

  # "public"
  exception = Exception
  data = os.environ
  defconf_key = 'CONFENV_PROFILE'
  filename = None
  filepath = None

  # "private"
  nodata = NoValue()
  truestr = ('true', 'on', 'ok', 'y', 'yes', 'yea', '1') 


  def __init__(self, **defaults):
    for item in ('defconf_key', 'filepath', 'filename'):
      if item in defaults:
        setattr(Env, item, defaults[item])
        del defaults[item]

    self.defaults = defaults
    self.readfile()

    setattr(self, 'keys', Env.data.keys)
    setattr(self, 'values', Env.data.values)
    setattr(self, 'items', Env.data.items)
    setattr(self, '__iter__', Env.data.__iter__)


  def __contains__(self, var):
    return var in self.data


  def __getattr__(self, key):
    if key in self.data: return self(key)
    return object.__getattr__(self, key)

  def __setattr__(self, key, val):
    if key in self.data:
      self.data[key] = val
    else:
      object.__setattr__(self, key, val)

  def __getitem__(self, key):
    return self(key)

  def __setitem__(self, key, val):
    self.data[key] = val


  def __call__(self, var, cast=None, default=nodata, parse_default=False):
    """Return value for given environment variable.

    :param var: Name of variable.
    :param cast: Type to cast return value as.
    :param default: If var not present in environ, return this instead.
    :param parse_default: force to parse default..

    :returns: Value from environment or default (if set)
    """

    isDefault = False
    if var in self.defaults:
      scheme = self.defaults[var]

      if isinstance(scheme, Iterable):
        if not cast: cast = scheme[0]

        if default is self.nodata and len(scheme) > 1:
          default = scheme[1]

      else:
        if not cast: cast = scheme

    try:
      result = self.data[var]

    except KeyError:
      if default is self.nodata:
        _msg  = 'Environment variable "' + var + '" is not set, but required.'
        raise self.exception(_msg)
      result = default
      isDefault = True

    if hasattr(result, 'startswith') and result.startswith('$'):
      ix=1
      ln = len(result)
      while ix < ln and result[ix].isidentifier():
        ix += 1
      result = self(result[1:ix], cast=cast, default=default if not isDefault else self.nodata) + result[ix:]

    if cast is None and default is not None and not isinstance(default, NoValue):
      cast = type(default)

    if isinstance(cast, str):
      if   cast == 'url':     cast = urlparse
      elif cast == 'json':    cast = json.loads
      elif cast == 'unicode': cast = str
      elif cast == 'bytes':   cast = str
      elif cast == 'str':     cast = str
      elif cast == 'bool':    cast = bool
      elif cast == 'int':     cast = int
      elif cast == 'float':   cast = float
      elif cast == 'list':    cast = list
      elif cast == 'tuple':   cast = tuple
      elif cast == 'dict':    cast = dict

    if result != default or (parse_default and result):
      result = self.parse_value(result, cast)

    return result

  get_value = __call__


  def str(self, var, default=nodata, multiline=False):
    """
    :rtype: str
    """
    value = self(var, default=default)
    if multiline:
      return value.replace('\\n', '\n')
    return value

  def unicode(self, var, default=nodata):
    """ python2 helper
    :rtype: unicode
    """
    return self(var, cast=str, default=default)

  def bytes(self, var, default=nodata, encoding='utf8'):
    """
    :rtype: bytes
    """
    return self(var, cast=str, default=default).encode(encoding)

  def bool(self, var, default=nodata):
    """
    :rtype: bool
    """
    return self(var, cast=bool, default=default)

  def int(self, var, default=nodata):
    """
    :rtype: int
    """
    return self(var, cast=int, default=default)

  def float(self, var, default=nodata):
    """
    :rtype: float
    """
    return self(var, cast=float, default=default)

  def json(self, var, default=nodata):
    """
    :returns: Json parsed
    """
    return self(var, cast=json.loads, default=default)

  def list(self, var, cast=None, default=nodata):
    """
    :rtype: list
    """
    return self(var, cast=list if not cast else (cast,), default=default)

  def tuple(self, var, cast=None, default=nodata):
    """
    :rtype: tuple
    """
    return self(var, cast=tuple if not cast else (cast,), default=default)

  def dict(self, var, cast=dict, default=nodata):
    """
    :rtype: dict
    """
    return self(var, cast=cast, default=default)

  def url(self, var, default=nodata):
    """
    :rtype: urlparse.ParseResult
    """
    return self(var, cast=urlparse, default=default, parse_default=True)

  def path(self, var, default=nodata, **kwargs):
    """
    :rtype: Path
    """
    return Path(self(var, default=default), **kwargs)


  @classmethod
  def parse_value(cls, value, cast):
    """Parse and cast provided value
    :param value: Stringed value.
    :param cast: Type to cast return value as.
    :returns: Casted value
    """

    if cast is None:
      return value

    elif cast is bool:
      try:
        result = int(value) != 0
      except ValueError:
        result = value.lower() in cls.truestr

    elif isinstance(cast, list):
      result = list(map(cast[0], [x for x in value.split(',') if x]))

    elif isinstance(cast, tuple):
      _prep = value.lstrip('(').rstrip(')').split(',')
      result = tuple(map(cast[0], [x for x in _prep if x]))

    elif isinstance(cast, dict):
      _castKey = cast.get('key', str)
      _castVal = cast.get('value', str)
      _castKeyVal = cast.get('cast', dict())

      result = dict(map(
        lambda keyval: (
          _castKey(keyval[0]),
          cls.parse_value(keyval[1], _castKeyVal.get(keyval[0], _castVal))
        ),
        [x.split('=') for x in value.split(';') if x]
      ))

    elif cast is list:
      result = [x for x in value.split(',') if x]

    elif cast is tuple:
      _prep = value.lstrip('(').rstrip(')').split(',')
      result = tuple([x for x in _prep if x])

    elif cast is dict:
      result = dict([x.split('=') for x in value.split(',') if x])

    elif cast is float:
      _prep = value.replace(' ', '').replace(',', '')
      result = float(_prep)

    else:
      result = cast(value)

    return result


  @classmethod
  def readfile(cls, filename=None):

    if not filename:
      if not cls.filename:
        if cls.defconf_key in cls.data:
          filename = cls.data[cls.defconf_key]
        else:
          filename = '.env'

      else:
        filename = cls.filename

    if not os.path.isabs(filename):
      if cls.filepath:
        filename = os.path.join(cls.filepath, filename)

    if not os.path.isabs(filename):
      # look for calling program path
      from sys import _getframe

      fn = os.path.dirname(_getframe(0).f_code.co_filename)
      bn = mymod = os.path.basename(fn)

      for i in range(1, 4):
        fn = os.path.dirname(_getframe(i).f_code.co_filename)
        bn = os.path.basename(fn)
        if not bn == mymod: break

      if not bn == mymod:
        filename = os.path.abspath(os.path.join(fn, filename))

      # otherwise use provided relative path

    if not os.access(filename, os.R_OK):
      if os.access(filename + '.env', os.R_OK):
        filename += '.env'
      else:
        from warnings import warn
        warn('File ' + filename + ' (or ' + filename + '.env) does not exist or not readable')
        return

    with open(filename) as fp:
      line = fp.readline()
      while line:
        line = line.strip()
        if len(line):
          if not (line.startswith('#') and line.startswith('unset')):
            if line.startswith('export'): line = line[6:].strip()

            i = line.find('=')
            if i > 0:
              cls.data[line[:i]] = line[i+1:].strip('"').strip("'")
            else:
              cls.data[line]=''

        line = fp.readline()


# EOF confenv/__init__.py
