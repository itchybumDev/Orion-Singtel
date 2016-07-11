import orionsdk
import requests
import json
import ast
import sys
import threading
import time
import os.path
from datetime import datetime, date
from influxdb import InfluxDBClient
from Tkinter import *
from tkMessageBox import askokcancel
from tkMessageBox import showinfo


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
	try:
		d["time"] = (rowsTitle[entryNum]['DateTime'])
	except:
		print "There is no Value DateTime in the Query. please check \n Program has STOPPED"
		sys.exit()
	del rowsTitle[entryNum]['DateTime']
	temp_data= getTags(rowsTitle[entryNum])
	d["tags"] = temp_data[0]
	d["fields"] = temp_data[1]
	return d
def showMsg(s):
	showinfo("Error",message=s)

def getTags(d):
	tags=['IPAddress','Caption','NodeDescription','DNS','SysName','Vendor','DisplayName','NodeID',
			'SysObjectID','Location','Contact','IOSVersion','AgentPort','EngineID','IP',
			'IP_Address','NodeName','IPAddressGUID','EntityType']
	keys = d.keys()
	ans = {}
	for key in keys:
		if any( key in tag for tag in tags):
			ans[key]=d[key]
			del d[key]
	return (ans,d)
'''
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
'''
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

def handleSQL(s, period):
	if ("where" not in s.lower()):
		s = s + " WHERE DateTime > ADDDAY(-"+ str(period)+",GETUTCDATE())"
	else:
		where = s[(s.lower()).find('where'):]
		a = where.find('and') 
		g = where.find('group')
		o = where.find('order')
		if (a!=-1 or g!=-1 or o!=-1):
			where = where[:max(a,g,o)] + ' and DateTime > ADDDAY(-'+ str(period)+',GETUTCDATE()) ' + where[max[a,o,g]:]
			s = s[:(s.lower()).find('where')]
		else:
			s = s+ ' and DateTime > ADDDAY(-'+ str(period)+',GETUTCDATE()) '

	if ("order" not in s.lower()):
		s = s + " ORDER BY DateTime desc"
	return s

def fetch(variables):
	try:
		int(variables[10].get())
		float(variables[9].get())
		int(variables[5].get())
	except:
		showMsg("Please input Number for Minutes/Days and Port")
		sys.exit()

	SolarWinds = variables[0].get()
	SWID = variables[1].get()
	SWPass = variables[2].get()
	SQL = variables[3].get()
	influxdb = variables[4].get()
	dbport = variables[5].get()
	dbID = variables[6].get()
	dbPass = variables[7].get()
	dbName = variables[8].get()
	t = float(variables[9].get()) * 60.0
	day = int(variables[10].get())
	#replace multiple whitespaces with 1 whitespace
	SQL = ' '.join(SQL.split())
	SQL = handleSQL(SQL,day)
	#check for the entry in influxdb table

	#====================================MAIN WORK==================================================
	def callback():
		print "Starting to pipe Data ORION --> Influxdb"
		if SQL.count('DateTime')<=2:
			print 'Please Insert DateTime to the Query for TimeSeries Data'
			sys.exit()
		#open InfluxDB server to connect
		try:
			client = InfluxDBClient(influxdb, dbport, dbID, dbPass, dbName)
			client.create_database(dbName)
		except:
			print ("InfluxDb server/port/ID or Pass is wrong")
			sys.exit()
		#open SolarWinds server to connect
		swis = orionsdk.SwisClient(SolarWinds, SWID, SWPass)
		latestPointSW = {}
		#var to load 1 day-worth of data at first use, then only a short peiod afterwards
		firstInput = 1
		#minute-worth of data for loading Solarwinds Database (in minutes)
		delayBy = 2
		while (True):
			if (firstInput==0):
				a = SQL.replace(('ADDDAY(-'+str(day)),'ADDMINUTE(-'+str(int(t/60)+delayBy),1)
				firstInput=-1
			if (firstInput==1):
				firstInput=0
			start_time = time.time()

			#turn of the Certificate warning
			requests.packages.urllib3.disable_warnings()
			#getting query done 
			try:
				if (firstInput==-1):
					data = swis.query(a)
				else:
					data = swis.query(SQL)
			except:
				print ("SolarWinds Server or ID or Pass is wrong")
				sys.exit()
			#preparing to get the titles and table name
			SQL_temp = SQL
			SQL_temp = SQL_temp.replace(',','')
			#this line is to get the Series Name
			measurement = getMeasurement(SQL_temp)
			data_str = json.dumps(data)
			data_arr = json.loads(data_str)
			try:
				rowsTitle = data_arr["results"]
			except:
				print "Error in Query Request Please check Syntax Again"
				sys.exit()
			
			L = []
			for i in range(0,len(rowsTitle)):
				onePoint=submitPoint(rowsTitle,measurement,i)
				#Check to see which is the latest point posting to InfluxDB
				if (cmp(latestPointSW,onePoint)==0):
					print "Database is Up-To-Date"
					break
				L.append(onePoint)
			
			if not L: #if no new point is added to L, dont post anything
 				p=1 #useless code, just for syntax purpose
			else:
				print "Submit " +str(len(L))+" point(s)"
				latestPointSW = L[0]
				client.write_points(L)
			
			print "\n Update Database: " + dbName
			runTime = time.time()-start_time
			print " Run time " + str(runTime)
			if (int(runTime) > 120 ):
				delayBy = (runTime + 61)/60
			print " Executing again in " + str(t)+ " seconds from " + str(datetime.now())+ "\n\n"
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
        ent.config(borderwidth=2)
        variables.append(var)
        var.set(samples[count])
        count+=1
    return variables

def getSamplesFromFile():
	f = open('Config.txt','r')
	finput = f.readlines()
	sample=[]
	for i in range(0,len(finput)):
		tmp =finput[i][(finput[i].find('=')+1):]
		tmp = tmp.replace('\n','')
		if (i!=3):
			tmp = tmp.replace(' ','')
		tmp = tmp.replace('"','')
		sample.append(tmp)
	if (len(sample)!=11):
		sample = samples = ['win-3vhamfq91kp', 'fish', 'swordfish', 
			'SELECT c.NodeID, IPAddress, IPAddressType, Caption, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, c.TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad c , Orion.Nodes n where c.NodeID = n.NodeID',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb', 2, 30]
	return sample
	
fields = 'SolarWindServer', 'ID', 'Pass', 'Query', 'InfluxdbServer', 'Port', 'ID', 'Pass', 'DBNAME', 'Update Period (mins)', 'How many days back?'


if __name__ == '__main__':
	root = Tk()
	root.title("SolarWinds to InfluxDB")
	gotInput = False
	root.geometry('{}x{}'.format(600, 300))
	#finding the Config File
	if os.path.isfile('Config.txt'):
		samples = getSamplesFromFile()
	else:
		samples = ['win-3vhamfq91kp', 'fish', 'swordfish', 
			'SELECT c.NodeID, IPAddress, IPAddressType, Caption, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, c.TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad c , Orion.Nodes n where c.NodeID = n.NodeID',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb', 2, 30]

	vars = makeform(root, fields, samples)	
	Button(root, text='Start', width = 10,
	        command=(lambda v=vars: fetch(v))).pack(side=BOTTOM)
	Quitter(root).pack(side=RIGHT)
	root.bind('<Return>', (lambda event, v=vars: fetch(v)))
	#thread.start_new_thread(mainWork(),())
	root.mainloop()
	

#===============================================================================================
