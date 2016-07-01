import orionsdk
import requests
import Tkinter
import json
from datetime import datetime, date
import time
from influxdb import InfluxDBClient
import ast
import sys

def convertUnixTime(str):
	date_object = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%f')
	unixtime = time.mktime(date_object.timetuple())
	unixtime = int(unixtime)
	return unixtime

def submitPoint(rowsTitle,measurement,entryNum):
	d = {"measurement": measurement.replace('.','')}
	d["time"] = rowsTitle[entryNum]['DateTime']
	del rowsTitle[entryNum]['DateTime']
	d["fields"] = rowsTitle[entryNum]
	return d

def getRecentDateInflux(client):
	result = client.query("SELECT * FROM OrionCPULoad ORDER by DESC LIMIT 1")
	temp_str = str(format(result))
	startIndex = temp_str.find("time")
	endIndex = temp_str.find("Z", startIndex)
	temp_date = (temp_str[startIndex:endIndex])[9:31]
	try:
		return convertUnixTime(temp_date)
	except:
		print "inside except"
		return 0
#===============================================================================================


SolarWinds = "win-3vhamfq91kp"
SWID = "fish"
SWPass = "swordfish"
SQL = "SELECT NodeID, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad"

influxdb = "192.168.201.129"
dbport = 8086
dbID = "root"
dbPass = "root"
dbName = "mydb"
t = 0.1
t = t*60
#check for the latest entry in influxdb table
mostRecent = 0
#====================================MAIN WORK==================================================
start_time = time.time()

if "DateTime" not in SQL:
	sys.exit("Please Insert DateTime to the Query for TimeSeries Data")

client = InfluxDBClient(influxdb, dbport, dbID, dbPass, dbName)
client.create_database(dbName)
while (True):
	#turn of the Certificate warning
	requests.packages.urllib3.disable_warnings()
	#getting query done. Prefer input as the locahost name rather than dynamic IP address.
	swis = orionsdk.SwisClient(SolarWinds, SWID, SWPass)
	data = swis.query(SQL)

	#preparing to get the titles and table name
	SQL_temp = SQL
	SQL_temp = SQL_temp.replace(',','')
	values = SQL_temp.split( )
	leng = len(values)

	#this loop is to get the title of each entry
	for x in range( 1, (leng-2)):
		values[x]

	#this line is to get the name of the table
	measurement = values[leng -1]
	data_str = json.dumps(data)
	data_list = ast.literal_eval(data_str)["results"]
	data_arr = json.loads(data_str)
	rowsTitle = data_arr["results"]
	L = []
	#open InfluxDB server to connect
	mostRecent = getRecentDateInflux(client)
	
	for i in range(len(rowsTitle)-1,-1,-1):
		if (convertUnixTime(rowsTitle[i]['DateTime']) < mostRecent):
			print "database is Updated"
			break
		print i
		onePoint = submitPoint(rowsTitle,measurement,i)
		L.append(onePoint)

	client.write_points(L)
	print "executing again in " + str(t)+ " seconds"
	time.sleep(t);

'''
Printing as Json file for checking
with open('data.txt', 'w') as outfile:
	json.dump(data, outfile)
'''

'''
toFile = "# DDL\n\nCREATE DATABASE IF NOT EXISTS NOAA_water_database\n\n# DML\n\n# CONTEXT-DATABASE: NOAA_water_database\n\n"
Printing to file for checking
for i in rowsTitle:
	line = measurement + " "
	for x in range(1, (leng-2)):
		if (values[x]=='DateTime'):
			line = line + values[x] + "=" + str(convertUnixTime(str(i[(values[x])]))) + " "
		else:
			line = line + values[x] + "=" + str(i[(values[x])]) + " "
	line = line + "\n"
	toFile += line

with open('dataInfluxdb.txt', 'w') as textfile:
	textfile.write(toFile)
'''
#creating a dict for data
'''
json_body = [
    {
        "measurement": "cpu_load_short",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        "time": "2009-11-10T23:00:00Z",
        "fields": {
            "value": 0.64
        }
    }
]
'''

