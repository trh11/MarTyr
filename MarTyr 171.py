import time, datetime, serial, string, codecs, csv, threading, sys, colorama
from prettytable import PrettyTable

ch = [0]*15
m = [0]*15
b = [0]*15
outlist = [0]*15
n = 0
filedate = datetime.date.today()
probe = ["pH-RAS","pH-MAIN","pH-QUAR",u"\u00b0"+"C-RAS",u"\u00b0"+"C-MAIN",u"\u00b0"+"C-QUAR",
"O2 %-RAS","O2 %-MAIN","O2 %-QUAR","COND-RAS","COND-QUAR","pH-INC",u"\u00b0"+"C-INC","O2 %-INC",u"\u00b0"+"C-AMB",
"SAL-RAS","SAL-QUAR"]

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
  global ch, outlist
  # the salinity readings are calculated and so correspond to no voltages which is
  # represented as "Not Applicable" on the realtime chart.
  ch.extend(['NA','NA'])
  print ('\033[91m'+"       DO NOT CLOSE WINDOW!!!")
  print ('\033[0m'+"     "+str(datetime.datetime.now()))
  tab = PrettyTable(["Probe", "Voltage", "Cal. Value"])
  tab.align["Probe"] = "l"
  tab.align["Cal. Value"] = "l"
  tab.padding_width = 1
  # adds the name, voltages, and calibrated probe value  to tab in sequence.
  for i in range (0,17):
    tab.add_row([probe[i],ch[i],outlist[i]])
  # pt parses tab into a set of strings that can be edited.  
  pt = tab.get_string()
  # write each string with a newline.
  sys.stdout.write("\r" + pt)
  print "\n             MarTyr 171"
  # clears outlist and ch so that readings are the correct dimensions.
  outlist = [0]*15
  ch = [0]*15

# sal gives the salinity (unitless) of water based on the conductivity and
# temperature. Negative conductivites are incongruent with the model, so
# Csamp values are constrained to positive numbers, as are salinity values
# in the output. Uses the model from: 
# http://www.chemiasoft.com/chemd/salinity_calculator and should be checked
# against that salinity calculater if in doubt.
def sal(Csamp, T):
  global S
  if Csamp <= 0:
    S = 0
  else:
    a = [.008, -.1692, 25.3851, 14.0941, -7.0261, 2.7081]
    b = [.0005, -.0056, -.0066, -.0375, .0636, -.0144]
    c = [-.0267243, 4.6636947, 861.3027640, 29035.1640851]
    Csol = c[0]*T**3 + c[1]*T**2 + c[2]*T + c[3]
    Rt = (1000*Csamp)/Csol
    S = (
    a[0] 
    + a[1]*Rt**(.5)
    + a[2]*Rt
    + a[3]*Rt**(1.5)
    + a[4]*Rt**2
    + a[5]*Rt**(2.5)
    + ((T-15)/(1+.0162*(T-15)))
      *(
      b[0] 
      + b[1]*Rt**(.5) 
      + b[2]*Rt 
      + b[3]*Rt**(1.5) 
      + b[4]*Rt**2 
      + b[5]*Rt**(2.5)
      )
    )
    if S <= 0:
      S = 0
  
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

    
    sal(outlist[9],outlist[3])
    outlist.append(round(S, 4))
    S = 0

    sal(outlist[10],outlist[5])
    outlist.append(round(S, 4))
  
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
