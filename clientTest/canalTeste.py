# coding=utf-8
import sys
import threading
import socketserver
import socket as sk
import time
from os import listdir
from threading import Lock, Thread

WAIT_TIME   = 1.8
BUFFER_SIZE = 1024
PORTA_SAIDA = 9092

MAX_CLIENTES_CANAL = 1
lock = Lock()

class ClientServer(threading.Thread):
    def __init__(self, client, path):
        threading.Thread.__init__(self)
        self.client = client
        self.client_sender = ClientSender(client, path)
        self.client_sender.start()
        # self.canal = canal

    def run(self):
        socketserver.TCPServer.allow_reuse_address = True
        logic = True
        cont = 0
        # while True:
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
            tcp.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

            origin = ('', PORTA_SAIDA)
            tcp.bind(origin)
            # tcp.connect((self.ip, PORTA_SAIDA))
            tcp.listen(1)

            while cont < self.client.maxConnections:
                print("Aguardando conexão...")
                connection, address = tcp.accept()

                try:
                    print("Conectado ", address)
                    lock.acquire()
                    self.client_sender.add_cliente(address[0])
                    lock.release()
                    while True:
                        msg = connection.recv(BUFFER_SIZE)
                        print(str(msg, 'utf-8'))
                        if not msg:
                            cont+=1
                            break
                        # msg = "teste"
                        # tcp.send(bytes(msg, encoding='utf-8'))
                finally:
                    tcp.close()


class ClientSender(threading.Thread):
    def __init__(self, client, path):
        threading.Thread.__init__(self)
        self.client = client

        # self.client_send = ClientSender(self.client, self)
        # self.client_send.start()
        # self.maxConnection = maxConnection

        self.sendVideo = None

        self.clients     = []
        self.path        = path
        self.curr_file   = 0
        self.total_files = len(listdir(self.path))

        self.nome_base   = listdir(self.path)[0].split('_')[0]

        print("Thread teste iniciada")
        # print("[+] Nova thread iniciada para o canal {}".format(self.canal_id))
    
    def run(self):

        while True:
            tempo_inicial = time.time()

            # Get the current video name
            lock.acquire()
            curr_video_name = self.client.get_current_video()
            lock.release()

            for _, cliente in enumerate(self.clients):
                print("[*] Enviando (arquivo {0}) para o cliente {1}.".format(
                    curr_video_name,
                    cliente
                ))
                self.enviar_video(cliente, curr_video_name)

            tempo_final  = time.time()
            delta_tempo  = tempo_final - tempo_inicial
            tempo_espera = WAIT_TIME - delta_tempo

            if tempo_espera < 0:
                tempo_espera = 0

            time.sleep(tempo_espera)

            self.curr_file += 1
            if self.curr_file >= self.total_files:
                self.curr_file = 0
    
    def add_cliente(self, ip):
        
        # Se o canal ultrapassar o limite maximo de pessoas conectadas
        # Envia "00"
        if len(self.clients) >= MAX_CLIENTES_CANAL:
            with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
                tcp.connect((ip, PORTA_SAIDA))
                msg = "00"
                tcp.send(bytes(msg, encoding='utf-8'))
            return

        # Senao envia "10"
        # msg = "10"
        # with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
        #     tcp.connect((ip, PORTA_SAIDA))
        #     tcp.send(bytes(msg, encoding='utf-8'))

        self.clients.append(ip)
        print("{} inserido no canal".format(ip))

    def remove_cliente(self, ip):
        if ip in self.clients:
            self.clients.remove(ip)
            print("{} removido do canal {}".format(ip, self.canal_id))
            return True
        return False

    def get_num_clients(self):
        return len(self.clients)


    def enviar_video(self, cliente, curr_video_name):
        socketserver.TCPServer.allow_reuse_address = True
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as sk_client:
            sk_client.connect((cliente, 9092))

            curr_file_num = curr_video_name.split('.')[0]

            # Send the current video number
            sk_client.send(bytes(curr_file_num, encoding='utf-8'))

            # Envia o arquivo
            nome_arq = self.path + curr_video_name
            print(nome_arq)
            with open(nome_arq, 'rb') as up_file:
                send_read = up_file.read(BUFFER_SIZE)
                while send_read:
                    sk_client.send(send_read)
                    send_read = up_file.read(BUFFER_SIZE)

class SendVideo(threading.Thread):
    def __init__(self, client, client_ip):
        threading.Thread.__init__(self)
        self.client = client
        self.clientIp = client_ip

    def run(self):
        socketserver.TCPServer.allow_reuse_address = True
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as sk_client:
            sk_client.connect((self.clientIp, 9092))
            # nome_arq = self.path + "{}_{}.mkv".format(self.nome_base, format(self.curr_file, '05d'))
            #
            # print(nome_arq)

            # teste = str(self.curr_file)

            # sk_client.send(bytes(teste, encoding='utf-8'))

            # lock.acquire()
            send_read = self.client.get_current_video()
            # lock.release()
            while send_read:
                sk_client.send(send_read)
                # lock.acquire()
                send_read = self.client.get_current_video()

# End class
