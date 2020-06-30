#!/usr/bin/env python3

import time
import paho.mqtt.client as mqtt
from datetime import datetime

timeSensor1 = datetime.now()
dataSensor1 = 200.00
timeSensor2 = datetime.now()
dataSensor2 = 200.00

from firebase import firebase
firebase = firebase.FirebaseApplication('https://hackaton-32051.firebaseio.com', None)
valeur = 1
tab = []

def ledoff():
    #result = firebase.get('/commerce', None)
    #print result
    global tab
    data = {'time': time.time(), 'etat': 0}
    result = firebase.post('/capteur/'+ '1', data)
    print('envoie1')
    
def ledon():
    #result = firebase.get('/commerce', None)
    #print result
    global tab
    data = {'time': time.time(),'etat': 1}
    result = firebase.post('/capteur/'+ '1', data)
    print('envoie1')

# This is the Subscriber

def compareMeasurements(newData,newTime,oldData,oldTime):
  if newData < 20.00:
    if oldData >=20.00:
      return newData,newTime
    elif -5.0 <= (newData-oldData) <= 5.0:
      return oldData,oldTime
    else:
      return newData,newTime
  else:
    if oldData < 20.00:
      return newData,newTime
    elif -5.0 <= (newData-oldData) <= 5.0:
      return oldData,oldTime
    else:
      return newData,newTime

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("Measurement")

def on_message(client, userdata, msg):
  global dataSensor1,timeSensor1, dataSensor2,timeSensor2,tab
  mes = msg.payload.decode().split(":")
  if mes[0] == "Sensor011":
    dataSensor1,timeSensor1=compareMeasurements(float(mes[1]),datetime.now(),dataSensor1,timeSensor1)
    print((datetime.now()-timeSensor1).total_seconds())
    if ((datetime.now()-timeSensor1).total_seconds() > 2.00):
      if(dataSensor1 < 150):
        print("parkingspot taken")
        tab.append(1)
        ledon()
      else:
	print("parkingspot free")
        ledoff()
    print("First Sensor " + mes[1])
 # if mes[0] == "Sensor012":
    #print("Second Sensor " + mes[1])
client = mqtt.Client()
client.connect("localhost")

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
