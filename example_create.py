#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 11:59:25 2025

@author: quintes
"""
import create as cr

cr.create_tdp("BDP0", "co", "NO1", "CH0", "///", "C=0=H")
cr.create_single("BP0Br", "C7H8Br", "///d", "C-C-C=CH3-Br", "triplet measurement")
cr.create_single("toluene", "C7H8", "///a", "C-C-C=CH3")
cr.create_rp("TRP", "BI", "FLAV", "CH0N", "///e", "C=0=H13")
cr.create_ttp("BDP0", "xy", "POR2", "CH0N", "///f", "C=0=H13NBr")
