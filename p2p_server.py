'''
@ Class Server
@ Date 2022/10/13
@ Auther whitocowworkgood
'''

import socket
import threading
import random
import json
import hashlib

class Server:
    
    def send(self, client_socket):
        
        while True:
            data={'User':"Server"}
            message = input()

            if message == 'quit':
                data['Message'] = str('quit')
                
                send_data = json.dumps(data)
                client_socket.send(send_data.encode('utf-8')) 
                break
            else:
                data['Message'] = str(message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                data['Hash'] = word
            
                send_data = json.dumps(data)
                client_socket.send(send_data.encode('utf-8')) 
        #client_socket.close()

    def recv(self, client_socket):
        while True:
            try:

                data = json.loads(client_socket.recv(1024).decode('utf-8'))
                
                if data['Message'] == 'quit':
                    break
                else:
                    if(data['Hash'] == hashlib.sha256(data['Message'].encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'], data['Message']))
                    else:
                        print("메시지가 변조되었습니다.")

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

    
