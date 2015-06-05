import time, datetime, serial, string, codecs, csv, threading, sys, colorama
from prettytable import PrettyTable

ch = [0]*15
m = [0]*15
b = [0]*15
outlist = [0]*15
n = 0
filedate = datetime.date.today()
probe = ["pH-RAS","pH-MAIN","pH-QUAR",u"\u00b0"+"C-RAS",u"\u00b0"+"C-MAIN",u"\u00b0"+"C-QUAR",
"O2 %-RAS","O2 %-MAIN","O2 %-QUAR","COND-RAS","COND-QUAR","pH-INC",u"\u00b0"+"C-INC","O2 %-INC",u"\u00b0"+"C-AMB"]

ser = serial.Serial('COM3',9600,timeout=.2)

colorama.init()
# put_cursor resets the command line output back to start to refresh the table of
# probe values
def put_cursor(x,y):
    print "\x1b[{};{}H".format(y+1,x+1)

# clear clears the output of the previous table before printing the current set of 
# probe values to a new table.    
def clear():
    print "\x1b[2J"

def writeV():
# n is the line number in the .csv document. It is incremented every data cycle.
  global n, filedate, dat, out
  n = n + 1 
  with open('Voltages\DirectVoltageReading'+str(filedate)+'.csv', 'a') as csvfile:
    # chvolwriter separates the string of voltages (dat) into 15 indexed positions,
    # prepends the date and time into index 0, and the line number into index 16. The
    # list is then appended to the most recent vlotage .csv file in the current 
    # directory, where the raw voltages are stored separately.
    chvolwriter = csv.writer(csvfile, delimiter=',', quotechar='|', lineterminator='\n')
    chvolwriter.writerow([str(datetime.datetime.now()) + "," + tdat + "," + str(n)])
    # call WriteP fuction directly after voltages are written.
    writeP()

def writeP():
  global n, filedate, dat, out
  with open('Calibrated Probes\DirectProbeReading'+str(filedate)+'.csv', 'a') as csvfile:
    # chwriter separates the string of calibrated probe readings (out) into 15 indexed
    # positions, prepends the date and time into index 0, and the line number into
    # index 16. The list is then appended to the most recent calibrated probe reading 
    # .csv file in the current directory to be accessed by the DirectProbeReading 
    # Mathematica GUI script.
    chcalwriter = csv.writer(csvfile, delimiter=',', quotechar='|', lineterminator='\n')
    chcalwriter.writerow([str(datetime.datetime.now()) + "," + out + "," + str(n)])
    # Sets the timing for WriteV and WriteP to restart ever 900s = 15min.
    threading.Timer(900,writeV).start()

  # dat is the data gathered over the USB. 15 channels of voltages comma separated 
  # in a single string.

# table prints an ASCII table whenever dat is received over serial. 
def table():  
  print ('\033[31m'+"       DO NOT CLOSE WINDOW!!!")
  print ('\033[0m'+"     "+str(datetime.datetime.now()))
  tab = PrettyTable(["Probe", "Voltage", "Cal. Value"])
  tab.align["Probe"] = "l"
  tab.align["Cal. Value"] = "l"
  tab.padding_width = 1
  # adds the name, voltages, and calibrated probe value  to tab in sequence.
  for i in range (0,15):
    tab.add_row([probe[i],ch[i],outlist[i]])
  # pt parses tab into a set of strings that can be edited.  
  pt = tab.get_string()
  # write each string with a newline.
  sys.stdout.write("\r" + pt)
  print "\n             MarTyr 171"
  
while True:  
  global dat
  dat = ser.readline()
  # When there is data over serial a .csv file is opened with the name scheme of
  # "MCUdat(today's date).csv" such that a new file is created every day.
  filedate = datetime.date.today()
  if dat:
    clear()
    put_cursor(0,0)
    # filedate sets a variable for today's date 
    filedate = datetime.date.today()
  
    # chlist splits the voltage string (dat) into a list of separate voltages.
    chlist = dat.split(",")
    # the for loop then converts the list into another list (ch) of floating
    # point integers to be calibrated.
    for i in range (0,15):
      ch[i] = float(chlist[i])
    
    # cal reads in the calibration values from "Probe Calibration Variables.txt"
    cal = open("Probe Calibration Variables.txt","r")
    # callist creates a nested list from the .txt file.
    callist = cal.readlines()
    
    # the for loop takes the index 0 values from callist, and converts them to a
    # list of floating point calibration slope values (m).
    for i in range (0,15):
      m[i] = float(callist[i].split("\t")[0])

    # the for loop takes the index 1 values from callist, and converts them to a
    # list of floating point calibration intercept values (b).
    for i in range (0,15):
      b[i] = float(callist[i].split("\t")[1])
  
    # the for loop creats a list (outlist) of floating point calibrated probe readings 
    # (m*ch +b) in the formof y = mx + b.
    for i in range (0,15):
      outlist[i] = round(m[i]*ch[i] + b[i],4)
  
    # outlist is converted to a string of comma separated variables (out) to be written
    # to a .csv file.
    global out
    out = str(outlist).strip("[]")
    # send all data to table
    table()
    # sets a second string set tdat that will not be parsed.
    tdat = dat
    # starts the writeV function at time ~ 0.
    if n == 0:
      writeV()