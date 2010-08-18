## {{{ http://code.activestate.com/recipes/392572/ (r1)
# openPorts.py

import ctypes
import socket
import struct

def getOpenPorts():
    """
        This function will return a list of ports (TCP/UDP) that the current 
        machine is listening on. It's basically a replacement for parsing 
        netstat output but also serves as a good example for using the 
        IP Helper API:
        http://msdn.microsoft.com/library/default.asp?url=/library/en-
        us/iphlp/iphlp/ip_helper_start_page.asp.
        I also used the following post as a guide myself (in case it's useful 
        to anyone):
        http://aspn.activestate.com/ASPN/Mail/Message/ctypes-users/1966295
   
     """
    portList = []
    connectionList = []
           
    DWORD = ctypes.c_ulong
    NO_ERROR = 0
    NULL = ""
    bOrder = 0
    AF_INET = socket.AF_INET

    # define TCP_TABLE_OWNER_PID_ALL for extended tcp / udp tables
    TCP_TABLE_OWNER_PID_ALL = 5
    UDP_TABLE_OWNER_PID = 1
    # define some MIB constants used to identify the state of a TCP port
    MIB_TCP_STATE_CLOSED = 1
    MIB_TCP_STATE_LISTEN = 2
    MIB_TCP_STATE_SYN_SENT = 3
    MIB_TCP_STATE_SYN_RCVD = 4
    MIB_TCP_STATE_ESTAB = 5
    MIB_TCP_STATE_FIN_WAIT1 = 6
    MIB_TCP_STATE_FIN_WAIT2 = 7
    MIB_TCP_STATE_CLOSE_WAIT = 8
    MIB_TCP_STATE_CLOSING = 9
    MIB_TCP_STATE_LAST_ACK = 10
    MIB_TCP_STATE_TIME_WAIT = 11
    MIB_TCP_STATE_DELETE_TCB = 12
    
    ANY_SIZE = 1         
    
    # defing our MIB row structures
    class MIB_TCPROW(ctypes.Structure):
        _fields_ = [('dwState', DWORD),
                    ('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD),
                    ('dwRemoteAddr', DWORD),
                    ('dwRemotePort', DWORD)]
    
    class MIB_UDPROW(ctypes.Structure):
        _fields_ = [('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD)]

    class MIB_TCPROW_OWNER_PID(ctypes.Structure):
        _fields_ = [('dwState', DWORD),
                    ('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD),
                    ('dwRemoteAddr', DWORD),
                    ('dwRemotePort', DWORD),
                    ('dwOwningPid', DWORD)]

    class MIB_UDPROW_OWNER_PID(ctypes.Structure):
        _fields_ = [('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD),
                    ('dwOwningPid', DWORD)]
  
    dwSize = DWORD(0)
    
    # call once to get dwSize 
    ctypes.windll.iphlpapi.GetTcpTable(NULL, ctypes.byref(dwSize), bOrder)
    
    # ANY_SIZE is used out of convention (to be like MS docs); even setting this
    # to dwSize will likely be much larger than actually necessary but much 
    # more efficient that just declaring ANY_SIZE = 65500.
    # (in C we would use malloc to allocate memory for the *table pointer and 
    #  then have ANY_SIZE set to 1 in the structure definition)
    
    ANY_SIZE = dwSize.value
    
    class MIB_TCPTABLE(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_TCPROW * ANY_SIZE)]
    
    tcpTable = MIB_TCPTABLE()
    tcpTable.dwNumEntries = 0 # define as 0 for our loops sake
    # now make the call to GetTcpTable to get the data
    if (ctypes.windll.iphlpapi.GetTcpTable(ctypes.byref(tcpTable), 
        ctypes.byref(dwSize), bOrder) == NO_ERROR):
        maxNum = tcpTable.dwNumEntries
        placeHolder = 0
        # loop through every connection
        while placeHolder < maxNum:
            item = tcpTable.table[placeHolder]
            placeHolder += 1
            # format the data we need (there is more data if it is useful - 
            #    see structure definition)
            lPort = item.dwLocalPort
            lPort = socket.ntohs(lPort)
            lAddr = item.dwLocalAddr
            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))
            portState = item.dwState
            # only record TCP ports where we're listening on our external 
            #    (or all) connections
            if str(lAddr) != "127.0.0.1" and portState == MIB_TCP_STATE_LISTEN:
                portList.append(str(lPort) + "/TCP")
    else:
        print "Error occurred when trying to get TCP Table"

    

    # *********  JESSE JESSE JESSE *************
    # Adding TCP Table w/ Owner PID for netstat - like
    # Process Output

    dwSize = DWORD(0)
    # call once to get dwSize
    ctypes.windll.iphlpapi.GetExtendedTcpTable(NULL, ctypes.byref(dwSize), bOrder,
                                               AF_INET, TCP_TABLE_OWNER_PID_ALL, DWORD(0))
    ANY_SIZE = dwSize.value # again, used out of convention 
    #                            (see notes in TCP section)
    
    class MIB_TCPTABLE_OWNER_PID(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_TCPROW_OWNER_PID * ANY_SIZE)]

    tcpTableOwnerPid = MIB_TCPTABLE_OWNER_PID()
    tcpTableOwnerPid.dwNumEntries = 0 # defined as 0 as for other structures

    # now make the call to GetTcpTable to get the data
    if (ctypes.windll.iphlpapi.GetExtendedTcpTable(ctypes.byref(tcpTableOwnerPid),
        ctypes.byref(dwSize), bOrder, AF_INET, TCP_TABLE_OWNER_PID_ALL, DWORD(0)) == NO_ERROR):

        maxNum = tcpTableOwnerPid.dwNumEntries
        placeHolder = 0

        while placeHolder < maxNum:

            item = tcpTableOwnerPid.table[placeHolder]
            placeHolder += 1

            #format the data we need from network reprs to local reprs
            lPort = item.dwLocalPort
            lPort = socket.ntohs(lPort)
            lAddr = item.dwLocalAddr
            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))
            rPort = item.dwRemotePort
            rPort = socket.ntohs(rPort)
            rAddr = item.dwRemoteAddr
            rAddr = socket.inet_ntoa(struct.pack('L', rAddr))
            pid = item.dwOwningPid
            pid = socket.ntohs(pid)
            portState = item.dwState
            # add above to connectionList as item
            connectionList.append([lAddr,lPort,rAddr,rPort,pid,portState, "/TCP"])
    else:
        print "Error occurred when trying to retreive TCP table"
        
    # ***************************************************************
    # on to udp again reset sizes
    dwSize = DWORD(0)
    # call once to get dwSize
    ctypes.windll.iphlpapi.GetUdpTable(NULL, ctypes.byref(dwSize), bOrder)

    ANY_SIZE = dwSize.value # again, used out of convention 
    #                            (see notes in TCP section)
    class MIB_UDPTABLE(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_UDPROW * ANY_SIZE)]  
                    
    udpTable = MIB_UDPTABLE()
    udpTable.dwNumEntries = 0 # define as 0 for our loops sake
    
    # now make the call to GetUdpTable to get the data
    if (ctypes.windll.iphlpapi.GetUdpTable(ctypes.byref(udpTable), 
        ctypes.byref(dwSize), bOrder) == NO_ERROR):
    
        maxNum = udpTable.dwNumEntries
        placeHolder = 0
        while placeHolder < maxNum:

            item = udpTable.table[placeHolder]
            placeHolder += 1
            lPort = item.dwLocalPort
    
            lPort = socket.ntohs(lPort)
            lAddr = item.dwLocalAddr
            
            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))
            
            # only record UDP ports where we're listening on our external 
            #    (or all) connections
            if str(lAddr) != "127.0.0.1":
                portList.append(str(lPort) + "/UDP")
    else:
        print "Error occurred when trying to get UDP Table"
    
    # next table, reset sizes again
    dwSize = DWORD(0)
    ctypes.windll.iphlpapi.GetExtendedUdpTable(NULL, ctypes.byref(dwSize), bOrder,
                                               AF_INET, UDP_TABLE_OWNER_PID, DWORD(0))
    ANY_SIZE = dwSize.value # used out of convention,
    #
    class MIB_UDPTABLE_OWNER_PID(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_UDPROW_OWNER_PID * ANY_SIZE)]
        
    udpTableOwnerPid = MIB_UDPTABLE_OWNER_PID()
    udpTableOwnerPid.dwNumEntries = 0 # defined as 0 for sake of loop
    
    #make the call to GetExtendedUdpTable to get the data
    if (ctypes.windll.iphlpapi.GetExtendedUdpTable(ctypes.byref(udpTableOwnerPid),
        ctypes.byref(dwSize), bOrder, AF_INET, UDP_TABLE_OWNER_PID, DWORD(0)) == NO_ERROR):
        
        maxNum = udpTableOwnerPid.dwNumEntries
        placeHolder = 0
        while placeHolder < maxNum:
            
            item = udpTableOwnerPid.table[placeHolder]
            placeHolder += 1
            
            # get info
            lPort = item.dwLocalPort
            lAddr = item.dwLocalAddr
            pid = item.dwOwningPid
            
            # format info to local reprs
            lPort = socket.ntohs(lPort)
            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))
            pid = socket.ntohs(pid)
            
            #add connections to list
            connectionList.append([lAddr,lPort,pid, "/UDP"])
            
    else:
        print "Error occurred while trying to aquire UDP Table"
    
    portList.sort()  
    
    # not required now??
    # now going to only return full pid list
    #return portList
    return connectionList

ListofOpenPorts = getOpenPorts()
## end of http://code.activestate.com/recipes/392572/ }}}