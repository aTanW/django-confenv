# -*- coding: utf-8 -*-
#
# tests/baseTest.py - confenv base class tests
# (c) 2019 Vitaly Protsko <villy@sft.ru>
# Licensed under GPLv3


# -----
from unittest import TestCase


# -----
class baseTestCase(TestCase):
  'confenv.Env class tests'

  def setUp(self):
    from confenv import Env
    self.base = Env

  def tearDown(self):
    del self.base

  def test_00_type(self):
    'Checking [Env] type of tor symbol'
    self.assertTrue(callable(self.base), 'Symbol "Env" is not callable')

  def test_01_defaults(self):
    'Checking [Env] class default values'
    self.assertTrue(self.base.exception == Exception, 'Bad default exception class')
    self.assertTrue(self.base.defconf_key == 'CONFENV_PROFILE', 'Bad default configuration key name')
    self.assertTrue(self.base.filename == None, 'Bad default environment file name')
    self.assertTrue(self.base.filepath == None, 'Bad default environment file path')

  def test_02_creation(self):
    'Checking [Env] Env class instantiation'
    ei = self.base()
    self.assertTrue(isinstance(ei, self.base), 'Bad Env class instantiation')

  def test_03_defaults(self):
    'Checking [Env] Env instant parameters'
    ei = self.base(defconf_key='TESTKEY', filepath='.', filename='test')
    self.assertTrue(ei.defconf_key == 'TESTKEY', 'Bad configuration key parameter assignment')
    self.assertTrue(ei.filename == 'test', 'Bad file name parameter assignment')
    self.assertTrue(ei.filepath == '.', 'Bad file path parameter assignment')

  def test_04_fileparse(self):
    'Checking [Env] .env file parsing'
    ei = self.base(filename='test')
    self.assertTrue(ei('TESTEXPORT') == 'value', 'Bad .env file parsing')

  def test_05_typetest(self):
    'Checking [Env] value types parsing'
    kwl = {
      'UNITEST': ('unicode', ),
      'BOOLTEST1': (bool, ),
      'BOOLTEST2': (bool, ),
      'INTTEST': (int, 100),
      'DEFTEST': ('int', 0),
      'FLOATEST': (float, ),
      'JSONTEST': ('json', ),
      'LISTEST': (list, ),
      'TUPLETEST': (tuple, ),
      'DICTEST1': (dict, {}),
      'DICTEST2': ('dict', {}),
      'DICTYPE': ({'value': str, 'cast': {'floatkey': float, 'boolkey': bool} }, {}),
      'URLTEST': ('url', ),
    }
    ei = self.base(filename='extest', **kwl)
    self.assertTrue(ei('STRTEST') == 'str test value', 'Plain string type test failed')
    self.assertTrue(ei('UNITEST') == 'Тест байт', 'Unicode type test failed')
    self.assertTrue(ei('BOOLTEST1'), 'bool type test failed')
    self.assertFalse(ei('BOOLTEST2'), 'bool type test failed')
    self.assertTrue(ei('INTTEST') == 54321, 'int type test failed')
    self.assertTrue(ei('DEFTEST') == 0, ' type test failed')
    self.assertTrue(ei('FLOATEST') == 12.345, ' type test failed')
    self.assertTrue(ei('JSONTEST') == {'hdr1':'val1','hdr2':{'hdr22':'val22','hdr21':'val21'},'hdr3':[1, 2, 3]}, 'JSON type test failed')
    self.assertTrue(ei('LISTEST') == [ 'a', 'b', 'c', 'd' ], 'list type test failed')
    self.assertTrue(ei('TUPLETEST') == ( '9', '8', '7', '6' ), 'tuple type test failed')
    self.assertTrue(ei('DICTEST1') == {'key1':'val1','key2':'val2','keyz':'valz'}, 'dict type test failed')
    self.assertTrue(ei('DICTEST2') == {'keyA':'valA'}, 'dict type test failed')
    self.assertTrue(ei('DICTYPE') == {'strkey':'strval','floatkey':5.43,'boolkey':True}, 'dict type test failed')
#    self.assertTrue(ei('TEST') == , ' type test failed')

  def test_06_varsubst(self):
    'Checking [Env] variable substitution'
    ei = self.base(filename='test')
    self.assertTrue(ei('LASTSUBST') == 'firstval/middle test', 'Bad variable substitution')

  def test_07_attrs(self):
    'Checking [Env] attribute access'
    ei = self.base(filename='test')
    self.assertTrue(ei.TESTKEY == 'testvalue', 'Bad item access as attribute')
    ei.TESTVAR = 'testvar'
    self.assertTrue(ei.TESTVAR == 'testvar', 'Bad attribute assignment')

  def test_08_dictlike(self):
    'Checking [Env] dict-like interface'
    ei = self.base(filename='test')
    k = ei.keys()
    self.assertTrue('TESTKEY' in k, 'Bad dict keys() emulation')
    ei['TESTVAR'] = 'testvar'
    self.assertTrue(ei['TESTVAR'] == 'testvar', 'Bad item assignment')
    

# EOF confenv/tests/baseTest.py
