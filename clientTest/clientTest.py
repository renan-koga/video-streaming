import socket
import socketserver
import threading
import vlc
import glob
import os
import sys
import time
from threading import Lock
from canalTeste import *

# lock = Lock()

class Client:
	def __init__(self, max_connections):
		# self.serverReceiver = None
		# self.clientReceiver = None
		# self.clientServer = None
		self.sender_ip = None
		self.clients = []
		self.connected = 0
		self.maxConnections = max_connections
		self.currentVideo = None

	def set_sender_ip(self, sender_ip):
		self.sender_ip = sender_ip

	def set_current_video(self, video):
		self.currentVideo = video

	def get_current_video(self):
		return self.currentVideo

# Receive data from server
class ServerReceiver(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client

	def run(self):
		self._stopped = False

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
			sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			sk_server.bind(('', 9091))
			sk_server.listen(1)

			file_num = 0

			while not self._stopped:
				content, address = sk_server.accept()

				# Recebe o nome do arquivo
				nome = "{}.mkv".format(file_num)
				sys.stdout.write("Recebendo '{}' de {}.\n".format(nome, address[0]))
				sys.stdout.flush()

				# Recebe o arquivo
				with open(nome, 'wb') as down_file:
					recv_read = content.recv(BUFFER_SIZE)
					while recv_read:
						down_file.write(recv_read)
						recv_read = content.recv(BUFFER_SIZE)

				print(">>>> ", len(self.client.clients))
				for _, cliente in enumerate(self.client.clients):
					print("[*] Enviando (arquivo {0}) para o cliente {1}.".format(
						nome,
						cliente
					))
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_client:
						sk_client.connect((cliente, 9092))

						# sk_client.send(bytes(nome1))

						with open(nome, 'rb') as up_file:
							send_read = up_file.read(BUFFER_SIZE)
							while send_read:
								sk_client.send(send_read)
								send_read = up_file.read(BUFFER_SIZE)

				# lock.acquire()
				self.client.set_current_video(nome)
				# lock.release()
				print(client.currentVideo)

				# time.sleep(2)
				content.close()
				# file_num += 1

	def stop(self):
		self._stopped = True

#Receive data from another client
class ClientReceiver(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		self.client = client

	def run(self):
		self._stopped = False

		socketserver.TCPServer.allow_reuse_address = True
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
			sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			print("Aguardando conexão...")

			sk_server.bind(('', 9092))
			sk_server.listen(1)

			file_num = 0

			while not self._stopped:
				content, address = sk_server.accept()

				# nome = content.recv(BUFFER_SIZE).decode('utf-8')

				# Recebe o nome do arquivo
				nome = "{}.mkv".format(file_num)
				sys.stdout.write("Recebendo '{}' de {}.\n".format(nome, address[0]))
				sys.stdout.flush()

				print("ARQUIVO ATUAL: ", nome)

				# Recebe o arquivo
				with open(nome, 'wb') as down_file:
					recv_read = content.recv(BUFFER_SIZE)
					while recv_read:
						down_file.write(recv_read)
						recv_read = content.recv(BUFFER_SIZE)

				# file_num += 1
				# lock.acquire()
				self.client.set_current_video(nome)
				# lock.release()
				# content.close()

	def stop(self):
		self._stopped = True


class Player():
	def __init__(self, path):
		self.vlc_instance = vlc.Instance('--quiet')
		self.player = self.vlc_instance.media_player_new()
		self.path = path
		self.vetor = []

	def listMovies(self):
		os.chdir("./")
		for file in glob.glob("*.mkv"):
			self.vetor.append(file)
		return self.vetor

	def play(self, file):
		# file = nome do arquivo. ex: '_000040.mkv'''
		media = self.vlc_instance.media_new(self.path + file)
		self.player.set_media(media)
		self.player.play()


class ExibeVideos(threading.Thread):
	def __init__(self, client):
		threading.Thread.__init__(self)
		Player.__init__(self, "./")
		self.client = client

	def run(self):
		while True:
			# player = Player('./')
			if self.client.currentVideo is not None:
				nomeMovie = self.client.currentVideo
				Player.play(self, nomeMovie)
				time.sleep(2)
				# os.remove('./'+nomeMovie)
			# lista = player.listMovies()
			# for file in lista:

# IP e porta do servidor
TCP_HOST = '191.52.76.36'  # IP
TCP_PORT = 6060  # porta
BUFFER_SIZE = 1024  # Normally 1024
qtd_max = int(input("Digite a quantidade de Usuários que poderão se conectar: "))

dest = (TCP_HOST, TCP_PORT)

msg = None

client = Client(qtd_max)
serverReceiver = ServerReceiver(client)
clientReceiver = ClientReceiver(client)

# recep.daemon = True

def conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, client):
	while True:
		msg = input()
		# tcp.connect(dest)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
			print(TCP_HOST)
			tcp.connect(dest)

			print("Enviado:", msg)

			# Sair do canal
			if msg[0:2] == '12':
				serverReceiver.stop()
				serverReceiver.join()
				# client = Client()

				# recep.stop()
				# recep.join()
				# recep = Receptor()

			tcp.send(bytes(msg, encoding='utf-8'))

			# Entrou em um canal
			if msg[0:2] == '10':
				# Recebe a mensagem de resposta
				#   "10" -> conectcou
				#   "00" -> nao conectou
				# message = ""
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
					sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

					sk_server.bind(('', 9091))
					sk_server.listen(1)

					content, address = sk_server.accept()

					received_msg = content.recv(BUFFER_SIZE)
					message = str(received_msg, 'utf-8')

				if message == "00":
					# AQUI É ONDE O CLIENTE PROCURA OUTRO CLIENTE PARA RECEBER OS ARQUIVOS
					print("Limite de canais conectados ao servidor excedidos.")

					# print("Digite o ip para se conectar a outro cliente: ")
					# client_ip = input()

					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						tcp2.connect((TCP_HOST, 6060))
						teste = "11" + msg[-1]
						tcp2.send(bytes(teste, encoding='utf-8'))

						clients_ip = str(tcp2.recv(BUFFER_SIZE), 'utf-8')
						clients_ip = handle_ip_list(clients_ip)

					# client_ip = '191.52.64.32'
					# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp3:
					# 	# print("IP TENTANDO CONECTAR: ", ip)
					# 	tcp3.connect((client_ip, 9093))
					# 	# tcp3.send(bytes("teste", encoding='utf-8'))
					# 	resp = str(tcp3.recv(BUFFER_SIZE), 'utf-8')
					# 	if resp == "OK":
					# 		client_ip = ip
					# 		break
					#
					# 	tcp3.close()

					client_ip = None
					# client_ip = str(client_ip)
					socketserver.TCPServer.allow_reuse_address = True
					for ip in clients_ip:
						with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp3:
							print("IP TENTANDO CONECTAR: ", ip)
							tcp3.connect((ip, 9093))
							resp = str(tcp3.recv(BUFFER_SIZE), 'utf-8')
							# print("RESPOSTA: ", resp)
							if resp == "OK":
								print("DEU BOM!")
								client_ip = ip
								break

							tcp3.close()

					if client_ip is None:
						client_ip = get_available_client(clients_ip)

					# return

					socketserver.TCPServer.allow_reuse_address = True
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
						print("CLIENTE IP: ", client_ip)
						# destiny = (client_ip, 9092)
						tcp2.connect((client_ip, 9095))
						tcp2.sendall(bytes("teste", encoding='utf-8'))
						tcp2.close()

					client.set_sender_ip(client_ip)
					clientReceiver.start()

					clientServer = ClientServer(client, "./")
					clientServer.start()

					x = ExibeVideos(client)
					x.start()

					while True:
						msg = input()

						if msg == "123":
							print("IP do cliente emissor: {} \n\n".format(client.sender_ip))
							print("IPs do(s) cliente(s) que recebem dados deste cliente em analise:")

							if len(client.clients) > 0:
								for client_receiver in client.clients:
									print(client_receiver + "\n")

							else:
								print("Nenhum cliente conectado a este")
						else:
							print("Comando Invalido!")


				elif not serverReceiver.is_alive():
					serverReceiver.start()

					clientServer = ClientServer(client, "./")
					clientServer.start()
					# print(client.currentVideo)
					x = ExibeVideos(client)
					x.start()
					# x = ExibeVideos(client)
					# x.start()

			# lista de clientes conectados
			if msg[0:2] == '11':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			# quantidade de clientes conectados
			if msg[0:2] == '13':
				print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

			tcp.shutdown(socket.SHUT_RDWR)

# def handle_ip_list(ip_list):
# 	ips1 = ip_list.split('[')[-1]
# 	ips2 = ips1.split(']')[0]
# 	ips = ips2.split(',')
#
# 	teste = []
#
# 	for ip in ips:
# 		teste.append(ip)
#
# 	return teste

def handle_ip_list(ip_list):
	cont = len(ip_list)
	i = 0
	teste = ''
	ips = []
	while i < cont:
		if ip_list[i] == ',' or ip_list[i] == ']':
			# print(">>>", teste)
			ips.append(teste)
			teste = ''

		else:
			if ip_list[i] != ' ' and ip_list[i] != '[' and ip_list[i] != "'":
				teste += ip_list[i]

		i += 1

	return ips

def get_available_client(clients_ip):
	for ip in clients_ip:
		if is_available(ip):
			return ip

	for ip in clients_ip:
		get_available_client(ip)

def is_available(ip):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
		tcp.connect((ip, 9093))
		msg = str(tcp.recv(BUFFER_SIZE), 'utf-8')
		tcp.close()

		if msg == "OK":
			return True

		else:
			return False


conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, client)

