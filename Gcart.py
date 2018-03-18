#!/usr/bin/env python
from Tkinter import *
import ttk
from ttk import *
import sys
import Tkinter
from dronekit import connect, VehicleMode, LocationGlobal
import time
import threading
import gps
import socket
import math
import dronekit_sitl

from readPiksiSBP import PiksiSBP

#######MODIFY ACCORDINGLY######
telemetry_port = "/dev/ttyUSB0"
gps_port = "/dev/ttyUSB1"
###############################

sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

top_label_font_size = 10
label_font_size = 12

#Use this line for connecting with 3dr radio
v = connect(telemetry_port, baud=57600 , wait_ready=False)
#use this line for connecting to simulation
#v = connect(connection_string, wait_ready=False)
print "Connected to Tractor \nReady to Go!!!"

root = Tk()
root.title("GcartLayout")
root.attributes('-zoomed', True)

# Create the frames for layout
frameTuple=("terminal", "topInfo", "tracHealth", "buttons", "lowerInfo", 
    "speedSel")
for x in frameTuple:
    globals()[x] = ttk.Frame(root, relief="groove", padding="3")
    globals()[x].grid_propagate(False)
    globals()[x].grid(sticky=(N,E,S,W))
    
# Place the frames in root
terminal.grid(column=6, columnspan= 4, row=2, rowspan=4)
topInfo.grid(column=0, columnspan= 6, row=0)
tracHealth.grid(column=6, columnspan= 4, row=0, rowspan=2)
buttons.grid(column=0, columnspan= 6, row=1, rowspan=4)
lowerInfo.grid(column=0, columnspan= 6, row=5)
speedSel.grid(column=0, columnspan= 10, row=7)

# Configure relative size of frames by changing column weights of root
for x in range(10):
    root.columnconfigure(x, weight=10)
for x in (1,2,3,4,7):
    root.rowconfigure(x, weight=10)
root.rowconfigure(0, weight=5)
root.rowconfigure(5, weight=6)
#~ root.rowconfigure(6, weight=2)

###topInfoFrame###
def gps_callback(self, attr_name, value):
    if value.fix_type==3:
        gpsLabel.configure(foreground="green")
    else:
        gpsLabel.configure(foreground="red")
    gpsStatus.set("%dDGPS Sats: %d" %(value.fix_type, value.satellites_visible))
v.add_attribute_listener("gps_0", gps_callback)
    
gpsStatus = StringVar()
gpsLabel = ttk.Label(topInfo, textvariable=gpsStatus, anchor="center", 
    font=("",top_label_font_size,""))
gpsLabel.grid(column=0, row=0, sticky=(N,E,S,W))

@v.on_message("RADIO")
def listener(self, name, message):
    if message.rssi < message.noise+10 or message.remrssi < message.remnoise+10:
        radioLabel.configure(foreground="red")
    else:
        radioLabel.configure(foreground="black")
    radioStatus.set('Radio %u/%u %u/%u' % (message.rssi, message.noise, 
        message.remrssi, message.remnoise))

radioStatus = StringVar()
radioLabel = ttk.Label(topInfo, textvariable=radioStatus, anchor="center", 
    font=("",top_label_font_size,""))
radioLabel.grid(column=0, row=1, sticky=(N,E,S,W))

@v.on_message("NAV_CONTROLLER_OUTPUT")
def listener(self, name, message):
    wpDist.set("Distance to waypoint: %s(m)" %(message.wp_dist))
    wpDistNum.set(message.wp_dist)
    
wpDist = StringVar()
wpDistNum = StringVar()
wpDistLabel = ttk.Label(topInfo, textvariable=wpDist, anchor="center", 
    font=("",top_label_font_size,""))
wpDistLabel.grid(column=1, row=0, sticky=(N,E,S,W))

for x in range(4):
    topInfo.columnconfigure(x, weight=1)
for x in range(2):
    topInfo.rowconfigure(x, weight=1)
###End of topInfo Frame####

###tractorHealthFrame###
@v.on_message("TRACTOR_HEALTH")
def listener(self, name, message):
    #print 'Tractor Health %d %d %d %d %d' % (message.rpm_D4, message.rpm_D5, 
    #   message.coolan_temp_D1, message.oil_pres_D4, message.fuel_level_D2)
    rpm = (message.rpm_D4 + (256*message.rpm_D5))/8 ##rpm
    coolant_temp = message.coolan_temp_D1-40 ##celsius
    oil_pressure = message.oil_pres_D4*4/6.89476 ##psi
    fuel_level = message.fuel_level_D2*0.4 ## percent
    
    rpmText.set(str(rpm))
    coolantText.set(str(int(coolant_temp))+" C")
    oilText.set(str(int(oil_pressure))+" PSI")
    fuelPercent.set(int(fuel_level))

    if fuel_level<25:
        fuelLabel.configure(style="FuelR.Vertical.TProgressbar")
    else:
       fuelLabel.configure(style="FuelG.Vertical.TProgressbar")    
    
    if coolant_temp<=70:
        coolantLabel.configure(foreground="blue")
    elif coolant_temp>=95:
        coolantLabel.configure(foreground="red")
    elif 70<coolant_temp<95:
        coolantLabel.configure(foreground="green")
    else:
        coolantLabel.configure(foreground="black")

    if 25<oil_pressure<70:
        oilLabel.configure(foreground="green")
    else:
        oilLabel.configure(foreground="red")
        
rpmText = StringVar()
rpmLabel = ttk.Label(tracHealth, textvariable=rpmText, anchor="center", 
    font=("",label_font_size,""))
rpmLabel.grid(column=0, row=1, rowspan=3, sticky=(N,E,S,W))

coolantText = StringVar()
coolantLabel = ttk.Label(tracHealth, textvariable=coolantText, anchor="center", 
    font=("",label_font_size,""))
coolantLabel.grid(column=1, row=1, rowspan=3, sticky=(N,E,S,W))

oilText = StringVar()
oilLabel = ttk.Label(tracHealth, textvariable=oilText, anchor="center", 
    font=("",label_font_size,""))
oilLabel.grid(column=2, row=1, rowspan=3, sticky=(N,E,S,W))

fuelStyle = ttk.Style()
fuelStyle.configure("FuelG.Vertical.TProgressbar", 
    background="green")
fuelStyle.configure("FuelR.Vertical.TProgressbar", 
    background="red")

fuelPercent = IntVar()
fuelLabel = ttk.Progressbar(tracHealth, orient=VERTICAL, variable=fuelPercent)
fuelLabel.grid(column=3, row=1, rowspan=4, sticky=(N,E,S,W))

ttk.Label(tracHealth, text="Fuel", anchor="center", 
    font=("",label_font_size,"")).grid(column=3, row=0)

ttk.Label(tracHealth, text="Coolant\nCelsius", anchor="center", 
    justify="center", font=("",label_font_size,"")).grid(column=1, row=0)

ttk.Label(tracHealth, text="Engine\nRPM", anchor="center", justify="center",
    font=("",label_font_size,"")).grid(column=0, row=0)

ttk.Label(tracHealth, text="Oil PSI\nPressure", anchor="center", 
    justify="center", font=("",label_font_size,"")).grid(column=2, row=0)

for x in range(3):
    tracHealth.columnconfigure(x, weight=10)
tracHealth.columnconfigure(3, weight=1)
tracHealth.columnconfigure(4, weight=1)
for x in range(5):
    tracHealth.rowconfigure(x, weight=1)
###End of tracHealthFrame###


# ###Terminal Frame###    
# text = Tkinter.Text(terminal)
# text.grid(column=0, row=0, sticky=(N,E,S,W))
# terminal.columnconfigure(0, weight=1)
# terminal.rowconfigure(0, weight=1)

# class Std_redirector(object):
#     def __init__(self,widget):
#         self.widget = widget
        
#     def write(self,string):
#         self.widget.insert(Tkinter.END,string)
#         self.widget.see(Tkinter.END)
            
# sys.stdout = Std_redirector(text)
# ###End of Terminal Frame###

###SpeedSelFrame####
def setTargetSpeed(scaleVal):
    #Updates target speed as slider is moved
    targetSpeed.set((str(round(float(scaleVal), 1)), "KPH"))

def setSpeed(requestSpeed):
    #Function for changing speed. requestSpeed is a number (0-whatever
    #the top speed is set for) default is 8mph
    #speedDict is a dictionary that can be obtained by running CalibrateSpeed.py
    speedDict={0:1000, 1:1040, 2:1100, 3:1150, 4:1240, 5:1299, 6:1350, 7:1425, 
        8:1509, 9:1550, 10:1625 , 11:1700, 12:1850, 13:2000}
    speedScaleVal.set(requestSpeed)
    setTargetSpeed(requestSpeed)
    
    if requestSpeed in speedDict:
        rc8Val=speedDict[requestSpeed]
    elif requestSpeed < 0:
        rc8Val=speedDict[0]
    elif requestSpeed > 13:
        rc8Val=speedDict[13]
    else:
        #map rc8 value if request speed is between two whole numbers
        lowerVal= math.floor(requestSpeed)
        upperVal= math.ceil(requestSpeed)
        spread=speedDict[upperVal]-speedDict[lowerVal]
        rc8Val=int((requestSpeed-lowerVal)*spread+speedDict[lowerVal])
    
    v.channels.overrides["8"] = rc8Val

def setSpeedonRelease(instanceVar):
    setSpeed(speedScaleVal.get())
        
speedStyle = ttk.Style()
speedStyle.configure("Speed.Horizontal.TScale", 
    sliderthickness="90", 
    sliderlength=75, 
    background="orange")    
speedStyle.map("Speed.Horizontal.TScale",
    background=[("pressed", "orange"),
                ("active", "orange")])
                    
speedScaleVal = DoubleVar()
speedScale = ttk.Scale(speedSel, 
    orient=HORIZONTAL, 
    from_=0.0, 
    to=13.0, 
    variable= speedScaleVal, 
    style="Speed.Horizontal.TScale", 
    command=setTargetSpeed)
speedScale.bind("<ButtonRelease-1>", setSpeedonRelease)
speedScale.grid(column=0, row=0, sticky=(N,E,S,W))
speedSel.columnconfigure(0, weight=1)
speedSel.rowconfigure(0, weight=1)

ttk.Label(root, 
    text="Speed Control", 
    anchor="center",
    font=("",label_font_size,"")
    ).grid(column=0, 
        columnspan=10, 
        row=6, 
        sticky=(S,E,W))

ttk.Label(root, 
    text="Slow", 
    anchor="center",
    font=("",label_font_size,"")
    ).grid(column=0, 
        row=6, 
        sticky=(S,E,W))
        
ttk.Label(root, 
    text="Fast", 
    anchor="center",
    font=("",label_font_size,"")
    ).grid(column=9, 
        row=6, 
        sticky=(S,E,W))
###End of SpeedSelFrame####


###Start of lowerInfoFrame###
###In Gear watcher###
def mode_callback(self, attr_name, value):
    if str(value) == "VehicleMode:HOLD":
        inGearLabel.configure(background="green")
        inGearStatus.set("Tractor is Parked")
    else:
        inGearLabel.configure(background="red")
        inGearStatus.set("Tractor is in Gear")
            
v.add_attribute_listener("mode", mode_callback)

inGearStatus = StringVar()
inGearLabel = ttk.Label(lowerInfo, textvariable=inGearStatus, anchor="center",
    font=("",label_font_size,""))
inGearLabel.grid(column=0, row=0, sticky=(N,E,S,W))

mode_callback(v,"mode",v.mode)

for x in range(3):
    lowerInfo.columnconfigure(x, weight=1)
lowerInfo.rowconfigure(0, weight=1)
###End of in Gear watcher###

###Speed watcher###
def speed_callback(self, attr_name, value):
    speedStatus.set((round(value*2.23694*1.609, 1), 'KPH'))
            
v.add_attribute_listener("groundspeed", speed_callback)

speedStatus = StringVar()
speedLabel = ttk.Label(lowerInfo, textvariable=speedStatus, anchor="center",
    font=("",label_font_size,""))
ttk.Label(lowerInfo, text="GPS Speed", anchor="center",
    font=("",label_font_size,"")).grid(column=1, row=0, sticky=(N,E,W))
speedLabel.grid(column=1, row=0, sticky=(S,E,W))
###End of Speed watcher###

###Target Speed Display###
targetSpeed = StringVar()
targetSpeedLabel = ttk.Label(lowerInfo, 
    textvariable=targetSpeed, 
    anchor="center",
    font=("",label_font_size,""))
ttk.Label(lowerInfo, 
    text="Target Speed", 
    anchor="center",
    font=("",label_font_size,"")).grid(
    column=2, 
    row=0, 
    sticky=(N,E,W))
targetSpeedLabel.grid(column=2, row=0, sticky=(S,E,W))
###End of Target Speed Display###
###End of lowerInfoFrame####=


###Start of Buttons###
offsetAhead=18.0
offsetLeft=8.5
def distBwPoints(lat1,lon1,lat2,lon2):
    #returns distance in meters between two points of lat and lon
    #lat and lon need to be in decimal degrees
    #going to use a,b,c triangle c is hyponteus
    #theta is the distance in km of one degree of latitude
    theta=111111.0
    a=math.fabs(((lat1-lat2)*theta))
    #~ print "a=", a
    b=math.fabs((lon1-lon2))*math.cos(math.radians(math.fabs(lat1)))*theta
    #~ print "b=",b
    c=math.sqrt(a*a+b*b)
    #~ print "c=",c
    return c

def vectorDistance(A,B,Front):
    #A and B are lists of form [lat, lon, heading, speed]
    #if Front is true computes how far cart is ahead or behind combine
    #if Front is false copmutes how far left or right of combine heading cart is
    #returns vector distances between A and B ie how far in front of combine is cart?
    #or how far is it to the side
    lat = 0
    lon = 1
    heading = 2
    speed = 3
    #change a and b to radians
    for x in range(3):
        A[x]=math.radians(A[x])
        B[x]=math.radians(B[x])

    #Bearing from A to B = atan2(x,y)
    #x=cos(latB)sin(delta Lon) delta lon = lonB-LonA
    #y=cos(latA)Sin(latB)-sin(latA)cos(latB)cos(delta Lon)
    deltaLon = B[lon]-A[lon]
    x = math.cos(B[lat])*math.sin(deltaLon)
    y = (math.cos(A[lat])*math.sin(B[lat]))-(math.sin(A[lat])*math.cos(B[lat])*math.cos(deltaLon))
    bearing = math.atan2(x,y)
    # print math.degrees(bearing)
    if Front:
        perpDist = math.cos(A[heading]-bearing)*distBwPoints(math.degrees(A[lat]),math.degrees(A[lon]),math.degrees(B[lat]),math.degrees(B[lon]))
    else:
        perpDist = math.sin(A[heading]-bearing)*distBwPoints(math.degrees(A[lat]),math.degrees(A[lon]),math.degrees(B[lat]),math.degrees(B[lon]))
    # print "perp Distance = ", perpDist
    return perpDist

nextGpsLoc = []
def getGpsLoc():
    #returns list of lat,lon,track,speed
    # Use the python gps package to access the laptop GPS
    global nextGpsLoc
    try:
        piksi = PiksiSBP(gps_port)  #gps.gps(mode=gps.WATCH_ENABLE)
        gotgps=True
        while gotgps:
            piksi.next()
            if (piksi.latlon_valid & piksi.speed_valid) != 0:
                # print "got new gps position"
                nextGpsLoc = [piksi.latitude, piksi.longitude, piksi.track, piksi.speed]
                # return nextGpsLoc
    except socket.error:
        print "Error the GPS does not seem to be connected \n"

gpsThread = threading.Thread(target=getGpsLoc)
gpsThread.start()   

'''
#Original function.
def getGpsLoc():
    #returns list of lat,lon,track,speed
    # Use the python gps package to access the laptop GPS
    global nextGpsLoc
    try:
        gpsd = gps.gps(mode=gps.WATCH_ENABLE)
        gotgps=True
        while gotgps:
            gpsd.next()
            if (gpsd.valid & gps.LATLON_SET) != 0:
                # print "got new gps position"
                nextGpsLoc = [gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.track,gpsd.fix.speed]
                # return nextGpsLoc
    except socket.error:
        print "Error the GPS does not seem to be Connected \n"

gpsThread = threading.Thread(target=getGpsLoc)
gpsThread.start()   
'''

def cartUnldLoc(distLeft,distAhead,combineLoc):
    #returns lat lon that is dist left and dist ahead of combine location.
    #if dist left or dist ahead is negative the offset will be behind
    #combineLoc is list with 4 elements in the same form that getGpsLoc returns
    #angle between headingLeft and hyptoneus line formed by the triangle 
    #created with distLeft + distAhead
    theta=math.degrees(math.atan(float(distAhead)/float(distLeft)))
    #alpha is the angle between 0(north) and the hyptoneus line 
    #(if you drew a line between combineloc and projected point)
    alpha=-1
    if (combineLoc[2]-90+theta)<0:
        alpha=math.radians(combineLoc[2]+270+theta)
        #~ print "if statement"
    else:
        alpha=math.radians(combineLoc[2]-90+theta)
        #~ print "else statement"
    #delta lat and delta lon equals the sine and cosine of alpha multiplied 
    #by hypotenues length (h)
    h=math.sqrt(distLeft*distLeft+distAhead*distAhead)
    deltaLat=math.cos(alpha)*h
    deltaLon=math.sin(alpha)*h
    #convert delta lat and delta lon to decimal degrees add to combine
    #lat lon and return the result
    deltaLat=deltaLat/111111.0
    deltaLon=deltaLon/(math.cos(math.radians(combineLoc[0]))*111111.0)
    lat=combineLoc[0]+deltaLat
    lon=combineLoc[1]+deltaLon
    loc=[lat,lon]
    return loc

nudge=0.0
nudgeFront=0.0
def setPointForward():
    global nudgeFront
    nudgeFront=15.0
    print "Set point ahead ",nudgeFront,"(m) \n"

def setPointForwardZero():  
    global nudgeFront
    nudgeFront=0.0
    print "Set ahead distance back to normal ",nudgeFront,"(m) \n"

def turnAround():
    global nudge
    print "CART IS TURNING AROUND!"
    print "CART IS MOVING CLOSER! \n"
    setSpeed(4.5)
    nudge=0.0 #this should ensure cart always turns to the right
    setPointForward()

def moveLeft():
    global nudge
    nudge=nudge+0.5
    print "nudge = ",nudge, "\n"
def moveRight():
    global nudge
    nudge=nudge-.5
    print "nudge = ",nudge, "\n"
    
sendCartControl = threading.Event()
sendCartStatus = False
dWpControl = threading.Event()
unloadCycle = False
approach1Cycle = False
approach2Cycle = False
doGuideRight = False
autoSpeed = True

turnSet=False
forwardSet=False

def bringItClose():
    global nudge
    nudge=0.0
    setPointForwardZero()
    print "CART IS COMING CLOSE!"
    print "CART IS COMING CLOSE!"
    print "CART IS COMING CLOSE!"
    print "nudge = ",nudge, "\n"

def sendCart(sendCartControl):
    #~ print "sendCartThreadisStarted"
    global turnSet
    global forwardSet
    global sendCartStatus
    global nextGpsLoc
    global approach1Cycle
    global approach2Cycle
    global nudge
    global nudgeFront
    combineLoc=[]
    speedChange = True
    global autoSpeed
    while True:
        #~ print "sendCartThread is Running"
        sendCartControl.wait()
        #~ print "Started sending tractor process"
        while v.mode.name!="GUIDED":
            v.mode = VehicleMode("GUIDED")
            time.sleep(1)
            print v.mode.name
        #~ print "Tractor is in Gear \nStarting to get gps location of combine"
        while unloadCycle:
            if combineLoc!=nextGpsLoc:
                combineLoc=nextGpsLoc
                # print combineLoc
                # print "Got Gps Location"
                if doGuideRight:
                    combineLoc[2]=combineLoc[2]+180.0
                    loc=cartUnldLoc(offsetLeft+nudge,offsetAhead-40,combineLoc)
                else:
                    # if combineLoc[3]<0.4: #watch if combine stops set tractor to slow
                    #     setSpeed(0)
                    loc=cartUnldLoc(offsetLeft+nudge,offsetAhead+nudgeFront,combineLoc)
                    cartLoc=v.location.global_frame
                    distance=distBwPoints(loc[0],loc[1],cartLoc.lat,cartLoc.lon)
                    frontDist = vectorDistance(list(combineLoc),[cartLoc.lat,cartLoc.lon, 50],True)
                    perpDist = vectorDistance(list(combineLoc),[cartLoc.lat,cartLoc.lon, 50],False)

                    #check distance b/w cart and combine if distance is below some 
                    #threshold execute turn cart around only do this once
                    if turnSet and forwardSet and autoSpeed:
                        if frontDist < 7.0:
                            if speedScaleVal.get() < 13: 
                                setSpeed(speedScaleVal.get()+0.05)
                                speedChange = True
                                # print "speed up" 
                        elif frontDist > 8.75:
                            if speedScaleVal.get() > 0:
                                setSpeed(speedScaleVal.get()-0.2)
                                speedChange = True
                                # print "slow down"
                        else:
                            # print "matchSpeed"
                            if speedChange:
                                setSpeed((combineLoc[3]*2.23694*1.609)+0.1)
                                speedChange = False
                    if turnSet==False:
                        if perpDist < 30 and frontDist < 100:
                            #send the cart outside the line
                            loc=cartUnldLoc(200,offsetAhead+nudgeFront,combineLoc)
                        else:
                            loc=cartUnldLoc(offsetLeft+nudge,offsetAhead+nudgeFront,combineLoc)
                        if 28.0>distance or frontDist < 0:
                            print "Turning Cart Around \n"
                            turnAround()
                            turnSet=True
                            loc=cartUnldLoc(offsetLeft+nudge,offsetAhead+nudgeFront,combineLoc)
                    if turnSet==True and forwardSet==False:
                        distance=distBwPoints(combineLoc[0],combineLoc[1],
                            cartLoc.lat,cartLoc.lon)
                        if 14.0>frontDist:
                            bringItClose()
                            forwardSet=True
                            emptyButton.grid()
                        loc=cartUnldLoc(offsetLeft+nudge,offsetAhead+nudgeFront,combineLoc)
                cartGoalLoc=LocationGlobal(loc[0],loc[1],0)
                v.simple_goto(cartGoalLoc)
                # print "Sending Cart to ", cartLoc
            if sendCartStatus==False:
                while v.mode.name!="HOLD":
                    v.mode = VehicleMode("HOLD")
                    time.sleep(1)
        while approach1Cycle:
            cartGoalLoc=LocationGlobal(approach[0],approach[1],0)
            v.simple_goto(cartGoalLoc)
            sendCartControl.clear()
            approach1Cycle = False
            dWpControl.set()
            if sendCartStatus==False:
                while v.mode.name!="HOLD":
                    v.mode = VehicleMode("HOLD")
                    time.sleep(1)
        while approach2Cycle:
            cartGoalLoc=LocationGlobal(approach2[0],approach2[1],0)
            v.simple_goto(cartGoalLoc)
            sendCartControl.clear()
            approach2Cycle = False
            dWpControl.set()
            if sendCartStatus==False:
                while v.mode.name!="HOLD":
                    v.mode = VehicleMode("HOLD")
                    time.sleep(1)
                                        
sendCartThread = threading.Thread(target=sendCart, 
    args=(sendCartControl,))
sendCartThread.start()

def stop():
    setSpeed(0)
    global sendCartControl
    global sendCartStatus
    global dWpControl
    global unloadCycle
    global approach1Cycle
    global doGuideRight
    sendCartControl.clear()
    dWpControl.clear()
    sendCartStatus=False
    unloadCycle=False
    approach1Cycle=False
    doGuideRight = False
    setButtons()
    v.mode = VehicleMode("HOLD")

def empty():
    global dWpControl
    global sendCartControl
    global unloadCycle
    sendCartControl.clear()
    unloadCycle = False
    #this is based off combine position so you push empty button when done
    #unloading and the cart turns around.
    combineLoc=nextGpsLoc
    loc=cartUnldLoc(20,-25,combineLoc)
    cartGoalLoc=LocationGlobal(loc[0],loc[1],0)
    v.simple_goto(cartGoalLoc)
    dWpControl.set()

def autoSpeed():
    global autoSpeed
    if autoSpeed:
        autoSpeed = False
        autoSpeedButton.configure(style="Arm.Default.TButton")
    else:
        autoSpeed = True
        autoSpeedButton.configure(style="Disarm.Default.TButton")

def distToWP(dWpControl):
    global sendCartStatus
    global nextGpsLoc
    controlVar = True
    while True:
        dWpControl.wait()
        time.sleep(1)
        if sendCartStatus==False:
            while v.mode.name!="HOLD":
                v.mode = VehicleMode("HOLD")
                time.sleep(1)
                dWpControl.clear()
        
        elif int(wpDistNum.get())<30 and controlVar:
            setSpeed(4)
            controlVar=False
        elif int(wpDistNum.get())<10:
            print "Ready location is being reached, stopping now! \n"
            while v.mode.name!="HOLD":
                v.mode = VehicleMode("HOLD")
                time.sleep(1)
            stop()
            controlVar = True
            dWpControl.clear() 


distWpThread = threading.Thread(target=distToWP, 
    args=(dWpControl,))
distWpThread.start()
    
def guideRight():
    global nudge
    nudge = 39
    global doGuideRight
    doGuideRight = True
    global unloadCycle
    unloadCycle = True
    global sendCartControl
    global sendCartStatus
    sendCartStatus=True
    sendCartControl.set()
    setButtons(start=False, gRight=False, LRNudge=True)
    
approach=[0,0,0,0]
approach2=[0,0,0,0]

def setApproach():
    global approach
    global nextGpsLoc
    if nextGpsLoc!=[]:
        approach[0]=nextGpsLoc[0]
        approach[1]=nextGpsLoc[1]
        print "Approach set to here"
        print "GPS coordinates are ", approach[0], " ", approach[1]
        print "ARE YOU SURE THIS IS A SAFE SPOT?????!!!!! \n"
        goToApproachButton.grid_remove()
        if approach[0] != 0:
            goToApproachButton.grid()
            approachHereButton.grid_remove()
            unlockApproach1.grid()
    else:
        print "GPS is not Working"

def doUnlockApproach1():
    unlockApproach1.grid_remove()
    approachHereButton.grid()

def doUnlockApproach2():
    unlockApproach2.grid_remove()
    approachHereButton2.grid()

def goToApproach():
    global sendCartStatus
    global sendCartControl
    global unloadCycle
    global doGuideRight
    unloadCycle = False
    sendCartStatus = True
    sendCartControl.set()
    global approach1Cycle
    approach1Cycle = True
    doGuideRight = False
    global approach2Cycle
    approach2Cycle = False

def setApproach2():
    global approach2
    global nextGpsLoc
    if nextGpsLoc!=[]:
        approach2[0]=nextGpsLoc[0]
        approach2[1]=nextGpsLoc[1]
        print "Approach set to here"
        print "GPS coordinates are ", approach2[0], " ", approach2[1]
        print "ARE YOU SURE THIS IS A SAFE SPOT?????!!!!! \n"
        goToApproachButton2.grid_remove()
        if approach2[0] != 0:
            goToApproachButton2.grid()
            approachHereButton2.grid_remove()
            unlockApproach2.grid()
    else:
        print "GPS is not Working"

def goToApproach2():
    global sendCartStatus
    global sendCartControl
    global unloadCycle
    global doGuideRight
    unloadCycle = False
    sendCartStatus = True
    sendCartControl.set()
    global approach2Cycle
    approach2Cycle = True
    doGuideRight = False
    global approach1Cycle
    approach1Cycle = False
  
def arm():
    v.channels.overrides["5"] = 2000
    armButton.grid_remove()
    disarmButton.grid()
    
def disarm():
    v.channels.overrides["5"] = 1000
    disarmButton.grid_remove()
    armButton.grid()    
        
def startUnloading():
    global nudge
    nudge=20.0 #distance away from combine cart initially starts
    global nudgeFront
    nudgeFront=0.0
    global turnSet
    global forwardSet
    global sendCartControl
    global sendCartStatus
    global unloadCycle
    unloadCycle = True
    sendCartStatus=True
    turnSet=False
    forwardSet=False
    print v.mode.name
    sendCartControl.set()
    setButtons(start=False, gRight=False, LRNudge=True)
    print "got there"

def setButtons(start=True, gRight=True, here=True, LRNudge=False, empty=False):
    #grids the default buttons
    global approach
    for widgets in buttons.children.values():
        widgets.grid_remove()
    for widgets in terminal.children.values():
        widgets.grid_remove()

    stopButton.grid()
    autoSpeedButton.grid()
    if v.channels.overrides["5"]==1000:
        armButton.grid()
    elif v.channels.overrides["5"]==2000:
        disarmButton.grid()
    else:
        disarmButton.grid()
    if start:
        startUnloadingButton.grid()
    if gRight:
        guideRightButton.grid()
    if here:
        unlockApproach1.grid()
        unlockApproach2.grid()
    if approach[0] != 0:
        goToApproachButton.grid()
    if approach2[0] != 0:
        goToApproachButton2.grid()
    if LRNudge:
        RNudgeButton.grid()
        LNudgeButton.grid()
    if empty:
        emptyButton.grid()
 
for x in range(3):
    buttons.columnconfigure(x, weight=1)
for x in range(2):
    buttons.rowconfigure(x, weight=1)

for x in range(2):
    terminal.columnconfigure(x, weight=1)
for x in range(2):
    terminal.rowconfigure(x, weight=1)
    
buttonStyle = ttk.Style()
buttonStyle.configure("Default.TButton",
    font=("",label_font_size,""),
    anchor="center",
    justify="center")
buttonStyle.map("Stop.Default.TButton",
    background=[("active", "orange")])
buttonStyle.configure("Stop.Default.TButton",
    background="orange")
buttonStyle.map("StartUnloading.Default.TButton",
    background=[("active", "green")])
buttonStyle.configure("StartUnloading.Default.TButton",
    background="green") 
buttonStyle.map("Arm.Default.TButton",
    background=[("active", "green")])
buttonStyle.configure("Arm.Default.TButton",
    background="green")
buttonStyle.map("Disarm.Default.TButton",
    background=[("active", "red")])
buttonStyle.configure("Disarm.Default.TButton",
    background="red")
buttonStyle.map("Approach.Default.TButton",
    background=[("active", "magenta")])
buttonStyle.configure("Approach.Default.TButton",
    background="magenta")
buttonStyle.map("Nudge.Default.TButton",
    background=[("active", "lightBlue")])
buttonStyle.configure("Nudge.Default.TButton",
    background="lightblue")
buttonStyle.map("GoTo.Default.TButton",
    background=[("active", "yellow")])
buttonStyle.configure("GoTo.Default.TButton",
    background="yellow")
buttonStyle.map("Unlock.Default.TButton",
    background=[("active", "pink")])
buttonStyle.configure("Unlock.Default.TButton",
    background="pink")

RNudgeButton=ttk.Button(buttons, 
    text="Nudge\nRight", 
    command= moveRight,
    style="Nudge.Default.TButton")
RNudgeButton.grid(column=2, row=1, sticky=(N,E,S,W))

LNudgeButton=ttk.Button(buttons, 
    text="Nudge\nLeft", 
    command= moveLeft,
    style="Nudge.Default.TButton")
LNudgeButton.grid(column=0, row=1, sticky=(N,E,S,W))
    
armButton=ttk.Button(buttons, 
    text="Arm\nTractor", 
    command= arm,
    style="Arm.Default.TButton")
armButton.grid(column=1, row=0, sticky=(N,E,S,W))

disarmButton=ttk.Button(buttons, 
    text="Disarm\nTractor", 
    command= disarm,
    style="Disarm.Default.TButton")
disarmButton.grid(column=1, row=0, sticky=(N,E,S,W))

stopButton=ttk.Button(buttons, 
    text="Stop", 
    command= stop,
    style="Stop.Default.TButton")
stopButton.grid(column=1, row=1, sticky=(N,E,S,W))

startUnloadingButton=ttk.Button(buttons, 
    text="Start\nUnloading", 
    command= startUnloading,
    style="StartUnloading.Default.TButton")
startUnloadingButton.grid(column=0, row=1, sticky=(N,E,S,W))

guideRightButton=ttk.Button(buttons, 
    text="Guide Right", 
    command= guideRight,
    style="Default.TButton")
guideRightButton.grid(column=2, row=1, sticky=(N,E,S,W))
    
approachHereButton=ttk.Button(buttons, 
    text="Approach\nIs Here", 
    command= setApproach,
    style="Approach.Default.TButton")
approachHereButton.grid(column=0, row=0, sticky=(N,E,S,W))

unlockApproach1=ttk.Button(buttons, 
    text="Unlock\nApproach 1", 
    command= doUnlockApproach1,
    style="Unlock.Default.TButton")
unlockApproach1.grid(column=0, row=0, sticky=(N,E,S,W))

goToApproachButton=ttk.Button(buttons, 
    text="Go To\nApproach", 
    command= goToApproach,
    style="GoTo.Default.TButton")
goToApproachButton.grid(column=2, row=0, sticky=(N,E,S,W))

emptyButton=ttk.Button(terminal,
    text="Empty", 
    command= empty,
    style="Nudge.Default.TButton")
emptyButton.grid(column=0, row=1, sticky=(N,E,S,W))

approachHereButton2=ttk.Button(terminal, 
    text="Approach 2\nIs Here", 
    command= setApproach2,
    style="Approach.Default.TButton")
approachHereButton2.grid(column=0, row=0, sticky=(N,E,S,W))

unlockApproach2=ttk.Button(terminal, 
    text="Unlock\nApproach 2", 
    command= doUnlockApproach2,
    style="Unlock.Default.TButton")
unlockApproach2.grid(column=0, row=0, sticky=(N,E,S,W))

goToApproachButton2=ttk.Button(terminal, 
    text="Go To\nApproach 2", 
    command= goToApproach2,
    style="GoTo.Default.TButton")
goToApproachButton2.grid(column=1, row=0, sticky=(N,E,S,W))

autoSpeedButton=ttk.Button(terminal, 
    text="Auto Speed", 
    command= autoSpeed,
    style="Disarm.Default.TButton")
autoSpeedButton.grid(column=1, row=1, sticky=(N,E,S,W))

v.channels.overrides["5"]=1000
setButtons()

###End of Buttons
root.mainloop()
