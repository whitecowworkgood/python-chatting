'''
@ Class Server
@ Date 2022/10/15
@ Auther whitocowworkgood
'''
#----------------import ----------------------------------------------------------
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
#----------------END import -------------------------------------------------------
class Server:
    
    # Start __init__-----------------------------
    def __init__(self):

        self.server_path='./server'
        self.server_name= str(random.randrange(0, 1000))

        self.server_pri_file = self.server_path+'/'+self.server_name+'_prikey.pem'
        self.server_pub_file = self.server_path+'/'+self.server_name+'_pubkey.pem'

        self.data={'User':self.server_name}
        self.client_name = None

        self.client_pubkey = None
        self.server_prikey = None
        self.server_pubkey = None
        
        #Make Socket----------------------------------------------------
        port = random.randrange(9999, 13000)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1',port)) 
        self.server_socket.listen(5)
        #End Make Socket----------------------------------------------------
        print("----------[System] Socket Start----------")

        print('서버 작동: 연결 포트 -> '+ str(port))
        print('연결 대기중.....')
        self.client_socket, addr = self.server_socket.accept()

        print("----------[System] Socket Connect----------")

        #서로의 이름 수신
        self.client_name = self.client_socket.recv(1024).decode('utf-8')
        #print(self.client_name)
        self.client_socket.send(self.server_name.encode('utf-8'))

        #End __init__----------------------------------

        

    def generate_keyset(self):

        
        #개인키가 있으면 읽는 부분
        if os.path.isfile(self.server_pri_file):
            
            self.server_prikey = make_key.read_pri_pem(self.server_pri_file)

            #공개키가 있으면 삭제 후 다시 생성
            if os.path.isfile(self.server_pub_file):

                os.remove(self.server_pub_file)
                self.server_pubkey = make_key.pub_key_gen(self.server_pub_file, self.server_prikey)
            
            #공개키가 없으면 생성
            else:
                self.server_pubkey = make_key.pub_key_gen(self.server_pub_file,self.server_prikey)

        #개인키가 없으면 생성 후 읽는 기능
        else:

            make_key.pri_key_gen(self.server_pri_file)
            self.server_prikey = make_key.read_pri_pem(self.server_pri_file)

            #공개키가 있으면 삭제 후 다시 생성
            if os.path.isfile(self.server_pub_file):

                os.remove(self.server_pub_file)
                self.server_pubkey = make_key.pub_key_gen(self.server_pub_file, self.server_prikey)
            
            #공개키가 없으면 생성
            else:
                self.server_pubkey = make_key.pub_key_gen(self.server_pub_file, self.server_prikey)
    
    def public_key_share(self):

        self.client_socket.send(bytes(make_key.share_read_pub(self.server_pub_file), encoding='utf-8'))

        self.client_pubkey = self.client_socket.recv(1024)
        self.client_pubkey = RSA.import_key(self.client_pubkey)

    def send(self):
        
        while True:
            
            message = input()

            if message == '/quit':
                
                self.data['Message'] = make_key.encrypt_msg(self.client_pubkey, message)
                
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 
                print("----------[System] Sender Exit----------")
                break
            else:

                self.data['Message'] =  make_key.encrypt_msg(self.client_pubkey, message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                self.data['Hash'] = word
            
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 


    def recv(self):
        while True:
            try:

                data = json.loads(self.client_socket.recv(1024).decode('utf-8'))
                
                if make_key.decrypt_msg(self.server_prikey, data['Message']) == '/quit':
                    print("----------[System] Recever Exit----------")
                    break
                else:
                    if(data['Hash'] == hashlib.sha256(make_key.decrypt_msg(self.server_prikey, data['Message']).encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],  make_key.decrypt_msg(self.server_prikey, data['Message'])))
                    else:
                        print("메시지가 변조되었습니다.")
                
            except Exception as e:
                print(e)
                break

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
    server.run()

    
