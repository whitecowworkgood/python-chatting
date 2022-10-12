import socket
import random
import threading
import json
import hashlib
class Client:
    user = random.randrange(1000, 13000)
    def send(self, client_socket):
        while True:
            data={'User':self.user}
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
                    #client_socket.send('quit'.encode('utf-8'))
                    break
                else:
                    if(data['Hash'] == hashlib.sha256(data['Message'].encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],data['Message']))
                    else:
                        print("메시지가 변조되었습니다.")

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
