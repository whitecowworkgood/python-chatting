import socket
import random
import threading

class Client:
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
                    #
                    break
                print('%s: %s' %('server',data.decode('utf-8')))
            except Exception as e:
                print(e)
                break
        #client_socket.close()

    def run(self):
        HOST = str(input("연결할 서버 주소를 입력하세요: "))
        PORT = int(input("연결할 서버 포트를 입력하세요: "))
        
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

        client_socket.connect((HOST, PORT)) 

        sender = threading.Thread(target=self.send, args=(client_socket,))
        sender.start()

        receiver = threading.Thread(target=self.recv, args=(client_socket,))
        receiver.start()
        
if __name__ == '__main__':
   
    client = Client()
    client.run()