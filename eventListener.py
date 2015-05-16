from ctypes import c_int, c_ubyte, c_void_p, POINTER, string_at #imports allowing the use of our library
from threading import Timer
import time
import platform
#import urllib2
import os
#import MySQLdb

#import pushover notifications stuffs
import httplib, urllib
pushover_user_key = #userkey goes here
pushover_app_token = #app token goes here
lastMethod = None

def sendPushover(title, msg):
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": pushover_app_token,
        "user": pushover_user_key,
        "title": title,
        "priority": "-2",
        "message": msg,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

#platform specific imports:
if (platform.system() == 'Windows'):
   #Windows
   from ctypes import windll, WINFUNCTYPE
   lib = windll.LoadLibrary('TelldusCore.dll') #import our library
else:
   #Linux
   from ctypes import cdll, CFUNCTYPE
   lib = cdll.LoadLibrary('libtelldus-core.so.2') #import our library


#device id to check for
doorId = 5;

#function to be called when a device event occurs      
def callbackfunction(deviceId, method, value, callbackId, context):
   print "device callback"
   #This var keeps track of last changed value of door, thereby avoiding duplicate pushover calls
   #Method refers to 1=open 2=closed 
   global lastMethod
   if (deviceId == doorId): 
     if(lastMethod != method):
        print "door sensor"
        print method
        if (method == 1):
          sendPushover("Door", "opened")
        else:
          sendPushover("Door", "closed")
        lastMethod = method

#function to be called when device event occurs, even for unregistered devices
def rawcallbackfunction(data, controllerId, callbackId, context):
   #Print the raw information
   raw1 = string_at(data)
   #print "RawData collected:" + raw1

if (platform.system() == 'Windows'):
   CMPFUNC = WINFUNCTYPE(c_void_p, c_int, c_int, POINTER(c_ubyte), c_int, c_void_p) #first is return type
   CMPFUNCRAW = WINFUNCTYPE(c_void_p, POINTER(c_ubyte), c_int, c_int, c_void_p)
else:
   CMPFUNC = CFUNCTYPE(c_void_p, c_int, c_int, POINTER(c_ubyte), c_int, c_void_p)
   CMPFUNCRAW = CFUNCTYPE(c_void_p, POINTER(c_ubyte), c_int, c_int, c_void_p)

cmp_func = CMPFUNC(callbackfunction)
cmp_funcraw = CMPFUNCRAW(rawcallbackfunction)

lib.tdInit()
lib.tdRegisterDeviceEvent(cmp_func, 0)
lib.tdRegisterRawDeviceEvent(cmp_funcraw, 0) #uncomment this, and comment out tdRegisterDeviceEvent, to see data for not registered devices

print "Waiting for events..."
while(1):
   time.sleep(0.5) #don't exit
