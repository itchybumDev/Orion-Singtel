import orionsdk
import requests
import Tkinter
import json
from datetime import datetime, date
import time
from influxdb import InfluxDBClient
import ast
import sys
from Tkinter import *
import threading
from tkMessageBox import askokcancel           

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
		print "New Database is Created"
		return 0
#=========================================GUI Interface===============================
class Quitter(Frame):                          
    def __init__(self, parent=None):           
        Frame.__init__(self, parent)
        self.pack()
        widget = Button(self, text='Quit', command=self.quit)
        widget.pack(expand=YES, fill=BOTH, side=LEFT)
    def quit(self):
        ans = askokcancel('Verify exit', "Really quit?")
        if ans: Frame.quit(self)

fields = 'SolarWindServer', 'ID', 'PASS', 'Query', 'InfluxdbServer', 'Port', 'ID', 'Pass', 'DBNAME'
samples = ['win-3vhamfq91kp', 'fish', 'swordfish', 'SELECT NodeID, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb']
def fetch(variables):
	global SolarWinds
	global SWID 
	global SWPass 
	global SQL
	global influxdb 
	global dbport 
	global dbID
	global dbPass
	global dbName
	global gotInput

	SolarWinds = variables[0].get()
	SWID = variables[1].get()
	SWPass = variables[2].get()
	SQL = variables[3].get()
	influxdb = variables[4].get()
	dbport = variables[5].get()
	dbID = variables[6].get()
	dbName = variables[8].get()
	dbPass = variables[7].get()
	#check for the latest entry in influxdb table
	def callback():
		print "thread started"
		t = 0.1
		t = t*60
		mostRecent = 0
		
		#====================================MAIN WORK==================================================
		start_time = time.time()
		if "DateTime" not in SQL:
			sys.exit("Please Insert DateTime to the Query for TimeSeries Data")

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
			client = InfluxDBClient(influxdb, dbport, dbID, dbPass, dbName)
			client.create_database(dbName)
			mostRecent = getRecentDateInflux(client)
			
			for i in range(len(rowsTitle)-1,-1,-1):
				if (convertUnixTime(rowsTitle[i]['DateTime']) < mostRecent):
					print "database is Updated"
					break
				print i
				onePoint = submitPoint(rowsTitle,measurement,i)
				L.append(onePoint)

			client.write_points(L)
			print(time.time()-start_time)
			print "executing again in " + str(t)+ " seconds"
			time.sleep(t);

	th=threading.Thread(target = callback)
	th.daemon = True
	th.start()

def makeform(root, fields, samples):
    form = Frame(root)                              
    left = Frame(form)
    rite = Frame(form)
    form.pack(fill=X) 
    left.pack(side=LEFT)
    rite.pack(side=RIGHT, expand=YES, fill=X)

    variables = []
    count = 0;
    for field in fields:
        lab = Label(left, width=20, text=field)
        ent = Entry(rite)
        lab.pack(side=TOP)
        ent.pack(side=TOP, fill=X)
        var = StringVar()
        ent.config(textvariable=var)
        variables.append(var)
        var.set(samples[count])
        count+=1

    return variables

if __name__ == '__main__':
	SolarWinds = ""
	SWID = ""
	SWPass = ""
	SQL = ""
	influxdb = ""
	dbport = ""
	dbID = ""
	dbPass = ""
	dbName = ""
	root = Tk()
	gotInput = False
	root.geometry('{}x{}'.format(600, 300))
	vars = makeform(root, fields, samples)
	Button(root, text='Start', width = 10,
                 command=(lambda v=vars: fetch(v))).pack(side=BOTTOM)
	Quitter(root).pack(side=RIGHT)
	root.bind('<Return>', (lambda event, v=vars: fetch(v)))
	#thread.start_new_thread(mainWork(),())
	root.mainloop()
	

#===============================================================================================



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

