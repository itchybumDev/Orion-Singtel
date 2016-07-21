import orionsdk
import requests
import json
import ast
import sys
import threading
import time
import os.path
import pyodbc
from datetime import datetime, date
from influxdb import InfluxDBClient
from Tkinter import *
from tkMessageBox import askokcancel
from tkMessageBox import showinfo
import pyodbc
import datetime

def show_odbc_sources(SQL,host,DBName,ID,PWD):
	connectStr = "DRIVER={SQL Server};SERVER="+host+";DATABASE="+DBName+";UID="+ID+";PWD="+PWD+";Trusted_Connection=yes"
	cnxn = pyodbc.connect(connectStr)
	cursor = cnxn.cursor()
	measurement=getMeasurement(SQL)
	fieldsArr = getFields(SQL)
	cursor.execute(SQL)
	row = cursor.fetchone()
	exportArr=[]
	while row is not None:
		#process the a Point data here
		dataPoint=parsePoint(fieldsArr,list(row))
		d = {"measurement": measurement.replace('.','')}
		try:
			d["time"] = (dataPoint['DateTime'])
			del dataPoint['DateTime']
		except:
			print "There is no Value DateTime in the Query. please check \n Program has STOPPED"
			sys.exit()
		temp_data= getTags(dataPoint)
		d["tags"] = temp_data[0]
		d["fields"] = temp_data[1]
		exportArr.append(d)
		#finish processing a Point data
		row = cursor.fetchone()
	return exportArr

def parsePoint(fields,data):
	d={}
	count=0
	for field in fields:
		d[field]=data[count]
		count+=1
	return d

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
	
def getMeasurement(s):
	#starting index of 'from'
	index_str = (s.lower()).find("from")
	index_str = index_str + 5
	tmp = s[index_str:]
	ans = tmp.split(' ',1)[0]
	return ans

def getFields(SQL):
	sql_temp = SQL.replace(',','')
	sql_temp = ' '.join(sql_temp.split())
	sql_temp = sql_temp[sql_temp.index(' '):]
	sql_temp = sql_temp[:(sql_temp.lower()).index('from')]
	sql_temp = ' '.join(sql_temp.split())
	array = sql_temp.split(' ')
	return array
	
def adjustMinute(SQL,period):
	SQL=SQL.replace('day','minute',1)
	indexOfBetween=SQL.index('between')
	SQL=SQL[:indexOfBetween] +'between 0 and ' + str(period)
	return SQL

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
		#sys.exit()()
	del rowsTitle[entryNum]['DateTime']
	temp_data= getTags(rowsTitle[entryNum])
	d["tags"] = temp_data[0]
	d["fields"] = temp_data[1]
	print temp_data[1]
	return d
def showMsg(s):
	showinfo("Error",message=s)

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
	if ('datadiff' in s.lower()):
		return s
	if ("where" not in s.lower()):
		s = s + " WHERE DATEDIFF(day,DateTime,getdate()) between 0 and " + str(period)
	else:
		where = s[(s.lower()).find('where'):]
		a = where.find('and') 
		g = where.find('group')
		o = where.find('order')
		if (a!=-1 or g!=-1 or o!=-1):
			where = where[:max(a,g,o)] + ' and DATEDIFF(day,DateTime,getdate()) between 0 and ' + str(period) + where[max[a,o,g]:]
			s = s[:(s.lower()).find('where')]
		else:
			s = s+ ' and DATEDIFF(day,DateTime,getdate()) between 0 and '+ str(period)
	return s
def fetch(variables):
	try:
		int(variables[11].get())
		float(variables[10].get())
		int(variables[6].get())
	except:
		showMsg("Please input Number for Minutes/Days and Port")
		sys.exit()()

	host=variables[0].get()
	DBName=variables[1].get()
	ID=variables[2].get()
	PWD=variables[3].get()
	SQL = variables[4].get()
	influxdb = variables[5].get()
	dbport = variables[6].get()
	dbID = variables[7].get()
	dbPass = variables[8].get()
	dbName = variables[9].get()
	t = float(variables[10].get()) * 60.0
	day = int(variables[11].get())
	#replace multiple whitespaces with 1 whitespace
	SQL = ' '.join(SQL.split())
	SQL = handleSQL(SQL,day)

	#====================================MAIN WORK==================================================
	def callback():
		print "Starting to pipe Data ORION --> Influxdb"
		if SQL.count('DateTime')<2:
			print 'Please Insert DateTime to the Query for TimeSeries Data'
			sys.exit()
	#========================open InfluxDB server to connect
		try:
			client = InfluxDBClient(influxdb, dbport, dbID, dbPass, dbName)
			client.create_database(dbName)
		except:
			print ("InfluxDb server/port/ID or Pass is wrong")
			##sys.exit()()
	#=======================Connect to Microsoft OCDB SQL server===============
		
		firstTime=1
		firstInput=1
		while (True):
			start_time=time.time()
			if (firstInput==0):
				subSQL=adjustMinute(SQL,round(t/60))
				firstInput=-1
			if (firstInput==1):
				firstInput=0
			try:
				if (firstInput==-1):
					L = show_odbc_sources(subSQL,host,DBName,ID,PWD)
				else:
					L = show_odbc_sources(SQL,host,DBName,ID,PWD)
			except:
				print ("SQL Server or ID or Pass is wrong")
				sys.exit()
			
			if not L: #if no new point is added to L, dont post anything
	 			print "Database is up to date"#useless code, just for syntax purpose
			else:
				print "Submit " +str(len(L))+" point(s)"
				client.write_points(L)
			
			print "\n Update Database: " + dbName
			runTime = time.time()-start_time
			print " Run time " + str(runTime)
			if (int(runTime) > 120 ):
				delayBy = (runTime + 61)/60
			print " Executing again in " + str(t)+ " seconds from " + str(datetime.datetime.now())+ "\n\n"
			time.sleep(t);
			firstTime=False
	#====================================End of MAIN WORK==================================================		
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
			'SELECT c.NodeID, Caption, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, c.TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM CPULoad c , Nodes n where c.NodeID = n.NodeID ',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb', 2, 30]
	return sample
	
fields = 'SQL Server','DBName', 'ID', 'Pass', 'Query', 'InfluxdbServer', 'Port', 'ID', 'Pass', 'DBNAME', 'Update Period (mins)', 'How many days back?'


if __name__ == '__main__':
	root = Tk()
	root.title("SQL to InfluxDB")
	gotInput = False
	root.geometry('{}x{}'.format(600, 300))
	#finding the Config File
	if os.path.isfile('Config.txt'):
		samples = getSamplesFromFile()
	else:
		samples = ['localhost','SolarWindsOrion', 'fish', 'swordfish', 
			'SELECT c.NodeID, Caption, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, c.TotalMemory, MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM CPULoad c , Nodes n where c.NodeID = n.NodeID ',
			'192.168.201.129', 8086 , 'root', 'root', 'mydb', 0.2, 1]
	vars = makeform(root, fields, samples)	
	Button(root, text='Start', width = 10,
	        command=(lambda v=vars: fetch(v))).pack(side=BOTTOM)
	Quitter(root).pack(side=RIGHT)
	root.bind('<Return>', (lambda event, v=vars: fetch(v)))
	#thread.start_new_thread(mainWork(),())
	root.mainloop()
	

#===============================================================================================
