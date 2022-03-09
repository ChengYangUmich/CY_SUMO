# -*- coding: utf-8 -*-

# importing sys
import sys
# add the path where the CY_sumo locates 
sys.path.append("..\src")
from sumoscheduler import SumoScheduler
from sumoscheduler import Duration as dur 
import os
import pandas as pd 
import numpy as np
import datetime
# Import CY_SUMO class 
from CY_SUMO import CY_SUMO, create_policy_dict

"""
This is an example script to replicate the steady-state simulations in the SUMO GUI

Script objective： 
Run multiple simulations with a set of different combinations of inputs

"""


# Get current path 
current_path = os.getcwd()
# Initiate name string of the sumo .dll core    
model = os.path.join(current_path,"A2O.dll")
# Create a list of sumo encode variables to track 
sumo_variables = [
                  "Sumo__Plant__Effluent__SNHx",
                  "Sumo__Plant__Effluent__SNHx",
                  "Sumo__Plant__Effluent__TCOD",
                  "Sumo__Plant__Effluent__SPO4"]
# Create the param_dict  
input_dic = {'Sumo__Plant__CSTR3__param__DOSP': [0.5,1],
             'Sumo__Plant__Influent__param__Q':[22000,24000]}
param_dict = create_policy_dict(input_dic)

# param_dict = {'trial1':{'Sumo__Plant__CSTR3__param__DOSP': 2,
#                         'Sumo__Plant__Influent__param__Q':24000},
#               'trial2':{'Sumo__Plant__CSTR3__param__DOSP': 1.5,
#                         'Sumo__Plant__Influent__param__Q':26000}}

# Create a CY_SUMO object 
test = CY_SUMO(model= model,
               sumo_variables=sumo_variables,
               param_dic=param_dict)
# Run a batch of simulations,output tracking variables into test1.xlsx, 
# and save .xml for each of steady-state simulations  
test.steady_state(save_table = True, 
                  save_name = "test1.xlsx", 
                  save_xml = True)