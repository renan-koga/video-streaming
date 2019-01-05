# coding=utf-8
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

class ClientSender(threading.Thread):
    def __init__(self, ip, cont, canal):
        threading.Thread.__init__(self)
        self.ip = ip
        self.maxConnections = cont
        self.canal = canal

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

            while cont < self.maxConnections:
                print("Aguardando conexão no IP: ", self.ip)
                connection, address = tcp.accept()

                try:
                    print("Conectado ", address)
                    lock.acquire()
                    self.canal.add_cliente(address[0])
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


class CanalThread(threading.Thread):
    def __init__(self, ip, macConnection, canal_id, path):
        threading.Thread.__init__(self)

        self.ip = ip
        self.sk_client = None
        self.client_send = None
        self.maxConnection = macConnection
        self.clients     = []
        self.canal_id    = canal_id
        self.path        = path
        self.curr_file   = 0
        self.total_files = len(listdir(self.path))

        self.nome_base   = listdir(self.path)[0].split('_')[0]

        print("Thread teste iniciada")
        # print("[+] Nova thread iniciada para o canal {}".format(self.canal_id))
    
    def run(self):
        self.client_send = ClientSender(self.ip, self.maxConnection, self)
        self.client_send.start()

        # socketserver.TCPServer.allow_reuse_address = True
        # logic = True
        # # while True:
        # with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as tcp:
        #     tcp.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
        #
        #     origin = (self.ip, PORTA_SAIDA)
        #     tcp.bind(origin)
        #     print("Aguardando conexão no IP: ", self.ip)
        #     # tcp.connect((self.ip, PORTA_SAIDA))
        #     tcp.listen(1)
        #
        #     while logic:
        #         print("Esperando por conexão")
        #         connection, address = tcp.accept()
        #
        #         try:
        #             print("Conectado ", address)
        #
        #             while True:
        #                 msg = connection.recv(BUFFER_SIZE)
        #                 print(str(msg, 'utf-8'))
        #                 if not msg:
        #                     logic = False
        #                     break
        #                 # msg = "teste"
        #                 # tcp.send(bytes(msg, encoding='utf-8'))
        #         finally:
        #             tcp.close()

        # tcp.shutdown()
        # tcp.close()
        # self.sk_client = connection
        # self.add_cliente(address)
        
        while True:
            tempo_inicial = time.time()

            lock.acquire()
            for _, cliente in enumerate(self.clients):
                print("[*] Enviando canal {0} (arquivo {1}) para o cliente {2}.".format(
                    self.canal_id,
                    self.curr_file,
                    cliente
                ))
                self.enviar_video(cliente)
            lock.release()

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
        print("{} inserido no canal {}".format(ip, self.canal_id))

    def remove_cliente(self, ip):
        if ip in self.clients:
            self.clients.remove(ip)
            print("{} removido do canal {}".format(ip, self.canal_id))
            return True
        return False

    def get_num_clients(self):
        return len(self.clients)

    def enviar_video(self, cliente):
        socketserver.TCPServer.allow_reuse_address = True
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as sk_client:
            sk_client.connect((cliente, 9093))
            sk_client.sendall(bytes("Vai carai", encoding='utf-8'))
            # nome_arq = self.path + "{}_{}.mkv".format(self.nome_base, format(self.curr_file, '05d'))
            #
            # print(nome_arq)
            #
            # # Envia o arquivo
            # with open(nome_arq, 'rb') as up_file:
            #     send_read = up_file.read(BUFFER_SIZE)
            #     while send_read:
            #         sk_client.send(send_read)
            #         send_read = up_file.read(BUFFER_SIZE)

# End class
