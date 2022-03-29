# Tutorial for CY_SUMO
Detailed Tutorial for using CY_SUMO. In this tutorial, we will walk through together examples that are provided in this repo (`.\examples\`) and template scripts can be adjusted based on users' needs.  
 > Author: Cheng Yang, University of Michigan 
 > 
 > Version: 2022_03_10

## Table of contents
[**Supplimentary SUMO Knowledge**](#step0)
   1. [The computational core - `sumoproject.dll`](#sumocore)
   2. [Storage of SUMO variables - `XXX.xml`](#sumostore)
   3. [SUMO Incode Names](#sumoincode)

[**Prepare ingredients needed from CY_SUMO**](#step1)

[**Steady-state simulations**](#step2)

[**Dynamic simulations**](#step3)

[**Dynamic simulations with steady-state start**](#step4)


## Supplimentary SUMO Knowledge <a name="step0"></a>
### The computational core - `sumoproject.dll`<a name="sumocore"></a>
> In the SUMO GUI, equations are complied to C++ code for faster calculations. It is often to see a message in the bottom-left of the GUI - 'Preparing Simulation: Build progress: x% '. This process is called compling, where all information in the GUI are complied to a `.dll` file. Python can directly communicate with this computational core with SUMO-Python API.
> 
> **How to find this core?**
> >
> > In the GUI, go to `View` --> `Directories` --> `Project Directory`. In the opened directory, there is a `sumoproject.dll`, which is the sumo computational core. 
> >
> > <img src="/TutorialPics/FindTempDir.JPG" alt="FineTempPic" style="height: 300px; width:800px;"/>  


### Storage of SUMO variables - `XXX.xml`<a name="sumostore"></a>
> - Values of all variables and information @ current simulation time stamp, including parameters, states, constants and others, are stored in a `XXX.xml` file, which could be loaded into the sumo computational core or saved from the sumo computational core. 
> - Dynamic Inputs (input_tables) are stored in a seperate form called `.tsv`. They could be found the same way as fining the `sumoproject.dll`
> 
> **How to save .xml file for CY_SUMO?**
> 
> > In the GUI, go to `Advanced` --> `Core  Window` (ALT+C). In the command line, type in `save XXX.xml`. The `XXX.xml` will be saved in the `Project Directory`.
> > <img src="/TutorialPics/CoreWindow.JPG" alt="CoreWindow" style="height: 600px; width:800px;"/>  


### SUMO Incode Names <a name="sumoincode"></a>
> SUMO Incode Names are names defined in an specific way that sumo computational core can understand. They are important, because they are variable names used in the SUMO-Python API and CY_SUMO. **For details about naming rules, please refer to "The Book of SumoSlang"- 7 Namespaces**.    
> 
> **Examples:**
> 
> - Sumo__Plant__CSTR2__param__L_Vtrain;
>      
> - Sumo__Plant__Effluent__SNOx;       
>      
> - Sumo__Time;
> 
> 
> 
> **Ways to query these variables**
> 
> 1. Search within the .xml file with CLRT+F (Recommended).
>  - Open the `XXX.xml` file with `.txt` format
>  - CLRT+F (Keyboard Shortcut for Search & Replace) + key words (e.g. SNHx, effluent)  
>      
> 2. Search in SUMO GUI. 'OUTPUT SETUP'--> bottom left panel --> dropdown bar changed from 'Variables' to 'Raw' --> search the tree structure and hover mouse on variables;       



## Prepare ingredients needed from CY_SUMO <a name="step1"></a>
1. Open target sumo project with SUMO GUI. In this case, it is `A2O plant.sumo`.
2. Open the `Project Directory` of the SUMO project, copy and paste the `sumoproject.dll` to the working directory of python. In this case, it was renamed into `A2O.dll`. Rename is not mandatory.
3. Save current values of the SUMO variable using the `save XXX.xml` command, then copy and paste it from the `Project Directory` to the working directory of python. In this case, it was saved as `A2O.xml`
4. For dynamic simulations, if tabular inputs are used in SUMO GUI, these tables are converted into `.tsv` files. Copy and paste all the `.tsv` files to the working directory of python. In this case, the '.tsv' file is `Influent_Table1.tsv`.

> Checklist in the python working directory
> - `A2O plant.sumo`
> - `A2O.dll`
> - `A2O.xml`
> - `Influent_Table1.tsv`
> - `CY_SUMO.py`
> - `sumoscheduler.py` (may not needed)

## Steady-state simulations <a name="step2"></a>
**Scirpt template: [steadyStateSimulation.py](https://github.com/ChengYangUmich/CY_SUMO/blob/main/examples/steadyStateSimulation.py)** 
> 1. Import required package and modules
```python
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
from CY_SUMO import CY_SUMO, create_param_dict
```

> 2. Define inputs for `CY_SUMO()`
>>   1. Specify the sumo computational core 
>> ```python
>> # Get current path 
>> current_path = os.getcwd()
>> # Initiate name string of the sumo .dll core    
>> model = os.path.join(current_path,"A2O.dll")
>> ```
>>   2. Specify the output sumo variables (incode names) to be stored in excel. 
>> ```python
>> sumo_variables = [
>>                  "Sumo__Plant__Effluent__SNHx",
>>                  "Sumo__Plant__Effluent__SNOx",
>>                  "Sumo__Plant__Effluent__TCOD",
>>                  "Sumo__Plant__Effluent__SPO4"]
>> ```
>>   3. Specify the input sumo variables that are changed in each steady-state simulation results.
>>   
>>   **Note:**
>>   - A self-defined function `create_param_dict()` from CY_SUMO.py was used to format inputs ranges into the standard input form `param_dict`for CY_SUMO(). 
>>   - New parameters could be added in the form of `'sumo_incode_name': [x,y,...,z]` into the curly bracket of `input_dict`.
>>   - New parameters could also be added in the form of `'sumo_incode_name': value` into each batch of `param_dict`.   
>>```python
>> input_dic = {'Sumo__Plant__CSTR3__param__DOSP': [1,2.01],
>>              'Sumo__Plant__Influent__param__Q':[21000, 24000]}
>> param_dict = create_param_dict(input_dic)
>> ```  
>> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; where the standard `param_dic` form should be:
>> ```python 
>> param_dict = {0:{'Sumo__Plant__CSTR3__param__DOSP': 2,
>>                  'Sumo__Plant__Influent__param__Q':24000},
>>               1:{'Sumo__Plant__CSTR3__param__DOSP': 1.5,
>>                  'Sumo__Plant__Influent__param__Q':26000}}
>> ```
>>   4. Create the `CY_SUMO()` object
>> ```python 
>>   test = CY_SUMO(model= model,
>>               sumo_variables=sumo_variables,
>>               param_dic=param_dict)
>> ```
>>   5. Run steady_state()
>> ```python
>> test.steady_state(save_table = True, 
>>                   save_name = "steady_state_results.xlsx", 
>>                   save_xml = True)
>> ```
>> where:
>> - `save_table`: True for saving sumo_variables into an excel file, whose default name is "steady_state_results.xlsx".
>> - `save_name`: Used to rename the excel file.
>> - `save_xml`: True for saving each steady-state simulation as a `.xml` file, which could be query later.
>>   
>>  6. Expected Results
>>   - No error message shown in the Python console + logs (e.g. #1 530049 Core loop started. #1 530024 Following variable Sumo__Plant__Effluent__SNHx) from the `A2O.dll` are normal.   
>>   - Four `.xml` files, namely `Cmd_ID_0.xml`,`Cmd_ID_1.xml`,`Cmd_ID_2.xml`,`Cmd_ID_3.xml` with identical/similar file size. If size differs more than several KBs, go to `CY_SUMO.py`- Line 307. Increase the number(in seconds) in time.sleep(0.2) so that the .ddl has more time to save results before being cleaned up. 
>>   - An excel file, 'steady_state_results.xlsx' that stores results of each steady-state simulations, whose rows are different simuluations and columns are variables of interest. 

## Dynamic simulations <a name="step3"></a>
**Scirpt template: [dynamicSimulation.py](https://github.com/ChengYangUmich/CY_SUMO/blob/main/examples/dynamicSimulation.py)** 
> 1. Import required package and modules
```python
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
from CY_SUMO import CY_SUMO, create_param_dict
```

> 2. Define inputs for `CY_SUMO()`
>>   1. Specify the sumo computational core 
>> ```python
>> # Get current path 
>> current_path = os.getcwd()
>> # Initiate name string of the sumo .dll core    
>> model = os.path.join(current_path,"A2O.dll")
>> ```
>>   2. Specify the output sumo variables (incode names) to be stored in excel. **Note**: "Sumo_Time" is a mandatory output to be included in `sumo_variables` for dynamic simulations 
>> ```python
>> sumo_variables = ["Sumo__Time",
>>                  "Sumo__Plant__Effluent__SNHx",
>>                  "Sumo__Plant__Effluent__SNOx",
>>                  "Sumo__Plant__Effluent__TCOD",
>>                  "Sumo__Plant__Effluent__SPO4"]
>> ```
>>   3. Specify the dynamic settings for each dynamic simulation.
>> The `dynamic_inputs` is a nested dictionary, whose keys are names for dynamic simulations and values are settings.
>> Specficially:
>> `xml`: the initial conditions to load, which represents values @ t = 0
>> 
>> `stop_time`: the total sumo simulation time, equivalent to the 'Stop time' in SUMO GUI-SIMULATION-Dynammic. 
>>   
>> `data_comm_freq`: the data inverval for outputs, equivalent to the 'Data interval' in SUMO GUI-SIMULATION-Dynammic.
>> 
>> `param_dic`: the constant parameters to change in the simulation (only used when they are different from .xml) 
>> 
>> `input_fun`: the time-dependent parameters to change in the dynamic simulation, in the form of functions of `t` (in unit of days) 
>> 
>> `tsv_file`: the dynamic input tables used in the SUMO GUI.  
>>```python
>> dynamic_inputs = {'Trial1':{'xml':'Cmd_ID_0.xml',
>>                            'stop_time':1*dur.day,
>>                            'data_comm_freq':1*dur.hour,
>>                            'param_dic':{'Sumo__Plant__CSTR3__param__DOSP': 2,
>>                                         'Sumo__Plant__Influent__param__Q':24000},
>>                            'input_fun':{"Sumo__Plant__Influent__param__TKN": lambda t: 32 + (42-32)/(1+np.exp(-5*(t-0.01))),
>>                                         "Sumo__Plant__Influent__param__TCOD": lambda t: 400 + 50*np.sin(20*t)},
>>                            'tsv_file':['Influent_Table1.tsv']},
>>                  'Trial2':{'xml':'Cmd_ID_0.xml',
>>                            'stop_time':1*dur.day,
>>                            'data_comm_freq':1*dur.hour,
>>                            'param_dic':{'Sumo__Plant__CSTR3__param__DOSP': 1,
>>                                         'Sumo__Plant__Influent__param__Q':20000},
>>                            'input_fun':{"Sumo__Plant__Influent__param__TKN": lambda t: 32 + (42-32)/(1+np.exp(-5*(t-0.01))),
>>                                         "Sumo__Plant__Influent__param__TCOD": lambda t: 400 + 50*np.sin(20*t)},
>>                            'tsv_file':['Influent_Table1.tsv']}
>>                  }
>> ```  

>>   4. Create the `CY_SUMO()` object
>> ```python 
>>   test = CY_SUMO(model= model,
>>               sumo_variables=sumo_variables)
>> ```
>>   5. Run dynamic_run()
>> ```python
>> test.dynamic_run(dynamic_inputs, save_name = "steady_state_results.xlsx")
>> ```
>> where:
>> - `save_name`: Used to rename the excel file.
>>   
>>  6. Expected Results
>>   - No error message shown in the Python console + logs (e.g. #1 530049 Core loop started. #1 530024 Following variable Sumo__Plant__Effluent__SNHx) from the `A2O.dll` are normal.   
>>   - An excel file, 'dynamic.xlsx' that stores results of each dynamic simulations in a sheet, each columns of which are time series of sumo variables. 


## Dynamic simulations with steady-state start<a name="step4"></a>
In the SUMO GUI, there is a button called 'Steady-state start' under `SIMULATION-Dyamic` where the steady-state is reached first and then the dynamic simulation starts. This could also be fulfilled in CY_SUMO by assembing the previous two steps. 
> Step I: run a batch of steady_state simulations and save them as .xml files with `CY_SUMO.steady_state()`
> 
> Step II: specify these .xml files into the `dynamic_inputs` and continue dynamic simulation with `CY_SUMO.dynamic_run()` 

The steady-state calculation is expensive. This two-step apprach saves time for the steady-state calculations in case that repetitions are needed. More computational time could be saved as the total number of simulations increases towards a magnitude of hundreds and thousands. Additionally, it is easy to debug if things go wroing. 
