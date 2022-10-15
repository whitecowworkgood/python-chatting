'''
@ Class Server
@ Date 2022/10/15
@ Auther whitocowworkgood
'''

import socket
import threading
import random
import json
import hashlib
import os
import sys
import shutil
import time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import base64
import make_key
class Server:
    
    def __init__(self):
        self.data={'User':"Server"}
        self.client_name = None

        self.client_pubkey = None
        self.server_prikey = None
        self.server_pubkey = None

        

        port = random.randrange(9999, 13000)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1',port)) 
        self.server_socket.listen(5) 

        print('서버 작동: 연결 포트 -> '+ str(port))
        print('연결 대기중.....')
        self.client_socket, addr = self.server_socket.accept()
        print("연결 완료!!")

        #서로의 이름 수신
        self.client_name = self.client_socket.recv(1024).decode('utf-8')
        #print(self.client_name)
        self.client_socket.send('server'.encode('utf-8'))


        

    def generate_keyset(self):

        if os.path.isfile("./server/%s_prikey.pem" % ("server")):
            
            self.server_prikey = make_key.read_pri_pem('./server', "server")

            if os.path.isfile("./server/%s_pubkey.pem" % ("server")):

                os.remove("./server/%s_pubkey.pem" % ("server"))
                self.server_pubkey = make_key.pub_key_gen(self.server_prikey)
                make_key.save_pub_key('./server', 'server', self.server_pubkey)

            else:
                self.server_pubkey = make_key.pub_key_gen(self.server_prikey)
                make_key.save_pub_key('./server', 'server', self.server_pubkey)
       
        else:
            make_key.pri_key_gen('./server', "server")
            self.server_prikey = make_key.read_pri_pem('./server', "server")

            if os.path.isfile("./server/%s_pubkey.pem" % ("server")):

                os.remove("./server/%s_pubkey.pem" % ("server"))
                self.server_pubkey = make_key.pub_key_gen(self.server_prikey)
                make_key.save_pub_key('./server', 'server', self.server_pubkey)
            else:

                self.server_pubkey = make_key.pub_key_gen(self.server_prikey)
                make_key.save_pub_key('./server', 'server', self.server_pubkey)

    
    def public_key_share(self):
        #원래는 소캣으로 해야하지만 우선 이렇게 만든다.
        '''
        if os.path.isfile('./server/%s_pubkey.pem' % (self.client_name)):
            self.client_pubkey = make_key.read_pub_pem('./server', self.client_name)

        else:
            self.client_socket.send('key'.encode('utf-8'))
            self.file_data=self.client_socket.recv(1024)
            fd = open('./server/%s_pubkey.pem'%(self.client_name), 'wb+')
            fd.write(bytes(self.file_data))
            fd.close()

        
        if self.client_socket.recv(1024).decode('utf-8') == 'public':
            fd=open("./server/%s_pubkey.pem" % ('server'), 'rb+')
            
            self.client_socket.send(str(f.read(1024)).encode('utf-8'))
            fd.close()
        '''
        #임시로 공유를 하고 암복호화를 확인하기 위한 코드
        if os.path.isfile('./server/%s_pubkey.pem'%(self.client_name)):
           self.client_pubkey =  make_key.read_pub_pem('./server', self.client_name)
        else:
            filename = '%s_pubkey.pem' % (self.client_name)
            src = './client/'
            dir = './server/'
            shutil.copy(src+filename, dir+filename)

            time.sleep(2)
            self.client_pubkey =  make_key.read_pub_pem('./server', self.client_name)
    
    def send(self):
        
        while True:
            
            message = input()

            if message == 'quit':
                
                self.data['Message'] = make_key.encrypt_msg(self.client_pubkey, message)
                
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 
                break
            else:

                self.data['Message'] =  make_key.encrypt_msg(self.client_pubkey, message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                self.data['Hash'] = word
            
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 
        #client_socket.close()

    def recv(self):
        while True:
            try:

                data = json.loads(self.client_socket.recv(1024).decode('utf-8'))
                
                if make_key.decrypt_msg(self.server_prikey, data['Message']) == 'quit':
                    break
                else:
                    if(data['Hash'] == hashlib.sha256(make_key.decrypt_msg(self.server_prikey, data['Message']).encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],  make_key.decrypt_msg(self.server_prikey, data['Message'])))
                    else:
                        print("메시지가 변조되었습니다.")
                
            except Exception as e:
                print(e)
                break
        #client_socket.close()
    def run(self):
        
        self.generate_keyset()
        time.sleep(2)
        self.public_key_share()

        sender = threading.Thread(target=self.send, args=())
        sender.start()

        receiver = threading.Thread(target=self.recv, args=())
        receiver.start()

if __name__ == '__main__':
    server = Server()
    #server.public_key_share()
    server.run()

    
