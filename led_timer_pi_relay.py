import datetime
import signal
import sys
import time

import RPi.GPIO
RPi.GPIO.setmode(RPi.GPIO.BOARD)
RPi.GPIO.setwarnings(False)



class PiRelay:
	def __init__(self, pin_number):
		self._pin_number = pin_number
		self._enabled = False

		RPi.GPIO.setup(self.pin_number, RPi.GPIO.OUT)
		self.off()


	@property
	def pin_number(self):
		return self._pin_number


	@property
	def enabled(self):
		return self._enabled


	def set_enabled(self, state):
		if state:
			self.on()
		
		else:
			self.off()


	def on(self):
		RPi.GPIO.output(self.pin_number, RPi.GPIO.HIGH)
		self._enabled = True


	def off(self):
		RPi.GPIO.output(self.pin_number, RPi.GPIO.LOW)
		self._enabled = False



class LED_Timer:
	# GPIO RELAY PIN NUMBERS
	RELAYS_GPIO_PINS = (31, 33, 35, 37)

	# RELAY CLASS INSTANCES
	RELAYS = [ PiRelay(x) for x in RELAYS_GPIO_PINS ]

	# Time of day to turn the LED relays on and off, tuple of the hour and minute of the time of day in military time.
	TIME_ON 	= datetime.time(16,0) # 4:00pm
	TIME_OFF 	= datetime.time(23,0) # 11:00pm

	CHECK_TIME_INTERVAL_SEC = 60


	@classmethod
	def reset_relays(cls):
		for relay in cls.RELAYS:
			relay.off()


	@staticmethod
	def is_time_between(begin_time, end_time, check_time = None):
		# https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da

		# If check time is not given, default to current UTC time
		#check_time = check_time or datetime.datetime.utcnow().time()
		check_time = check_time or datetime.datetime.now().time()

		if begin_time < end_time:
			return check_time >= begin_time and check_time <= end_time

		else: # crosses midnight
			return check_time >= begin_time or check_time <= end_time


	@classmethod
	def start_timer(cls, forced_state = None):
		#relays_to_use = cls.RELAYS
		relays_to_use = [cls.RELAYS[3]]

		while True:
			if forced_state is not None:
				relays_should_be_on = forced_state
				status = '{0}: Forced State Mode: {1}'.format(time.ctime(), forced_state)

			else:
				relays_should_be_on = cls.is_time_between(cls.TIME_ON, cls.TIME_OFF)
				status = '{0}: Schedule Mode: {1} - {2}'.format(time.ctime(), cls.TIME_ON, cls.TIME_OFF)

			print('====================LED TIMER PI RELAY====================')
			print(status)
			print('{0}: Relays should be on: {1}'.format(time.ctime(), relays_should_be_on))

			for relay in relays_to_use:
				if relay.enabled != relays_should_be_on:
					relay.set_enabled(relays_should_be_on)

				print('{0}: Relay PIN {1} is on: {2}'.format(time.ctime(),relay.pin_number,relay.enabled))
			
			time.sleep(cls.CHECK_TIME_INTERVAL_SEC)


	@classmethod
	def test_relays(cls):
		'''Test relay wiring by toggling on and off every second.'''
		while True:
			for relay in cls.RELAYS:
				relay.set_enabled(not(relay.enabled))
			
			time.sleep(1)



def interrupt_handler(_signum, _frame):
	# If we hit ctrl-c to break out of the code early, turn all the relays off.
	LED_Timer.reset_relays()
	exit(1)



if __name__ == '__main__':
	# Command Line Arguments
	arg1 = None
	if len(sys.argv) > 1:
		arg1 = sys.argv[1].lower()

	# Force the timer to be on or off regardless of schedule.
	forced_state = None
	if arg1 in [ 'true', 'on' ]:
		forced_state = True
	
	elif arg1 in [ 'false', 'off' ]:
		forced_state = False

	# Create a handler for an early out so via ctrl-c so the relays get turned off.
	signal.signal(signal.SIGINT, interrupt_handler)

	# Start Timer
	LED_Timer.start_timer(forced_state = forced_state)
	#LED_Timer.test_relays()
