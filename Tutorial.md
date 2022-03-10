# Tutorial for CY_SUMO
Detailed Tutorial for using CY_SUMO
 > Author: Cheng Yang, University of Michigan 
 > 
 > Version: 2022_03_10

## Table of contents
[**Step 0: Supplimentary SUMO Knowledge**](#step0)
   1. [The computational core - `sumoproject.dll`](#sumocore)


## Step 0: Supplimentary SUMO Knowledge <a name="step0"></a>
### The computational core - `sumoproject.dll`<a name="sumocore"></a>
> In the SUMO GUI, equations are complied to C++ code for faster calculations. It is often to see a message in the bottom-left of the GUI - 'Preparing Simulation: Build progress: x% '. This process is called compling, where all information in the GUI are complied to a `.dll` file. Python can directly communicate with this computational core with SUMO-Python API.
> 
> **How to find this core?**
> 
> In the GUI, go to `View` --> `Directories` --> `Project Directory`. In the opened directory, there is a `sumoproject.dll`, which is the sumo computational core. 
> 
> <img src="/TutorialPics/FindTempDir.JPG" alt="FineTempPic" style="height: 300px; width:800px;"/>  


### Storage of SUMO variables - `XXX.xml`
> Values of all variables and information @ current simulation time stamp, including parameters, states, constants and others, are stored in a `.xml` file, which could be loaded into the sumo computational core or saved from the sumo computational core. 
> 
> **How to save .xml file for CY_SUMO?**
> 
> > In the GUI, go to `Advanced` --> `Core  Window` (ALT+C).
> > 
> > <img src="/TutorialPics/CoreWindow.JPG" alt="CoreWindow" style="height: 600px; width:800px;"/>  
> > 
> > In the command line, type in `save A2O.xml`. The .xml will be saved in the `Project Directory`.
> > 


### SUMO Incode Names 
> SUMO Incode Names are names defined in an specific way that sumo computational core can understand. They are important, because they are variable names in the Python scripts. **For details about naming rules, please refer to "The Book of SumoSlang"- 7 Namespaces**.    
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
> 1. Search within the .xml file with CLT+F (Recommended).
>      
> 2. Search in SUMO GUI. OUTPUT SETUP--> bottom left panel --> dropdown bar changed from 'Variables' to 'Raw' --> Search the tree structure and hover mouse on variables;       



## Step 1: Prepare ingredients needed from SUMO GUIs 
### 
