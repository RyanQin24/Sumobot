from flask import Flask
from flask import render_template
from playsound import playsound
from threading import Thread
import RPi.GPIO as GPIO
import time
from pygame import mixer


#starts flask
app= Flask(__name__)

#Pin assignment variables
GPIO.setmode(GPIO.BCM)
IntLeftLiSen = 23
IntRightLiSen = 24
IntStartBtn = 12
IntDistTrig = 19
IntDistEcho = 13
IntInterfereLi = 4
IntLeftServo = 14
IntRightServo = 15
IntLeftWheelsEnable = 27
IntRightWheelsEnable = 17
IntRightICIn1 = 22
IntRightICIn2 = 10
IntLeftICIn3 = 9
IntLeftICIn4 = 11

#GPIO setup
GPIO.setup(IntStartBtn, GPIO.IN)
GPIO.setup(IntDistTrig, GPIO.OUT)
GPIO.setup(IntDistEcho, GPIO.IN)
GPIO.setup(IntInterfereLi, GPIO.OUT)
GPIO.setup(IntLeftServo, GPIO.OUT)
GPIO.setup(IntRightServo, GPIO.OUT)
GPIO.setup(2, GPIO.OUT)
pwmLeftServo = GPIO.PWM(IntLeftServo,50)
pwmLeftServo.start(0)
pwmRightServo = GPIO.PWM(IntRightServo,50)
pwmRightServo.start(0)
GPIO.setup(IntLeftWheelsEnable, GPIO.OUT)
GPIO.setup(IntRightWheelsEnable, GPIO.OUT)
GPIO.setup(IntLeftICIn3, GPIO.OUT)
GPIO.setup(IntLeftICIn4, GPIO.OUT)
GPIO.setup(IntRightICIn1, GPIO.OUT)
GPIO.setup(IntRightICIn2, GPIO.OUT)
GPIO.output(IntLeftWheelsEnable, GPIO.HIGH)
GPIO.output(IntRightWheelsEnable, GPIO.HIGH)
GPIO.output(IntInterfereLi, GPIO.LOW)
GPIO.output(2, GPIO.HIGH)

#Physical variable constants
IntServoRetractAngle = 100
IntLeftServoExtendAngle = 0
IntRightServoExtendAngle = 8

def LeftServo(IntAngle):
        FltDuty = IntAngle / 18 + 3
        pwmLeftServo.ChangeDutyCycle(FltDuty)

def RightServo(IntAngle2):
        FltDuty2 = IntAngle2 /18 + 3
        pwmRightServo.ChangeDutyCycle(FltDuty2)

# Wheel drivetrain 4 wheen drive motor system output function
def drivetrainPower(IntLeftdir, IntRightdir, IntLeftPower, IntRightPower):
        if IntLeftPower == 0 and IntRightPower == 0:
                GPIO.output(IntRightICIn1, GPIO.LOW)
                GPIO.output(IntRightICIn2, GPIO.LOW)
                GPIO.output(IntLeftICIn3, GPIO.LOW)
                GPIO.output(IntLeftICIn4, GPIO.LOW)
              
        else:
                if IntLeftdir == 1:
                        GPIO.output(IntLeftICIn3, GPIO.HIGH)
                        GPIO.output(IntLeftICIn4, GPIO.LOW)
                elif IntLeftdir == -1:
                        GPIO.output(IntLeftICIn3, GPIO.LOW)
                        GPIO.output(IntLeftICIn4, GPIO.HIGH)

                if IntRightdir == 1:
                        GPIO.output(IntRightICIn1, GPIO.LOW)
                        GPIO.output(IntRightICIn2, GPIO.HIGH)
                elif IntRightdir == -1:
                        GPIO.output(IntRightICIn1, GPIO.HIGH)
                        GPIO.output(IntRightICIn2, GPIO.LOW)

drivetrainPower(0,0,0,0)

def light():
	bolState = GPIO.input(IntInterfereLi)
	if bolState:
		GPIO.output(IntInterfereLi, GPIO.LOW)
	else:
		GPIO.output(IntInterfereLi, GPIO.HIGH)

#pygame music player algorithm for music playback
mixer.init()

mixer.music.load('/home/pi/webpage/Power.wav')
mixer.music.set_volume(1.4)

def playy():
	if mixer.music.get_busy():
		mixer.music.stop()		
	else:
		mixer.music.play()
	

IntServoStart = 0
def Servomove():
	if GPIO.input(2):
		drivetrainPower(0,0,0,0)
		LeftServo(IntLeftServoExtendAngle)
		RightServo(IntRightServoExtendAngle)	
		time.sleep(1)
		pwmLeftServo.ChangeDutyCycle(0)
		pwmRightServo.ChangeDutyCycle(0)
		IntServoStart = 1
		GPIO.output(2, GPIO.LOW)
	else:
		LeftServo(IntServoRetractAngle)
		RightServo(IntServoRetractAngle)
		time.sleep(1)
		pwmLeftServo.ChangeDutyCycle(0)
		pwmRightServo.ChangeDutyCycle(0)
		GPIO.output(2, GPIO.HIGH)	

#defining flask functions 
@app.route('/')
def index():
	return render_template('web.html')

@app.route('/A')
def forward():
	drivetrainPower(1,1,100,100)
	return render_template('web.html') 

@app.route('/B')
def left():
	drivetrainPower(-1,1,100,100)
	return render_template('web.html')

@app.route('/C')
def reverse():
	drivetrainPower(-1,-1,100,100)
	return render_template('web.html')

@app.route('/D')
def right():
        drivetrainPower(1,-1,100,100)
        return render_template('web.html')


@app.route('/E')
def apache():
	drivetrainPower(0,0,0,0) 
	return render_template('index.html')

@app.route('/I')
def servo_exd():
	Servomove()
	return render_template('web.html')	
	
@app.route('/F')
def lights():
	light()
	return render_template('web.html')

@app.route('/G')
def music():
	playy()
	return render_template('web.html')	

@app.route('/H')
def stop():
	drivetrainPower(0,0,0,0)
	return render_template('web.html')

if __name__=="__main__":
	print("Start")
	app.run(debug=True, host='10.42.0.1')
