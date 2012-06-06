import socket, time

class Engine:

	def start(self):
		HOST = 'localhost'
		PORT = 9000
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		print 'Listening...'
		s.listen(5)

		self.conn, addr = s.accept()
		print 'Established: ' + str(addr)
		response = self.receive()

		return response


	def send(self, user_command = ''):
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

	def stop(self):
		self.conn.close()
