import ctypes
from ctypes import POINTER, CFUNCTYPE
from ctypes import c_double, c_int, c_uint, c_short
from ctypes import c_char, c_char_p, c_longlong, c_ulonglong
import time
import os

import platform
import sys

class Duration:
    msec = 1
    sec  = 1000 * msec
    min  = 60 * sec
    hour = 60 * min
    day  = 24 * hour
    week = 7 * day



class SumoScheduler:
    def __init__(self, sumoPath=""):
        # Preparing some convenience member fields.
        self.version = 'Sumo21'
        self.platform_name = ''
        self.message_callback = None
        self.datacomm_callback = None
        self.scheduledJobs = 0
        self._load_sumo(sumoPath)
        self.jobData = { }
        self.dur = Duration()
        self.persistent = "persistent"
    def _load_sumo(self, sumoPath=""):
        library_prefix = ''
        library_ext = ''
        self.platform_name = platform.system()
        if self.platform_name == 'Windows':
            library_ext = 'dll'
            library_prefix = ''
            import winreg
            
            def getInstallLocation():            
                aKey = "SOFTWARE\\Dynamita\\" + self.version +"\\PATHS"
                aReg = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
                try:
                    aKey = winreg.OpenKey(aReg, aKey)
                    val = winreg.QueryValueEx(aKey, "INST")
                    return val[0]
                except:            
                    aKey = "SOFTWARE\\Dynamita\\" + self.version +"\\PATHS"
                    aReg = winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
                    try:
                        aKey = winreg.OpenKey(aReg, aKey)
                        val = winreg.QueryValueEx(aKey, "INST")
                        return val[0]
                    except:
                        return ""
                        
            if sumoPath == "":
                sumoPath = getInstallLocation()
            if sumoPath == "":
                raise FileNotFoundError(self.version + 'is not installed')
            if sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 8):
                os.add_dll_directory(sumoPath) # Python 3.8
        elif self.platform_name == 'Linux':
            library_ext = 'so'
            library_prefix = 'lib'
        elif self.platform_name == 'Darwin':
            library_ext = 'dylib'
            library_prefix = 'lib'
        else:
            raise NotImplementedError('Unsupported platform.')

        core_filename = os.path.join(
            sumoPath, library_prefix + "sumoscheduler." + library_ext
        )
        if os.path.isfile(core_filename):
            cwd = os.getcwd()
            os.chdir(sumoPath)
            self.scheduler = ctypes.cdll.LoadLibrary(core_filename)
            os.chdir(cwd)
        else:
            raise FileNotFoundError('Core file not found: ' + core_filename)

        self.scheduler.schedule.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
        self.scheduler.schedule.restype = c_int
        self.scheduler.setParallelJobs.argtypes = [c_int]
        self.scheduler.setMaxJobReuse.argtypes = [c_int]
        self.scheduler.finish.argtypes = [c_int]
        self.scheduler.sendCommand.argtypes =[c_int, c_char_p]
        self.scheduler.setLogDetails.argtypes = [c_int]
        
        
        def convertToData(s):
            if (";" in s):
                result = []
                for item in s.split(";"):
                    result.append(convertToData(item))
                return result
            try:
                return float(s)            
            except ValueError:
                return s        
        
        def internal_datacomm_callback(job, msg):            
            if self.datacomm_callback is not None:
                data = {}
                lst = msg.decode('utf8').split("|")
                for pair in lst:
                    args = pair.split(" = ")
                    data[args[0]] = convertToData(args[1])
                self.datacomm_callback(job, data)
            return 0

        def internal_message_callback(job, msg):            
            if (msg is not None) and (self.message_callback is not None):
                self.message_callback(job, msg.decode('utf8'))
            return 0;
        
        CALLBACKFUNC = ctypes.CFUNCTYPE(c_int, c_int, c_char_p)
        self.c_message_callback = CALLBACKFUNC(internal_message_callback) 
        self.c_datacomm_callback = CALLBACKFUNC(internal_datacomm_callback) 
        
        self.scheduler.register_message_callback.argtypes = [CALLBACKFUNC]
        self.scheduler.register_message_callback(self.c_message_callback)
        self.scheduler.register_datacomm_callback.argtypes = [CALLBACKFUNC]
        self.scheduler.register_datacomm_callback(self.c_datacomm_callback)
        
    def schedule (self, model, commands, variables, blockDatacomm=False, jobData=None):
        varstr = "|".join(variables)
        self.scheduledJobs += 1      
        id = self.scheduler.schedule(model.encode("utf8"), (";".join(commands)).encode("utf8"), varstr.encode("utf8"), int(blockDatacomm))
        self.jobData[id] = jobData
       
    def setParallelJobs(self, jobs):
        self.scheduler.setParallelJobs(jobs)
        
    def setMaxJobReuse(self, reuse):
        self.scheduler.setMaxJobReuse(reuse)
        
    def finish(self, job):
        self.scheduledJobs -= 1
        self.scheduler.finish(job)
        if (self.jobData[job] == None or not (self.persistent in self.jobData[job]) or  self.jobData[job][self.persistent] != True):
            del self.jobData[job]
        
    def sendCommand(self, job, command):
        self.scheduler.sendCommand(job, command.encode("utf8"))
               
    def getJobData(self, jobId):
        return self.jobData[jobId]
        
    def isSimFinishedMsg(self, msg):
        return msg.startswith("530004")

    def setLogDetails(self, level):
        self.scheduler.setLogDetails(level)

    def cleanup(self):
        self.jobData.clear()
        self.scheduler.cleanup()
        
    def frange(self, start, end, step):
        result = []
        count = round((end - start) / step)
        for i in range(count):
            result.append(i * step + start)
        result.append(end)
        return result
        
