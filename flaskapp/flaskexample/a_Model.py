#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 12:05:11 2018

@author: rebeccareitz
"""

def ModelIt(fromUser  = 'Default', births = []):
  in_month = len(births)
  print('The number born is %i' % in_month)
  result = in_month
  if fromUser != 'Default':
    return result
  else:
    return 'check your input'