#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 11:55:09 2025

@author: quintes
"""
# run only once to create databases

from main import engine
from models.base import Model
from models.measurements import *
from models.molecules import *


Model.metadata.create_all(engine)
