import socket, time

class Engine:

	_transaction_id = 0

	def _add_transaction_id(self, s):
		self._transaction_id += 1
		return str(s) + ' -i ' + str(self._transaction_id)

	def __init__(self):
		self.conn = None

	def start(self):
		HOST = 'localhost'
		PORT = 9000
		socket.setdefaulttimeout(5)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
			s.listen(5)
			self.conn, addr = s.accept()
		except socket.timeout:
			print "timeout..."
			s.close()
			return ["Timeout", "Connection closed."]
		response = self.receive()

		return [str(addr), response]


	def stop(self):
		if self.conn:
			self.conn.close()


	def send(self, user_command = ''):
		user_command = self._add_transaction_id(user_command)
		sent = self.conn.send(user_command + '\0')
		response = self.receive()

		return sent, response


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


	def run(self):
		return self.send('run')
