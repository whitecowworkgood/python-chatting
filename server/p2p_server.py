'''
@ Class Server
@ Date 2022/10/17
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
import base64

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import make_key
#----------------END import -------------------------------------------------------
class Server:
    
    # Start __init__-----------------------------
    def __init__(self):

        self.server_key_path='./server/key'

        if os.path.isdir(self.server_key_path):
            pass
        else:
            os.makedirs(self.server_key_path)

        self.server_name= str('Server')

        self.server_private_key_file = self.server_key_path+'/'+self.server_name+'_prikey.pem'
        self.server_public_key_file = self.server_key_path+'/'+self.server_name+'_pubkey.pem'

        self.data={'User':self.server_name}
        self.client_name = None

        self.client_public_key = None
        self.server_private_key = None
        self.server_public_key = None
        
        #End __init__----------------------------------

    def make_socket(self):

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


    def generate_keyset(self):

        
        #개인키가 있으면 읽는 부분
        if os.path.isfile(self.server_private_key_file):
            
            self.server_private_key = make_key.read_pri_pem(self.server_private_key_file)

            #공개키가 있으면 삭제 후 다시 생성
            if os.path.isfile(self.server_public_key_file):

                os.remove(self.server_public_key_file)
                self.server_public_key = make_key.pub_key_gen(self.server_public_key_file, self.server_private_key)
            
            #공개키가 없으면 생성
            else:
                self.server_public_key = make_key.pub_key_gen(self.server_public_key_file,self.server_private_key)

        #개인키가 없으면 생성 후 읽는 기능
        else:

            self.server_private_key = make_key.pri_key_gen(self.server_private_key_file)

            #공개키가 있으면 삭제 후 다시 생성
            if os.path.isfile(self.server_public_key_file):

                os.remove(self.server_public_key_file)
                self.server_public_key = make_key.pub_key_gen(self.server_public_key_file, self.server_private_key)
            
            #공개키가 없으면 생성
            else:
                self.server_public_key = make_key.pub_key_gen(self.server_public_key_file, self.server_private_key)
    
    def public_key_share(self):

        self.client_socket.send(bytes(make_key.share_read_pub(self.server_public_key_file), encoding='utf-8'))

        self.client_public_key = self.client_socket.recv(1024)
        self.client_public_key = RSA.import_key(self.client_public_key)

    def send(self):
        
        while True:
            
            message = input()

            if message == '/quit':
                
                self.data['Message'] = make_key.encrypt_msg(self.client_public_key, message)
                
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 
                print("----------[System] Sender Exit----------")
                break
            else:

                self.data['Message'] =  make_key.encrypt_msg(self.client_public_key, message)
            
                word = hashlib.sha256(message.encode('utf-8')).hexdigest()
                self.data['Hash'] = word
            
                send_data = json.dumps(self.data)
                self.client_socket.send(send_data.encode('utf-8')) 


    def recv(self):
        while True:
            try:

                data = json.loads(self.client_socket.recv(1024).decode('utf-8'))
                
                if make_key.decrypt_msg(self.server_private_key, data['Message']) == '/quit':
                    print("----------[System] Recever Exit----------")
                    break
                else:
                    if(data['Hash'] == hashlib.sha256(make_key.decrypt_msg(self.server_private_key, data['Message']).encode('utf-8')).hexdigest()):
                        print('%s: %s' %(data['User'],  make_key.decrypt_msg(self.server_private_key, data['Message'])))
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

        sender = threading.Thread(target=self.send, args=())
        sender.start()

        receiver = threading.Thread(target=self.recv, args=())
        receiver.start()


if __name__ == '__main__':
    server = Server()
    server.run()
