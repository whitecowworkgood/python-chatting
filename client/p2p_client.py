'''
@ Class Client
@ Date 2022/10/16
@ Auther whitocowworkgood
'''
#----------------import ----------------------------------------------------------
import socket
import random
import threading
import json
import hashlib
import os
import sys
import shutil
import time
import base64

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import make_key
#----------------END import -------------------------------------------------------

class Client:

    # Start __init__-----------------------------
    def __init__(self):

        self.client_path='./client/key'

        if os.path.isdir(self.client_path):
            pass
        else:
            os.makedirs(self.client_path)
        
        self.user = str(input('사용자 명을 입력해 주세요: '))

        self.client_pri_file = self.client_path+'/'+self.user+'_prikey.pem'
        self.client_pub_file = self.client_path+'/'+self.user+'_pubkey.pem'

        self.data={'User':self.user}
        self.server_name = None

        self.client_pubkey = None
        self.client_prikey = None
        self.server_pubkey = None
        
    #End __init__----------------------------------
        
    def make_socket(self):

        print("----------[System] Socket Start----------")

        HOST = str(input("연결할 서버 주소를 입력하세요: "))
        PORT = int(input("연결할 서버 포트를 입력하세요: "))
        
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.client_socket.connect((HOST, PORT))

        #서로의 이름 전송
        self.client_socket.send(self.user.encode('utf-8'))
        self.server_name = self.client_socket.recv(1024).decode('utf-8')

        print("----------[System] Socket Connect----------")

    def generate_keyset(self):
        
        if os.path.isfile(self.client_pri_file):
            self.client_prikey = make_key.read_pri_pem(self.client_pri_file)
            
            if os.path.isfile(self.client_pub_file):

                os.remove(self.client_pub_file)
                self.client_pubkey = make_key.pub_key_gen(self.client_pub_file,self.client_prikey)
            
            else:
                self.client_pubkey = make_key.pub_key_gen(self.client_pub_file,self.client_prikey)

        else:
            self.client_prikey = make_key.pri_key_gen(self.client_pri_file)
            
            if os.path.isfile(self.client_pub_file):

                os.remove(self.client_pub_file)
                self.client_pubkey = make_key.pub_key_gen(self.client_pub_file, self.client_prikey)
            else:

                self.client_pubkey = make_key.pub_key_gen(self.client_pub_file, self.client_prikey)
    
    def public_key_share(self):

        self.server_pubkey = self.client_socket.recv(1024)
        
        self.server_pubkey = RSA.import_key(self.server_pubkey)

        self.client_socket.send(bytes(make_key.share_read_pub(self.client_pub_file), encoding='utf-8'))

    def send(self):
        while True:
            
            message = input()
            if message == '/quit':
                self.data['Message'] =  make_key.encrypt_msg(self.server_pubkey, message)
                
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8'))
                print("----------[System] Sender Exit----------")
                break
            else:
                self.data['Message'] =  make_key.encrypt_msg(self.server_pubkey, message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                self.data['Hash'] = word
            
                send_data = json.dumps(self.data)

                self.client_socket.send(send_data.encode('utf-8')) 

    def recv(self):
        while True:
            try:
                data = json.loads(self.client_socket.recv(1024).decode('utf-8'))
                
                if  make_key.decrypt_msg(self.client_prikey, data['Message']) == '/quit':
                    print("----------[System] Recever Exit----------")
                    break
                else:
                    if(data['Hash'] == hashlib.sha256( make_key.decrypt_msg(self.client_prikey, data['Message']).encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],make_key.decrypt_msg(self.client_prikey, data['Message'])))
                    else:
                        print("메시지가 변조되었습니다.")

            except Exception as e:
                print(e)
                break


    def run(self):
        self.make_socket()

        self.generate_keyset()
        time.sleep(1)
        self.public_key_share()

        receiver = threading.Thread(target=self.recv, args=())
        receiver.start()

        sender = threading.Thread(target=self.send, args=())
        sender.start()
        
        
        
if __name__ == '__main__':
   
    client = Client()
    client.run()
