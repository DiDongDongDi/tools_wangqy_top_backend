#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file: urls
@author: kody
@create: 2025-06-28 08:52:52
@desc:
"""

from django.urls import path
from excel_tools import views

urlpatterns = [
    path("file/upload", views.upload_file, name="upload_file"),
]
