
Orion To Influxdb
1. Purpose
The program is designed to transfer SELECTED* data points from SolarWinds Orion Database to InfluxDB Database; which can be used with existing Grafana Dashboard. Furthermore, data manipulation from InfluxDB Admin Console (http://locahost:8083) is relatively easier than using SolarWinds Software.

2. Installation & Manual
Step 1: Navigate to OrionToInfluxdb folder



Step 2: Locate OrionToInfluxdb.exe file. Double click to RUN 

Step 3: The GUI will pop up along with Command Prompt (2 Panels).



SolarWindServer: This is the IP address or Machine Name, on which your _ SolarWinds _ is running. Eg: 192.168.1.1 or localhost or *machineName*
ID: Authorization ID for Solarwinds Server. Eg: admin
Pass: Authorization Password for Solarwinds Server. Eg: admin
Query: Query String for data that you want to pipe from SolarWinds to InfluxDB, remember to include *DateTime* as the software is expecting time series database. Eg: SELECT NodeID, DateTime, MinLoad FROM Orion.CPULoad
*Note: Do not input Data Manipulation Keywords like *Order by*, etc. Since it is not necessary to order or group the data.

InfluxdbServer: : This is the IP address or Machine Name, on which your _ InfluxDB _ is running. Eg: 192.168.1.1 or localhost or *machineName*
Port: The port number that your InfluxDB server. Eg: (Default) 8086
ID: Authorization ID for Solarwinds Server. Eg: root
Pass: Authorization Password for Solarwinds Server. Eg: root
DBNAME: Give your new database a Name. Eg: mydb
Update Period (mins): How frequent do you want to update your InfluxDB database. Eg: 1 (every 1 minute)
How many months back: This is useful for the very first time loading the Database from _ SolarWinds _ to _ InfluxDb _¸which indicate how long ago the data should be loaded. Eg: 1 (1 month)
Step4: Start importing data to Influxdb. Command Prompt will indicate the process has started.



Step 5: Keep BOTH windows running in background to ensure the data is updated every *Period* minutes interval. And carry on with your work.

Extra: You can set default Server IP, Server ID, Server Password and the rest of the fields by editing the Config.txt file (place the file inside the same folder as your OrionToInfluxdb.exe ).



3. Source Code
The program is building using Python 2.7. The source code is included* in the package with the name OrionToInfluxdb.py . Detail code explanation can found inside the code (written as comment)

Code Summary:

Establish connection to SolarWinds Server
Establish connection to InfluxDB Server
Checking Query String for parsing purposes
Request data (using Query String) from SolarWinds Sever
Process the returned result from SolarWinds
Post processed data to InfluxDB
Repeat every *minutes interval
4. Author
Name: Nguyen Luong Chuong Thien

Last updated: July 5, 2016

Email: terryn@ncs.com.sg or nl.chuongthien@u.nus.edu
