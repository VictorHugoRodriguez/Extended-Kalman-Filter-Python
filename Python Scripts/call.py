#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 11:36:54 2019

@author: victorh
"""

############# Important notes #################################################
# database_config.py must be executed first follow by the file call.py, which 
# contains the required loop to run the calculations constantly.
# File database_config.py contains the initial value configuration for the 
# calculations, creates the database structure (required tables), provides the 
# initial conditions for the observer x0 and the initial Cov. matrix of the
# estimation error P0=Q*200. 
# Observer.py contains the required observer calculations
###############################################################################

while True:
    exec(open("./Observer.py").read())
