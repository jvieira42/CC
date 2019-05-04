import time

class Timer:
	TIMER_STOP = -1

	def __init__(self,duration):
		self.start_time = self.TIMER_STOP
		self.duration = duration

	def start(self): 
		if self.start_time == self.TIMER_STOP:
			self.start_time = time.time()

	def stop(self):
		if self.start_time != self.TIMER_STOP:
			self.start_time = time.time()

	def running(self):
		return self.start_time != self.TIMER_STOP

	def timeout(self):
		if not self.running():
			return False
		else:
			return time.time() - self.start_time >= self.duration