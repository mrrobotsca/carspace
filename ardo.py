import RPi.GPIO as GPIO
import time
import json
import datetime
GPIO.setwarnings(False)
from firebase import firebase
firebase = firebase.FirebaseApplication('https://hackaton-32051.firebaseio.com', None)
valeur = 1
tab = []

def ping():
	"""Get reading from HC-SR04"""
        global pastValue
	
	def liton(pin,tiim):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(tiim)
            print "LED ON\n"
        def litoff(pin,tiim):
            GPIO.output(pin,GPIO.LOW)
            time.sleep(tiim)
            print "LED OFF \n"
            
	GPIO.setmode(GPIO.BCM)
	 
	TRIG = 23 
	ECHO = 18
	 
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)
	GPIO.setup(22,GPIO.OUT)
	GPIO.setup(27,GPIO.OUT)
	 
	GPIO.output(TRIG, False)
	time.sleep(1)
	 
	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)
	 
	while GPIO.input(ECHO)==0:
	  pulse_start = time.time()
 
	while GPIO.input(ECHO)==1:
	  pulse_end = time.time()
	  
	 
	pulse_duration = pulse_end - pulse_start
	distance = pulse_duration * 17150
	
	distance = round(distance, 2)

	if distance<=6:
            GPIO.output(27,True)
            GPIO.output(22,False)
            valeur = 1
            print "Allo"
            ledoff()
        if distance>6 :
            GPIO.output(27,False)
            GPIO.output(22,True)
            valeur = 0
            print "A l'huile"
            ledon()
        tab.append(valeur)
	print "Distance:",distance,"cm", tab
	 
	GPIO.cleanup()

print "Reading Distance \n"

def ledoff():
    #result = firebase.get('/commerce', None)
    #print result
    global tab
    if len(tab) > 1:
        if tab[len(tab) - 1] != tab.pop(len(tab) - 2):
            data = {'time': time.time(), 
                    'etat': 0}
            result = firebase.post('/capteur/'+ '1', data)
            print('envoie1')
    
def ledon():
    #result = firebase.get('/commerce', None)
    #print result
    global tab
    if len(tab) > 1:
        if tab[len(tab) - 1] != tab.pop(len(tab) - 2):
            data = {'time': time.time(), 
                    'etat': 1}
            result = firebase.post('/capteur/'+ '1', data)
            print('envoie1')
while True:
	ping()