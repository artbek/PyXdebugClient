import socket, time, threading, Queue

class Engine(threading.Thread):

	_transaction_id = 0
	status = 'idle'
	watches = []
	signal = ''

	def _add_transaction_id(self, s):
		self._transaction_id += 1
		return str(s) + ' -i ' + str(self._transaction_id)

	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.conn = None
		self.s = None

	def connect(self):
		HOST = ''
		PORT = 9000
		socket.setdefaulttimeout(3)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.s.bind((HOST, PORT))
			self.s.listen(5)
			self.queue.put("listening...")
			self.status = 'listening'
			self.conn, addr = self.s.accept()
			self.status = 'running'
			response = self.receive()
			output = {
				'addr': str(addr),
				'console': response
			}
		except socket.timeout:
			self.s.shutdown(socket.SHUT_RDWR);
			self.s.close()
			self.s = None
			output = {'response': 'Timeout. Connection closed.'}
			self.status = 'idle'

		self.queue.put(output)
		print output


	def run(self):
		print "Start thread " + str(self.name)
		while True:
			if (self.signal == 'listen'):
				self.signal = ''
				self.connect()
			elif (self.signal == 'stop'):
				self.signal = ''
				self.disconnect()
			elif (self.signal == 'kill'):
				break

			time.sleep(0.1)


	def disconnect(self):
		if (self.s):
			self.s.shutdown(socket.SHUT_RDWR);
			self.s.close();
		if (self.conn):
			self.conn.close()
		self.status = 'idle'


	def send(self, user_command = ''):
		user_command = self._add_transaction_id(user_command)
		sent = self.conn.send(user_command + '\0')
		response = self.receive()

		return response


	def receive(self):
		counter = 0
		datas = ''
		while 1:
			data = self.conn.recv(1)
			if not data:
				datas = 'Debugging session finished.'
				break
			datas += data
			if (ord(data) == 0):
				counter += 1
				if (counter == 1):
					#print 'Incoming length: ' + str(datas)
					datas = ''
				if (counter == 2):
					#print datas
					break
		return datas


	def step_over(self):
		output = {
			'code': self.send('step_over'),
			'stack': self.send('stack_get'),
			'watchview': self.get_watches(),
		}
		self.queue.put(output)


	def step_into(self):
		output = {
			'code': self.send('step_into'),
			'stack': self.send('stack_get'),
			'watchview': self.get_watches(),
		}
		self.queue.put(output)


	def xrun(self):
		self.send('run')


	def get_watches(self):
		output = []
		for w in self.watches:
			r = self.send('property_get -n' + str(w))
			output.append(r)

		print output
		return output



