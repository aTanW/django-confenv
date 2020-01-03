# -*- coding: utf-8 -*-
#
# tests/djangoTest.py - confenv django extensions tests
# (c) 2019 Vitaly Protsko <villy@sft.ru>
# Licensed under GPLv3


# -----
from unittest import TestCase
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ImproperlyConfigured
from pkgutil import find_loader

if DJANGO_VERSION < (2, 0):
  DJANGO_POSTGRES = 'django.db.backends.postgresql_psycopg2'
else:
  DJANGO_POSTGRES = 'django.db.backends.postgresql'

if find_loader('redis_cache'):
  DJANGO_REDIS = 'redis_cache.RedisCache'
else:
  DJANGO_REDIS = 'django_redis.cache.RedisCache'


# -----
class djangoTestCase(TestCase):
  'confenv.django.Env class tests'

  def setUp(self):
    from confenv.django import Env
    self.base = Env

  def tearDown(self):
    del self.base

  def test_10_type(self):
    'Checking [Env] type of tor symbol'
    self.assertTrue(callable(self.base), 'Symbol "Env" is not callable')

  def test_11_defaults(self):
    'Checking [Env] class default values'
    self.assertTrue(self.base.exception == ImproperlyConfigured, 'Bad default exception class')

  def test_12_creation(self):
    'Checking [Env] Env class instantiation'
    ei = self.base()
    self.assertTrue(isinstance(ei, self.base), 'Bad Env class instantiation')

  def test_13_fileparse(self):
    'Checking [Env] .env file parsing'
    ei = self.base(filename='test')
    self.assertTrue(ei('TESTEXPORT') == 'value', 'Bad .env file parsing')

  def test_14_typetest(self):
    'Checking [Env] value types parsing'
    ei = self.base(filename='djtest')
    self.assertTrue(ei.db_url()                  == {'NAME':'test','PORT':5432,'ENGINE':DJANGO_POSTGRES,'HOST':'db.example.com','PASSWORD':'access','USER':'user'}, 'Default PostgreSQL url parse test failed')
    self.assertTrue(ei.db_url('DB2_URL')         == {'HOST':'ldap.example.com','PASSWORD':'access','NAME':'ldap://ldap.example.com','USER':'user','ENGINE':'ldapdb.backends.ldap'}, 'LDAP url parse test failed')
    self.assertTrue(ei.cache_url()               == {'BACKEND':'django.core.cache.backends.dummy.DummyCache','LOCATION':''}, 'Default cache url test failed')
    self.assertTrue(ei.cache_url('CACHE2_URL')   == {'BACKEND':DJANGO_REDIS,'LOCATION':'redis://user3:access3@redis.example.com/10'}, 'redis cache url test failed')
    self.assertTrue(ei.search_url('SEARCH_URL')  == {'ENGINE':'haystack.backends.simple_backend.SimpleEngine'}, 'Default search url test failed')
    self.assertTrue(ei.search_url('SEARCH2_URL') == {'ENGINE':'haystack.backends.solr_backend.SolrEngine','URL':'http://search.example.com:8983/solr/greatsite/select/q=*.*'}, 'Solr search url test failed')
    self.assertTrue(ei.email_url('EMAIL_URL')    == {'EMAIL_BACKEND':'django.core.mail.backends.dummy.EmailBackend','EMAIL_PORT':None,'EMAIL_HOST_USER':None,'EMAIL_HOST':None,'EMAIL_HOST_PASSWORD':None,'EMAIL_FILE_PATH':''}, 'Default e-mail url parse test failed')
    self.assertTrue(ei.email_url('EMAIL2_URL')   == {'EMAIL_BACKEND':'django.core.mail.backends.smtp.EmailBackend','EMAIL_PORT':None,'EMAIL_HOST_USER':'user4','EMAIL_HOST':'mta.example.com','EMAIL_HOST_PASSWORD':'access4','EMAIL_FILE_PATH':'','EMAIL_USE_TLS':True}, 'SSL e-mail url parse test failed')
    self.assertTrue(ei.email_url('EMAIL3_URL')   == {'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend', 'EMAIL_PORT': None, 'EMAIL_HOST_USER': 'user5', 'EMAIL_HOST': 'mta1.example.com', 'EMAIL_HOST_PASSWORD': 'access5', 'EMAIL_FILE_PATH': '', 'EMAIL_USE_TLS': True}, 'TLS e-mail url parse test failed')

# EOF confenv/tests/djangoTest.py
