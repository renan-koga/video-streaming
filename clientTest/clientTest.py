import socket
import socketserver
import threading
import sys
import time, sys


class Receptor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self._stopped = False

        socketserver.TCPServer.allow_reuse_address = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
            sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            sk_server.bind(('', 9092))
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

                content.close()
                file_num += 1

    def stop(self):
        self._stopped = True


# IP e porta do servidor
TCP_HOST = '191.52.64.32'  # IP
TCP_PORT = 6060  # porta
BUFFER_SIZE = 1024  # Normally 1024
qtd_max = int(input("Digite a quantidade de Usuários que poderão se conectar: "))

dest = (TCP_HOST, TCP_PORT)

msg = None

recep = Receptor()


# recep.daemon = True


def conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, recep):
    while True:
        msg = input()
        # tcp.connect(dest)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
            print(TCP_HOST)
            tcp.connect(dest)

            print("Enviado:", msg)

            # Sair do canal
            if msg[0:2] == '12':
                recep.stop()
                recep.join()
                recep = Receptor()

            tcp.send(bytes(msg, encoding='utf-8'))

            # Entrou em um canal
            if msg[0:2] == '10':
                # Recebe a mensagem de resposta
                #   "10" -> conectcou
                #   "00" -> nao conectou
                message = ""
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk_server:
                    sk_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    sk_server.bind(('', 9091))
                    sk_server.listen(1)

                    content, address = sk_server.accept()

                    received_msg = content.recvmsg(BUFFER_SIZE)
                    message = str(received_msg[0], 'utf-8')

                if message == "00":
                    # AQUI É ONDE O CLIENTE PROCURA OUTRO CLIENTE PARA RECEBER OS ARQUIVOS
                    print("Limite de canais conectados ao servidor excedidos.")

                    print("Digite o ip para se conectar a outro cliente: ")
                    clientIp = input()

                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp2:
                        tcp2.connect(clientIp, 9092)
                        tcp2.send(bytes("teste", encoding='utf-8'))
                        tcp2.close()

                    recep.start()


                    # dest = (TCP_HOST, TCP_PORT)

                    # conecta(TCP_HOST,TCP_PORT,BUFFER_SIZE,dest,msg,recep)

                elif not recep.is_alive():
                    recep.start()

            # lista de clientes conectados
            if msg[0:2] == '11':
                print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

            # quantidade de clientes conectados
            if msg[0:2] == '13':
                print(str(tcp.recv(BUFFER_SIZE), 'utf-8'))

            tcp.shutdown(socket.SHUT_RDWR)


conecta(TCP_HOST, TCP_PORT, BUFFER_SIZE, dest, msg, recep)