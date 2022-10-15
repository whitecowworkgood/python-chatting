'''
@ Class Client
@ Date 2022/10/15
@ Auther whitocowworkgood
'''

import socket
import random
import threading
import json
import hashlib
import os
import sys
import shutil
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import base64
import make_key

class Client:
    def __init__(self):
        #self.user = random.randrange(1000, 13000)
        self.data={'User':str(self.user)}
        self.server_pubkey=None

        

        HOST = str(input("연결할 서버 주소를 입력하세요: "))
        PORT = int(input("연결할 서버 포트를 입력하세요: "))
        
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

        self.client_socket.connect((HOST, PORT))

        #서로의 이름 전송
        self.client_socket.send(str(self.user).encode('utf-8'))
        self.server_name = self.client_socket.recv(1024).decode('utf-8')
        
        


    def generate_keyset(self):
        
        if os.path.isfile("./client/%s_prikey.pem" % (str(self.user))):
            self.client_prikey = make_key.read_pri_pem('./client', str(self.user))
            
            if os.path.isfile("./client/%s_pubkey.pem" % (str(self.user))):

                os.remove("./client/%s_pubkey.pem" % (str(self.user)))
                self.client_pubkey = make_key.pub_key_gen(self.client_prikey)
                make_key.save_pub_key('./client', str(self.user), self.client_pubkey)
            
            else:
                self.client_pubkey = make_key.pub_key_gen(self.client_prikey)
                make_key.save_pub_key('./client',str(self.user), self.client_pubkey )

        else:
            make_key.pri_key_gen('./client', str(self.user))
            self.client_prikey = make_key.read_pri_pem('./client', str(self.user))
            
            if os.path.isfile("./client/%s_pubkey.pem" % (str(self.user))):

                os.remove("./client/%s_pubkey.pem" % (str(self.user)))
                self.client_pubkey = make_key.pub_key_gen(self.client_prikey)
                make_key.save_pub_key('./client', str(self.user), self.client_pubkey)
            else:

                self.client_pubkey = make_key.pub_key_gen(self.client_prikey)
                make_key.save_pub_key('./client', str(self.user), self.client_pubkey)
    
    def public_key_share(self):
        #원래는 소캣이지만, 이렇게 한다.
        '''
        if os.path.isfile('./client/%s_pubkey.pem' % (self.server_name)):
            self.client_pubkey = make_key.read_pub_pem('./client', self.server_name)
            
        else:

            self.file_data=self.client_socket.recv(1024)
            fd = open('./client/%s_pubkey.pem'%(self.server_name), 'wb+')
            fd.write(bytes(self.file_data))
            fd.close()

            self.client_socket.send("public".encode('utf-8'))
        

        if self.client_socket.recv(1024).decode('utf-8') == 'public':
            fd=open("./client/%s_pubkey.pem" % (self.server_name), 'rb+')
            
            self.client_socket.send(str(f.read(1024)).encode('utf-8'))
            fd.close()
        '''
        #임시로 공유를 하고 암복호화를 확인하기 위한 코드
        if os.path.isfile('./client/%s_pubkey.pem'%('server')):
            self.server_pubkey =  make_key.read_pub_pem('./client', 'server')
        else:
            filename = '%s_pubkey.pem' % (self.user)
            src = './client/'
            dir = './server/'
            shutil.copy(src+filename, dir+filename)
            self.server_pubkey =  make_key.read_pub_pem('./client', 'server')

    def send(self):
        while True:
            
            message = input()
            if message == 'quit':
                self.data['Message'] =  make_key.encrypt_msg(self.server_pubkey, message)
                
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 
                break
            else:
                self.data['Message'] =  make_key.encrypt_msg(self.server_pubkey, message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                self.data['Hash'] = word
            
                send_data = json.dumps(self.data)

                self.client_socket.send(send_data.encode('utf-8')) 
        #client_socket.close()

    def recv(self):
        while True:
            try:
                data = json.loads(self.client_socket.recv(1024).decode('utf-8'))
                
                if  make_key.decrypt_msg(self.client_prikey, data['Message']) == 'quit':
                    #client_socket.send('quit'.encode('utf-8'))
                    break
                else:
                    if(data['Hash'] == hashlib.sha256( make_key.decrypt_msg(self.client_prikey, data['Message']).encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],make_key.decrypt_msg(self.client_prikey, data['Message'])))
                    else:
                        print("메시지가 변조되었습니다.")

            except Exception as e:
                print(e)
                break
        #client_socket.close()

    def run(self):
        
        self.generate_keyset()
        self.public_key_share()

        receiver = threading.Thread(target=self.recv, args=())
        receiver.start()

        sender = threading.Thread(target=self.send, args=())
        sender.start()

        
        
if __name__ == '__main__':
   
    client = Client()
    #client.public_key_share()
    client.run()
