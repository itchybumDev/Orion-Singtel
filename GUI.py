from Tkinter import *
from tkMessageBox import askokcancel           

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
	SolarWinds = variables[0]
	SWID = variables[1]
	SWPass = variables[2]
	SQL = variables[3]
	influxdb = variables[4]
	dbport = variables[5]
	dbID = variables[6]
	dbPass = variables[7]
	dbName = variables[8]

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
    root = Tk()
    root.geometry('{}x{}'.format(600, 300))
    vars = makeform(root, fields, samples)
    Button(root, text='Start', width = 10,
                 command=(lambda v=vars: fetch(v))).pack(side=BOTTOM)
    Quitter(root).pack(side=RIGHT)
    root.bind('<Return>', (lambda event, v=vars: fetch(v)))   
    root.mainloop()
