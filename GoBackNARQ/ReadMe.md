**IP Project 2:**  Go Back N Protocol over UDP

**Team**
1.. Sai Kiran Mayee Maddi(smaddi) - 200257327
2. Abhishek Arya(aarya) - 200206728

This application is coded and tested on Python 3. 

Following are the steps to run the application -   

**Step 1 - Server Setup:**  
<ul>
<li> 1. Navigate to the server directory where server.py file is located. </li>
<li> 2. Run Server file server.py using the following command: </li>
    <li> python server.py <portNumber: 7735> <fileName: serverTest.txt>  <probability: 0.05 > (if only python 3 is installed in your system) </li>
    <li> python3 server.py <portNumber: 7735> <fileName: serverTest.txt> <probability: 0.05 >  (if multiple version of python is installed)  </li>
   <li>  **Example:** python server.py 7735 'serverTest.txt' 0.05 </li>
</ul>

**Step 2 - Client Setup:**  
1. Navigate to the client directory where client.py file is located and run the command after knowing the server IP address:
    python client.py <serverIP> <serverPortNumber: 7735> <fileName :clientTest.txt> <N window size: 64> <MSS: 600> (if only python 3 is installed in your system)
    python3 client.py <serverIP > <serverPortNumber: 7735> <fileName :clienttest.txt> <N window size: 64> <MSS :600> (if multiple version of python is installed)
    **Example:** python client.py 198.62.08.96 7735 'clientTest.txt' 64 600

The time taken to execute the program is displayed by client.py
**NOTE:** Run step 1 and step 2 in the same order. 
