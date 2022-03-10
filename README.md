# CY_SUMO
 Implementation of SUMO simulations via Python. 
 > Author: Cheng Yang, University of Michigan 
 > 
 > Version: 2022_03_07

# About 
This is a modulue that wraps up the SUMO-Pyhton API (Dynamita) that could run SUMO simulations in batches. With inputs and outputs pre-defined, all simulations could be run with several lines of codes. It is designed for users who want to run hundreds of thousands of SUMO simulations but with little knowledge of the SUMO-Python API. **It frees SUMO-users from iterative manual interactions with SUMO GUI.**

Specifically, `CY_SUMO` is able to:
- Implement steady-state simualtions in batches. Results from each steady-state simulation can be save as a 'XXX.xml', and outputs of interests could be stored into an excel file for comparision. An typical application is sensitivity analysis.    
- Implement dynamic simualtions in batches. The initial conditions (start-points), inputs (can be both time-varying or constants), simulation durations and data intervals could be defined specifically for each batch. An typical application is scenario analysis.     

# Preparation
## Materials
The followings are *required* to use `CY_SUMO`:
- Digital twin license from Dynamita 
- A functional SUMO project (`XXX.sumo`) in GUI, where the following items could be generated and copied to the directory where python scripts locate: 
    - `sumoproject.dll` - the SUMO computational core.
    -  `XXX.xml` - an xml file that stores all current values/information of SUMO comuputation --> used for finding encode names of sumo variables. 
    -  `XXX.tsv` - (optional) a tsv file that stores the pre-defined dynamic tables as in the SUMO GUI.
- python (version > 3.7) 

*Note: XXX are names that are case-specific.*
## Dependencies
The following dependencies are *required* to use `CY_SUMO`:
- `sumo.sumoscheduler` and its dependencies.  --> available as the './src/sumoscheduler.py'
- [`numpy`](https://numpy.org/doc/stable/user/index.html)
- [`pandas`](https://pandas.pydata.org/)
- [`os`](https://docs.python.org/3/library/os.html)
- [`datatime`](https://docs.python.org/3/library/datetime.html) 
- [`time`](https://docs.python.org/3/library/time.html) 

## Example python scripts 
- [Steady-state simulations](https://github.com/ChengYangUmich/CY_SUMO/blob/main/examples/dynamicSimulation.py) 
-

