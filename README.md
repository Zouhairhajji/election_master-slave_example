# Election slave/master

the program becomes slave is the master is down
when the master is down, one of the slaves become master, knowing that if the user requests an url from slave, the request will be transmitted to the master 

### Prerequisites

  in order to execute this example, you need to have 
     - redis using port : 6379
     - python with modules :
          - Flask, request, redirect, Resource, Api, dumps, jsonify, create_engine, redis, logging, Queue
  in order to execute this example, you need to execute (port = 10001) : 
    - python series-manager-server-ft.py 10001 $(uuidgen)
    

### Examples
  python series-manager-server-ft.py 10000 $(uuidgen)  # for master
  python series-manager-server-ft.py 10001 $(uuidgen)  # for slave1
  python series-manager-server-ft.py 10002 $(uuidgen)  # for slave2
  python series-manager-server-ft.py 10003 $(uuidgen)  # for slave3
  python series-manager-server-ft.py 10004 $(uuidgen)  # for slave4
