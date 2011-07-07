#!/usr/bin/env python
"""
Enumerates Processes to aquire process names and ids
uses - PSAPI to enumerate processes and
     - Kernel32 to get names of above processes
based on example at http://msdn.microsoft.com/en-us/library/ms682623(v=VS.85).aspx
and http://code.activestate.com/recipes/305279-getting-process-information-on-windows/
returns list of tuples with (pid,process name)
"""
import ctypes

# PSAPI.DLL
psapi = ctypes.windll.psapi
# Kernel32.DLL
kernel = ctypes.windll.kernel32

def getProcesses():
    """ get list of process names and ids in form (pid,process name) """
    DWORD = ctypes.c_ulong
    #define symbols that are needed for process access
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    # enum process buffers
    parr = DWORD * 1024
    aProcesses = parr()
    cbNeeded = DWORD(0)
    hModule = DWORD()
    modname = ctypes.c_buffer(30)
    processList = {}
    
    # get list of process ids
    psapi.EnumProcesses(ctypes.byref(aProcesses),
                        ctypes.sizeof(aProcesses),
                        ctypes.byref(cbNeeded))
    
    # get number of returned processes
    nReturned = cbNeeded.value/ctypes.sizeof(DWORD())
    # create python array without empty slots
    pidProcess = [ps for ps in aProcesses][:nReturned]
    
    for pid in pidProcess:
        # get handle to the process from the pid
        hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                      False, pid)
        if hProcess:
            # gets module handles and gets the name of module
            psapi.EnumProcessModules(hProcess, ctypes.byref(hModule),
                                     ctypes.sizeof(hModule), ctypes.byref(cbNeeded))
            psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, ctypes.sizeof(modname))
            # turns array into python string for later use
            pname = "".join([i for i in modname if i!= '\x00'])
            if pname == "":
                pname = "System"
            processList[pid]= pname
            
            # Clean up modname in case the next process name isn't as long
            for i in range(modname._length_):
                modname[i]='\x00'
            # Close handle
            kernel.CloseHandle(hProcess)
    
    #return list of processes and ids
    return processList

if __name__ == "__main__":
    psl = getProcesses()
    for pid, name in sorted(psl.items(), key=lambda x: (-1*x[1], x[0])):
        print "%d : %s" % (pid,name)
