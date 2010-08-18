#!/usr/bin/env python
"""
pynetstat works in similar way to netstat on windows but
exposes the information to display it in novel ways
*********
/TCP :: 192.168.1.100:1780 --> 66.102.11.100:80 :: 61448 :: ESTABLISHED
displays local address localport connected to remote address and port
then the process id accosiated with it and the connection status
"""
import openPorts

def getConnections():
    ''' get open connections from iphelperapi '''
    connections = openPorts.getOpenPorts()
    connections.sort()
    return connections

# tcp states for printout
tcpstate = ["","CLOSED","LISTEN","SYN_SENT","SYN_RCVD","ESTABLISHED","FIN_WAIT1",
            "FINWAIT2","CLOSE_WAIT","CLOSING","LAST_ACK","TIME_WAIT","DELETE_TCB"]


def printConnections(connectionList):
    ''' print out connections, tcp first then udp '''
    # list to add udp connections to
    udplist = []
    for a in connectionList:
        try:
            print "%s :: %s:%d --> %s:%d :: %d :: %s" % (a[6],a[0],a[1],a[2],a[3],a[4],tcpstate[a[5]])
        # udp connections don't have as many fields, so its easy enough to sort this way
        except IndexError:
            udplist.append(a)
    for b in udplist:
        print "%s :: %s:%d --> *.* :: %d :: LISTENING" % (b[3],b[0],b[1],b[2])

def main():
    ''' main function to run from direct call from cli '''
    connections = getConnections()
    printConnections(connections)
    
if __name__ == "__main__":
    main()