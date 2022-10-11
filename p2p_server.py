import socket
import threading
import random
import json

class Server:
    
    def send(self, client_socket):
        while True:
            message = input()
            if message == 'quit':
                client_socket.send('quit'.encode('utf-8'))
                break
            client_socket.send(message.encode('utf-8')) 
        #client_socket.close()

    def recv(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data.decode('utf-8') == 'quit':
                    break
                print('%s: %s' %("client",data.decode('utf-8'))) 
            except Exception as e:
                print(e)
                break
        #client_socket.close()
    def run(self):
        
        port = random.randrange(9999, 13000)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', port)) 
        server_socket.listen(5) 

        print('서버 작동: 연결 포트 -> '+ str(port))
        print('연결 대기중.....')
        client_socket, addr = server_socket.accept()

        sender = threading.Thread(target=self.send, args=(client_socket,))
        sender.start()

        receiver = threading.Thread(target=self.recv, args=(client_socket,))
        receiver.start()

if __name__ == '__main__':
    server = Server()
    server.run()

    