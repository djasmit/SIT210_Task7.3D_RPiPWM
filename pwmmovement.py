#libraries
import RPi.GPIO as GPIO
import time

#defines
GPIO.setmode(GPIO.BCM)
SENSOR_TRIGGER = 18 #PCM CLK
SENSOR_ECHO = 24 #GPIO24
PWM_PIN = 12 #PWM0
PWM_KH = 100 #LED_PIN khz
MIN_DIST = 0 #min distance for PWM (cm)
MAX_DIST = 10 #max distance for PWM (cm)

#GPIO and PWM initialization
GPIO.setup(SENSOR_TRIGGER, GPIO.OUT)
GPIO.setup(SENSOR_ECHO, GPIO.IN)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.output(PWM_PIN, GPIO.LOW)
PWM = GPIO.PWM(PWM_PIN, PWM_KH)
PWM.start(0)    

#calculate distance
def distance():
    GPIO.output(SENSOR_TRIGGER, True)
    
    time.sleep(0.00001)
    GPIO.output(SENSOR_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    #start reading
    while GPIO.input(SENSOR_ECHO) == 0:
        StartTime = time.time()
    
    #stop reading
    while GPIO.input(SENSOR_ECHO) == 1:
        StopTime = time.time()
    
    #time it took for signal to reach device
    TimeElapsed = StopTime - StartTime
    
    #distance = time / sonic speed
    distance = (TimeElapsed * 34300)/2
    print("Measured Distance = %.1f cm" % distance)
    
    return distance

#activates PWM based on received distance
def PWMSignal(distance, minDist, maxDist):
    #don't let distances be negative
    if (maxDist < 0.0 or minDist < 0.0):
        return False
    
    #make sure max distance is larger than min
    if (maxDist < minDist):
        temp = maxDist
        maxDist = minDist
        minDist = temp
        
    range = maxDist - minDist
    distPos = distance - minDist
    distPercent = (distPos/range) * 100.0
    closeness = 100.0 - distPercent
        
    #objects within 1 metre trigger the signal
    if (distPos <= maxDist):
        power = closeness
        
    #objects within 1cm activate full-power signal
    elif (distPos == minDist):
        power = 100.0
        
    #reading outside of range switches device off
    else:
        power = 0.0
    
    #set PWM output to power level
    PWM.ChangeDutyCycle(power)
    print("PWM power = %.1f" % power)

#turns off pins and cleans up GPIO
def shutdown():
    PWM.stop()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()    

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            PWMSignal(dist, MIN_DIST, MAX_DIST)
            
            time.sleep(1)
        #end while
    except KeyboardInterrupt:
        print("Measurement stopped by user")
        shutdown()
        