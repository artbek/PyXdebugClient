import socket, time, threading

class Engine(threading.Thread):

	_transaction_id = 0
	status = 'idle'

	def _add_transaction_id(self, s):
		self._transaction_id += 1
		return str(s) + ' -i ' + str(self._transaction_id)

	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.conn = None


	def run(self):
		HOST = ''
		PORT = 9000
		socket.setdefaulttimeout(5)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
			s.listen(5)
			self.queue.put("listening...")
			self.conn, addr = s.accept()
			self.status = 'running'
			response = self.receive()
			output = {
				'addr': str(addr), 
				'console': response
			}
		except socket.timeout:
			s.close()
			output = {'response': 'Timeout. Connection closed.'}

		self.queue.put(output)
		print output


	def stop(self):
		if self.conn:
			self.conn.close()
			self.status = 'idle'


	def send(self, user_command = ''):
		user_command = self._add_transaction_id(user_command)
		sent = self.conn.send(user_command + '\0')
		response = self.receive()

		output = {
			'sent': sent, 
			'code': response
		}
		self.queue.put(output)
		print output


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
		return self.send('step_over')


	def step_into(self):
		return self.send('step_into')


	def xrun(self):
		return self.send('run')
