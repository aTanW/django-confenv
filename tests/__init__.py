# -*- coding: utf-8 -*-
#
# tests/__init__.py - confenv module tests
# (c) 2019 Vitaly Protsko <villy@sft.ru>
# Licensed under GPLv3

# 
from pkgutil import find_loader
from unittest import TestSuite, defaultTestLoader

def autoload():
  result = TestSuite()

  baseSuite = defaultTestLoader.loadTestsFromName('tests.baseTest')
  if baseSuite.countTestCases() > 0: result.addTest(baseSuite)

  if find_loader('django'):
    djangoSuite = defaultTestLoader.loadTestsFromName('tests.djangoTest')
    if djangoSuite.countTestCases() > 0: result.addTest(djangoSuite)

  return result


# EOF confenv/tests/__init__.py
