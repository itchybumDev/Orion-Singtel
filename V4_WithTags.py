import orionsdk
import requests
import Tkinter
import json
import ast
import sys
import threading
import time
from datetime import datetime, date
from influxdb import InfluxDBClient
from Tkinter import *
from tkMessageBox import askokcancel

def convertUnixTime(str):
	str = str[:str.find('.')]
	date_object = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')
	unixtime = time.mktime(date_object.timetuple())
	unixtime = int(unixtime)
	return unixtime
def convertToUTC(posix_time):
	return datetime.utcfromtimestamp(posix_time).strftime('%Y-%m-%dT%H:%M:%SZ')

def submitPoint(rowsTitle,measurement,entryNum):
	d = {"measurement": measurement.replace('.','')}
	d["time"] = (rowsTitle[entryNum]['DateTime'])
	del rowsTitle[entryNum]['DateTime']
	temp_data= getTags(rowsTitle[entryNum])
	d["tags"] = temp_data[0]
	d["fields"] = temp_data[1]
	return d

def getTags(d):
	tags=['IPAddress','Caption','NodeDescription','DNS','SysName','Vendor','DisplayName']
	keys = d.keys()
	ans = {}
	for key in keys:
		if any( key in tag for tag in tags):
			ans[key]=d[key]
			del d[key]
	return (ans,d)

def getRecentDateInflux(client):
	print("Loading influxDB Database...")
	result = client.query("SELECT * FROM OrionCPULoad ORDER by DESC LIMIT 1")
	temp_str = str(format(result))
	startIndex = temp_str.find("time")
	endIndex = temp_str.find("Z", startIndex)
	temp_date = (
		emp_str[startIndex:endIndex])[9:31]
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

def handleSQL(s):
	if ("order" not in s.lower()):
		s = s + " ORDER BY DateTime desc"
	return s

def fetch(variables):
	SolarWinds = variables[0].get()
	SWID = variables[1].get()
	SWPass = variables[2].get()
	SQL = variables[3].get()
	SQL = handleSQL(SQL)
	influxdb = variables[4].get()
	dbport = variables[5].get()
	dbID = variables[6].get()
	dbPass = variables[7].get()
	dbName = variables[8].get()
	t = float(variables[9].get()) * 60.0
	#check for the latest entry in influxdb table
	#====================================MAIN WORK==================================================
	def callback():
		print "Starting to pipe Data ORION --> Influxdb"

		if "DateTime" not in SQL:
			print "Please Insert DateTime to the Query for TimeSeries Data"
			sys.exit()

		client = InfluxDBClient(influxdb, dbport, dbID, dbPass, dbName)
		client.create_database(dbName)
		#open InfluxDB server to connect
		while (True):
			#turn of the Certificate warning
			start_time = time.time()
			requests.packages.urllib3.disable_warnings()
			#getting query done. Prefer input as the locahost name rather than dynamic IP address.
			swis = orionsdk.SwisClient(SolarWinds, SWID, SWPass)
			try:
				data = swis.query(SQL)
			except:
				print ("SolarWinds ID or Pass is wrong")
				sys.exit()
			#preparing to get the titles and table name
			SQL_temp = SQL
			SQL_temp = SQL_temp.replace(',','')
			#this line is to get the name of the table
			measurement = getMeasurement(SQL_temp)
			seriesName = measurement
			data_str = json.dumps(data)
			data_arr = json.loads(data_str)
			rowsTitle = data_arr["results"]
			L = []
			for i in range(0,len(rowsTitle)-1):
				#if (convertUnixTime(rowsTitle[i]['DateTime']) < mostRecent):
				#	print "Database is Up-To-Date"
				#	break
				onePoint=submitPoint(rowsTitle,measurement,i)
				L.append(onePoint)
			print L[0]
			client.write_points(L)
			print "Run time " + str((time.time()-start_time))
			print "Executing again in " + str(t)+ " seconds\n\n\n"
			time.sleep(t);
	#====================================End of MAIN WORK==================================================		
	th=threading.Thread(target = callback)
	th.daemon = True
	th.start()

def getMeasurement(s):
	#starting index of 'from'
	index_str = (s.lower()).find("from")
	index_str = index_str + 5
	tmp = s[index_str:]
	ans = tmp.split(' ',1)[0]
	return ans

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
        if (field == 'Pass'):
        	ent.config(textvariable=var)
        	ent.config(show="*")
        else:
        	ent.config(textvariable=var)
        variables.append(var)
        var.set(samples[count])
        count+=1
    return variables

fields = 'SolarWindServer', 'ID', 'Pass', 'Query', 'InfluxdbServer', 'Port', 'ID', 'Pass', 'DBNAME', 'Update Period'
samples = ['win-3vhamfq91kp', 'fish', 'swordfish', 'SELECT DateTime, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb', 10]

if __name__ == '__main__':
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
