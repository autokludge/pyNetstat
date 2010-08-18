pyNetstat
=========

pyNetstat is a netstat like program using the iphelper api
and the process api to view connections and to disconnect

Files
-----
* openPorts.py -- Based on [Recipe 392572](http://code.activestate.com/recipes/392572-using-the-win32-iphelper-api/) by Zeb Bowden, wrapping the IP helper API
                    to aquire the current open connections and udp bindings.
* pidnames.py -- Wrapper for the Process API (psapi) to get process names from process ids (pid)
* pynetstat.py -- currently dumps open connections to cli, in future gui with connection management
                    and different views (sorting, expandable tree)