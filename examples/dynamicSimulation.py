# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:47:26 2022

@author: 28417
"""

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
This is an example script to replicate the dynamic simulations in the SUMO GUI,
with (1)different initial conditions; (2)dynamic input functions; and 
(3) adjusted parameters

Script objective： 
Run multiple dynamic simulations with a set of different combinations of inputs

"""
dynamic_inputs = {'Trial1':{'xml':'Cmd_ID_0.xml',
                            'stop_time':1*dur.day,
                            'data_comm_freq':1*dur.hour,
                            'param_dic':{'Sumo__Plant__CSTR3__param__DOSP': 2,
                                         'Sumo__Plant__Influent__param__Q':24000},
                            'input_fun':{"Sumo__Plant__Influent__param__TKN": lambda t: 32 + (42-32)/(1+np.exp(-5*(t-0.01))),
                                         "Sumo__Plant__Influent__param__TCOD": lambda t: 400 + 50*np.sin(20*t)},
                            'tsv_file':['Influent_Table1.tsv']},
                  'Trial2':{'xml':'Cmd_ID_0.xml',
                            'stop_time':1*dur.day,
                            'data_comm_freq':1*dur.hour,
                            'param_dic':{'Sumo__Plant__CSTR3__param__DOSP': 1,
                                         'Sumo__Plant__Influent__param__Q':20000},
                            'input_fun':{"Sumo__Plant__Influent__param__TKN": lambda t: 32 + (42-32)/(1+np.exp(-5*(t-0.01))),
                                         "Sumo__Plant__Influent__param__TCOD": lambda t: 400 + 50*np.sin(20*t)},
                            'tsv_file':['Influent_Table1.tsv']}
                  }


# Get current path 
current_path = os.getcwd()
# Initiate name string of the sumo .dll core    
model = os.path.join(current_path,"A2O.dll")
# Create a list of sumo encode variables to track 
sumo_variables = ["Sumo__Time",
                  "Sumo__Plant__Effluent__SNHx",
                  "Sumo__Plant__Effluent__SNOx",
                  "Sumo__Plant__Effluent__TCOD",
                  "Sumo__Plant__Effluent__SPO4"]

# Create a CY_SUMO object 
test = CY_SUMO(model= model,
               sumo_variables=sumo_variables)
test.dynamic_run(dynamic_inputs,save_name="dynamic.xlsx")