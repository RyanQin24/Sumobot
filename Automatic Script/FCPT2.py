#Importing Libraries
import RPi.GPIO as GPIO
import time
import random

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

#Physical variable constants
IntLeftLightSenThreshold = 200
IntRightLightSenThreshold = 300
IntServoRetractAngle = 100
IntLeftServoExtendAngle = 0
IntRightServoExtendAngle = 8
IntLeftServoFlipAngle = 70
IntRightServoFlipAngle = 80
IntMinTurnTime = 1
IntMaxTurnTime = 3
IntMaxTurnSpeed = 50
IntDistThresh = 14
IntFlipTime = 3

#GPIO setup
GPIO.setup(IntStartBtn, GPIO.IN)
GPIO.setup(IntDistTrig, GPIO.OUT)
GPIO.setup(IntDistEcho, GPIO.IN)
GPIO.setup(IntInterfereLi, GPIO.OUT)
GPIO.setup(IntLeftServo, GPIO.OUT)
GPIO.setup(IntRightServo, GPIO.OUT)
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
pwmLeftWheels = GPIO.PWM(IntLeftWheelsEnable, 50)
pwmRightWheels = GPIO.PWM(IntRightWheelsEnable, 50)
pwmLeftWheels.start(0)
pwmRightWheels.start(0)

#sensor IO functions
def LeftLightSen():
	IntLeftcount = 0

	#Output on the pin for capacitor discharge

	GPIO.setup(IntLeftLiSen, GPIO.OUT)
	GPIO.output(IntLeftLiSen, GPIO.LOW)
	time.sleep(0.1)

      	#Change the pin back to input
	GPIO.setup(IntLeftLiSen, GPIO.IN)

        #Count up until pin is in high state
	while (GPIO.input(IntLeftLiSen) == GPIO.LOW):
		IntLeftcount += 1
		time.sleep(0.0001)
	return IntLeftcount

def RightLightSen():
	IntRcount = 0

        #Output on the pin for capacitor discharge

	GPIO.setup(IntRightLiSen, GPIO.OUT)
	GPIO.output(IntRightLiSen, GPIO.LOW)
	time.sleep(0.1)

        #Change the pin back to input
	GPIO.setup(IntRightLiSen, GPIO.IN)

        #Count up until the pin is in high state
	while (GPIO.input(IntRightLiSen) == GPIO.LOW):
		IntRcount += 1
		time.sleep(0.0001)
	return IntRcount

def DistSen():
	time.sleep(0.1)

	#sending 10 microsecond pulse to signal sensor to start measuring distance
	GPIO.output(IntDistTrig, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(IntDistTrig, GPIO.LOW)

	#finding the very latest time that sensor outputs 0v 
	while GPIO.input(IntDistEcho) == 0:
		FltStartTime = time.time()

        #finding time sensor outputs 5v
	while GPIO.input(IntDistEcho) == 1:
		FltEndTime = time.time()


        #calculating difference in time and then distance
	FltTimeDiff = FltEndTime - FltStartTime

	FltDistance = FltTimeDiff * 17150

	return FltDistance

#Motor Output Functions

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
		pwmLeftWheels.ChangeDutyCycle(100)
		pwmRightWheels.ChangeDutyCycle(100)
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
		elif IntLeftdir == -1:
			GPIO.output(IntRightICIn1, GPIO.HIGH)
			GPIO.output(IntRightICIn2, GPIO.LOW)

		pwmLeftWheels.ChangeDutyCycle(IntLeftPower)
		pwmRightWheels.ChangeDutyCycle(IntRightPower)

#Start of Prematch Initialization
while True:
	
	drivetrainPower(0,0,0,0)
	GPIO.output(IntInterfereLi, GPIO.LOW)
	LeftServo(IntServoRetractAngle)
	RightServo(IntServoRetractAngle)

	#button condition statement for starting match
	if GPIO.input(IntStartBtn) == GPIO.HIGH:
		GPIO.output(IntInterfereLi, GPIO.HIGH)
		time.sleep(5)
		#Match logic algorithms

		FltExtendTime = time.time()
		
		#loop
		while True:
			
			#Reading Light Sensor values
			IntLeftSenState = LeftLightSen()
			IntRightSenState = RightLightSen()
			
			#If else statements based on light sensor's value
			if IntLeftSenState <= IntLeftLightSenThreshold or IntRightSenState <= IntRightLightSenThreshold:

				#Backing up and turning if robot hits border. For added protection, flipper arms are retracted
				drivetrainPower(-1,-1,100,100)
				time.sleep(0.9)
				FltDlytime = random.uniform(IntMinTurnTime, IntMaxTurnTime)
				print(FltDlytime)
				LeftServo(IntLeftServoFlipAngle)
				RightServo(IntRightServoFlipAngle)

				# If, else if statements for deciding the direction to turn based of light sensor's value
				if IntLeftSenState <= IntLeftLightSenThreshold:
					drivetrainPower(1,-1,IntMaxTurnSpeed,IntMaxTurnSpeed)
				elif IntRightSenState <= IntRightLightSenThreshold:
					drivetrainPower(-1,1,IntMaxTurnSpeed,IntMaxTurnSpeed)
				time.sleep(FltDlytime)

				FltExtendTime = time.time()
			else:
				
				#Driving forward and operating lifter based off distance sensor if robot is not hitting border
				drivetrainPower(1,1,100,100)
				IntCurDist = DistSen()

				#if statements for operating the flipper based of the distance sensor
				if IntCurDist < IntDistThresh: 
					LeftServo(IntLeftServoFlipAngle)
					RightServo(IntRightServoFlipAngle)
					FltExtendTime = time.time()
				if time.time()-FltExtendTime >= IntFlipTime and IntCurDist > IntDistThresh:
					LeftServo(IntLeftServoExtendAngle)
					RightServo(IntRightServoExtendAngle) 

				
				                                                                                                                                                


