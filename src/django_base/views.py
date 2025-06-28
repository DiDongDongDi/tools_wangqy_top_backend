#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file: views
@author: kody
@create: 2025-06-28 08:22:56
@desc:
"""

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def get_menu_list_i18n(request):
    return JsonResponse({"code": 0, "data": {"list": []}})
