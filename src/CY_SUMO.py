# -*- coding: utf-8 -*-

from sumoscheduler import SumoScheduler
from sumoscheduler import Duration as dur 
import os
import pandas as pd 
import numpy as np
import datetime
import time 

def create_param_dict(a_dict):
    """
    This is a function to create the required parameter dictionary from lists of inputs' values. 

    Parameters
    ----------
    a_dict : dictionary
        keys: (string) sumo incode variables
        values: (list) their corresponding values' lists 
        example: 
        {"Sumo__Plant__CSTR2__param__DOSP":[0], 
         "Sumo__Plant__CSTR3__param__DOSP":[0,0.5],
         "Sumo__Plant__CSTR4__param__DOSP":[0,0.5]}

    Returns
    -------
    policy_dict: (nested dictionary)
        keys: (int) starting from 0 
        values: (dictionary) 
            keys: (string) sumo incode variables 
            values: (numeric type: int/float) the value of sumo incode variables
   example: 
        {
        0: {'Sumo__Plant__CSTR2__param__DOSP': 0,
             'Sumo__Plant__CSTR3__param__DOSP': 0,
             'Sumo__Plant__CSTR4__param__DOSP': 0},
        1: {'Sumo__Plant__CSTR2__param__DOSP': 0,
            'Sumo__Plant__CSTR3__param__DOSP': 0,
            'Sumo__Plant__CSTR4__param__DOSP': 0.5},
        2: {'Sumo__Plant__CSTR2__param__DOSP': 0,
            'Sumo__Plant__CSTR3__param__DOSP': 0.5,
            'Sumo__Plant__CSTR4__param__DOSP': 0},
        3: {'Sumo__Plant__CSTR2__param__DOSP': 0,
            'Sumo__Plant__CSTR3__param__DOSP': 0.5,
            'Sumo__Plant__CSTR4__param__DOSP': 0.5} 
        }
    """
    
    if not isinstance(a_dict, dict):
        raise TypeError("The input should be a dictionary whose keys are sumo incode names and values are lists of the their corresponding values")
    else:
        policy_dict = {}
        name_list=list(a_dict.keys())
        import itertools
        policy_space = list(itertools.product(*list(a_dict.values())))
        for policyID, an_op in enumerate(policy_space):
            temp_dict = {}
            for i in range(len(name_list)):
                temp_dict[name_list[i]] = an_op[i]
            policy_dict[policyID] = temp_dict
    return policy_dict





class CY_SUMO():
    """
    This is a module/wrapper to run SUMO21 simulations by directly interacting 
    sumocore.dll, which is on the SUMO-Python API (sumoscheduler.py) provided
    by Dynamita. It is able to replicate major functions in SUMO GUI.  
      
    Author: Cheng Yang, Unversitiy of Michigan, Ann Arbor, MI 
    
    Inputs:
    --------------
    (Mandatory)
        `model`: str  
        The 'XXX.dll' file generated by the SUMO GUI, e.g. "sumocore.dll".
        Full path is needed if python scripts and the 'XXX.dll' are not located 
        under the same path, e.g."C:/Users/28417/sumocore.dll" 
            
        `sumo_variables`: list
        The sumo incode variables to track in the ouputs,
        which can be found in the .xml file  
        e.g.  ["Sumo__Time",
               "Sumo__Plant__Effluent1__SNHx",
               "Sumo__Plant__CSTR2__DOSP",
               "Sumo__Plant__CSTR3__DOSP",
               "Sumo__Plant__CSTR4__DOSP"]
           
        `param_dic`: dictionary (could be nested dictionary)  
        The (nested) dictionary that stores the different combinations of   
        parameters to adjust in the simulation. 
        e.g. {"set1":{'Sumo__Plant__CSTR3__param__DOSP': 2,
                      'Sumo__Plant__Influent__param__Q':24000}
              "set2":{'Sumo__Plant__CSTR3__param__DOSP': 1,
                      'Sumo__Plant__Influent__param__Q':12000}}     
        
        
        
    (Optional)

        `parallel_job`: int, default = 4 
        Number of cores in CPU that can be run in parallel 
        
        `default_xml`: string, default = None 
        Name of the 'XXX.xml' loaded in advance for simulation
        
        `param_dic`: dictionary, nested
        Parameters to change in simulations.
        e.g. 
            {'trial1':{'Sumo__Plant__CSTR3__param__DOSP': 2,
                        'Sumo__Plant__Influent__param__Q':24000},
             'trial2':{'Sumo__Plant__CSTR3__param__DOSP': 1.5,
                         'Sumo__Plant__Influent__param__Q':26000}}
        
        
    Attributes: - Only important attributes are listed, attributes not mentioned 
                  here are for internal use.
    --------------
        All inputs, both mandatory and optional 
        
        `SS_table`: pd.DataFrame()
        --The output from parallel steady-state simulations 
    
    
    Methods: - Only important methods are listed, methods not mentioned 
                  here are for internal use.
    --------------
        `steady_state()`: run multiple steady state simulations

    Examples: 
        please refer to https://github.com/ChengYangUmich/CY_SUMO/examples
    --------------
    """
    def __init__(self, 
                 model, 
                 sumo_variables, 
                 paralell_job = 4,
                 default_xml = None,
                 param_dic = None):
        self.model = model
        self.sumo_variables = sumo_variables
        self.paralell_job = paralell_job
        self.default_xml = default_xml
        self.param_dic = param_dic
        self._param_commands_dic = {} # predefined, converted from self.param_dic
        # Intermediate variable for extracting current values of state variables
        # in SUMO
        if param_dic == None:
            self.current_sumo_vars = {1:None}
        else:
            # Create an empty nested diction for intermediate data storage
            self.current_sumo_vars = {key:None for key in range(1,len(param_dic)+1)}   
            # Add variable names from the param_dic into sumo_variables
            for a_dic in self.param_dic.values():
                for a_var in a_dic.keys():
                    self.sumo_variables.append(a_var)
        self.sumo_variables = self._unique_list(self.sumo_variables)
        
    def _set_up_scheduler(self, msg_callback, datacomm_callback):
        """
        (Internal) method
    
        Used for creating a SumoScheduler Object. One console is only allow 
        to create one SumoScheduler object
        
        Parameters:
        --------------   
        `msg_callback`: function
            The message callback function used for SumoScheduler registration
        `datacomm_callback`: function
            The data commnunication callback function used for SumoScheduler registration
            
        """
        self.sumo = SumoScheduler()
        self.sumo.setParallelJobs(self.paralell_job)
        self.sumo.message_callback = msg_callback
        self.sumo.datacomm_callback = datacomm_callback
    
    def _line_command(self, a_dict, sumo_default):
        """
        (Internal) Method, used to create a one-line commands seperated with ';'
        from an initial condition dictionary that could be input into the SUMO
        Parameters
        ----------
        a_dict : dictionary
            a dictionary that stores the parameters to be adjusted
            e.g. {'Sumo__Plant__CSTR3__param__DOSP': 2,
                  'Sumo__Plant__Influent__param__Q':24000}

        Returns
        -------
        commands : string 
            a string that combines all items from the a_dict and formats them 
            into a online standard SUMO input command
            e.g. "reset;mode steady;set Sumo__Plant__CSTR3__param__DOSP 2; 
                  set Sumo__Plant__Influent__param__Q 24000;start;"
        """
        # If not .xml file is given, reset and start simulations
        if sumo_default == True:
            commands = "reset;"
        # If .xml file is given, load .xml file, map to initial condition and then start 
        else:
            commands = f"load {self.default_xml};maptoic;"
        commands += "mode steady;"
        # append ajusted variables into the one-line command string 
        for a_key, a_val in a_dict.items():
            commands += f"set {a_key} {a_val};"
        commands += "start;"
        return commands
   
    def _set_ss_commands(self,sumo_default):
        """
        (Internal) Method, used to create a list of commands used for 
        steady-state simulations, and stored it in self._param_commands_dic
            e.g. "reset;mode steady;set Sumo__Plant__CSTR3__param__DOSP 2; 
                  set Sumo__Plant__Influent__param__Q 24000;start;" --> 
                  ["reset","mode steady",
                   "set Sumo__Plant__CSTR3__param__DOSP 2",
                   "set Sumo__Plant__Influent__param__Q 24000",
                   "start"]
        """
        if sumo_default:
            self._param_commands_dic[0] = 'reset;mode steady;start'
        else:
            if self.param_dic == None:
                self._param_commands_dic[0] = 'load {self.default_xml};maptoic;mode steady;start'
            # if `self.param_dic` is a nested diction
            elif any(isinstance(i,dict) for i in self.param_dic.values()):            
                for a_dic_key,a_dic in self.param_dic.items():
                    self._param_commands_dic[a_dic_key] = self._line_command(a_dic,sumo_default)
            else:
                self._param_commands_dic[0] = self._line_command(self.param_dic,sumo_default)

    
    # Code block replicating steady-state simulations
    def steady_state(self, sumo_default = False, save_table = True, 
                     save_name = "steady_state_result.xlsx", save_xml = False):
        """
        Parameters
        ----------
        sumo_default: Boolean, optional
            Whether to reset back to all sumo default 
        save_table : Boolean, optional  
            Whether to save the self.ss_table
        save_name : String, optional 
            The ouput xlsx file name saved from the self.ss_table
        save_xml: Boolean, optional
            Whether to save the .xml files for each steady state simulations

        Returns
        -------
        None. examples see --> .\examples\steadyStateSimulation.py

        """
        # Pre-define variables to store steady-state simulation results 
        self.SS_table = pd.DataFrame()
        # An intermediate boolean used in steady_state_msg_callback 
        self._save_xml = save_xml
        # Create the steady-state commands in lists 
        self._set_ss_commands(sumo_default=sumo_default)
        # Register callback functions 
        msg_callback = self._steady_state_msg_callback
        datacomm_callback = self._steady_state_datacomm_callback
        self._set_up_scheduler(msg_callback, datacomm_callback)
        for a_key, a_line_command in self._param_commands_dic.items():
            commands = []
            for a_element in a_line_command.split(";"):
                if a_element != "":
                    commands.append(a_element + ";")              
            self.sumo.schedule(
                model = self.model,
                commands = commands,
                variables = self.sumo_variables,
                jobData ={"SS_cmd": a_line_command,
                          "Cmd_ID": a_key})
                # blockDatacomm=True)
        print("Jobs started:", self.sumo.scheduledJobs)
        
        while (self.sumo.scheduledJobs > 0):
            time.sleep(0.1)

        # self.sumo.scheduler.cleanup()
        
        if save_table == True:
            self.SS_table.to_excel(save_name)
            print(f"------SS_table saved as {save_name}-----")
    
            
    def _steady_state_msg_callback(self,job,msg):
        """
        (Internal) method
        Parameters
        ----------
        job : Int
            The job ID defined in the sumo scheduler
        msg : string 
            Message similar to the sumo core window 

        Returns
        -------
        None.

        """
        print(f"#{job} {msg}")
        if (self.sumo.isSimFinishedMsg(msg)):
            ## save the .xml files
            if self._save_xml == True:
                jobData = self.sumo.getJobData(job)
                xml_file = f"Cmd_ID_{jobData['Cmd_ID']}.xml"
                command = f"save {xml_file};"
                self.sumo.sendCommand(job,command)
                time.sleep(2) # Increase the sleep time if the .xml is saved in malform (whose size is smaller than others)
                print(f"{xml_file} -------- saved-----------")
            x = pd.DataFrame([self.current_sumo_vars[job]])
            self.SS_table = pd.concat([self.SS_table,x], ignore_index=True)
            # self.SS_table = self.SS_table.append(self.current_sumo_vars[job],ignore_index = True)
            self.sumo.finish(job)
    
    def _steady_state_datacomm_callback(self,job,data):
        """
        (Internal) method
        Parameters
        ----------
        job : Int
            The job ID defined in the sumo scheduler
        data : dictionary 
            Stored information defined in the self.sumo.schedule() - jobData 

        Returns
        -------
        None.

        """
        jobData = self.sumo.getJobData(job)
        self.current_sumo_vars[job] = {**data,**jobData}
        
        
    # Code block replicating dynamic simulations with initial states loaded       
    def dynamic_run(self, dynamic_inputs, 
                    save_table= True, save_name = "dynamic_result.xlsx"):
        """
        Dynamic runs with given initial conditions (.xml), changed parameters, input functions

        Parameters
        ----------
        dynamic_inputs : dictionary (nested)
            e.g. 
            dynamic_inputs = 
                 {'Trial1':{'xml':'Cmd_ID_0.xml',
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

            
        save_table : Boolean, optional
            Whether to save the simulations to a .xlsx file whose sheets are keys in the `dynamic_inputs`. The default is True.
        save_name : String ended with '.xlsx', optional
            Name of the excel file to save. The default is "dynamic_result.xlsx".

        Returns
        -------
        None.

        """
        # Create a dictionary to store dynamic simulation results
        self._myDataDic = {key:pd.DataFrame() for key in dynamic_inputs.keys()}
        msg_callback = self._msg_callback_dyn
        datacomm_callback = self._datacomm_callback_dyn
        self._set_up_scheduler(msg_callback, datacomm_callback)
        
        for a_dyn_key, a_dyn_input in dynamic_inputs.items():
            # Generate the commands for inputs 
            temp_xml = a_dyn_input['xml']
            commands =  [f'load "{temp_xml}";', "maptoic;"]
            if a_dyn_input['tsv_file'] != None:
                for a_tsv in a_dyn_input['tsv_file']:
                    commands.append(f'loadtsv "{a_tsv}";')
            for a_constant_var, its_value in  a_dyn_input['param_dic'].items():
                commands.append(f"set {a_constant_var} {its_value};")
                # Add adjusted variables in sumo variable 
                self.sumo_variables.append(a_constant_var)
            # Add dynamic input sumo variables 
            for a_dyn_var in a_dyn_input["input_fun"].keys():
                self.sumo_variables.append(a_dyn_var)
            commands.append(f"set Sumo__StopTime {a_dyn_input['stop_time']};")
            commands.append(f"set Sumo__DataComm {a_dyn_input['data_comm_freq']};")
            commands.append("mode dynamic;")
            commands.append("start;")
            # schedule jobs 
            self.sumo.schedule(self.model, 
                                commands=commands, 
                                jobData= {'key_ID':a_dyn_key,
                                          'info':a_dyn_input}, 
                                variables=self.sumo_variables,
                                blockDatacomm=True)
        print("Jobs started:", self.sumo.scheduledJobs)
    
        while (self.sumo.scheduledJobs > 0):
            time.sleep(0.1)
        
        self.sumo.cleanup() 
        
        # Code block to save self_myDataDic to a excel file 
        if save_table == True:
            with pd.ExcelWriter(save_name) as writer:
                for a_key in list(self._myDataDic.keys()):
                    a_df = self._myDataDic[a_key]
                    sheet_name = f"{a_key}"
                    a_df.to_excel(writer, sheet_name)
            print(f"{save_name} was saved successfully")
    
    def _msg_callback_dyn(self,job,msg):
        """
        (Internal) method
        Parameters
        ----------
        job : Int
            The job ID defined in the sumo scheduler
        msg : string 
            Message similar to the sumo core window 

        Returns
        -------
        None.

        """
        print(f"SUMO: #{job} {msg}")
        if (self.sumo.isSimFinishedMsg(msg)):
            self.sumo.finish(job) 
            
    def _datacomm_callback_dyn(self, job, data):
        """
        (Internal) method
        Parameters
        ----------
        job : Int
            The job ID defined in the sumo scheduler
        data : dictionary 
            Stored information defined in the self.sumo.schedule() - jobData 

        Returns
        -------
        None.

        """
        jobData = self.sumo.getJobData(job)
        data["Sumo__Time"] /= self.sumo.dur.day 
        x = pd.DataFrame([data])
        self._myDataDic[jobData['key_ID']] = pd.concat([self._myDataDic[jobData['key_ID']] ,x],ignore_index=True)
        # self._myDataDic[jobData['key_ID']] = self._myDataDic[jobData['key_ID']].append(data,ignore_index = True)
        if len(jobData['info']['input_fun']) !=0:
            for a_var,a_fun in jobData['info']['input_fun'].items():
                current_value = a_fun(data["Sumo__Time"])
                print(f"{a_var} == {current_value}")
                self.sumo.sendCommand(job, f"set {a_var} {current_value}")
                
       
    def _unique_list(self, list1):
        # initialize a null list
        unique_list = []
     
        # traverse for all elements
        for x in list1:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        return unique_list
