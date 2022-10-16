from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import base64

#----------RSA키 생성----------
def pri_key_gen(target):
    
    pri_key = RSA.generate(1024)
    f=open(target, 'wb+')
    f.write(pri_key.exportKey('PEM'))
    f.close()
 
def pub_key_gen(target, pri_key):
    pub_key = pri_key.public_key()
    f=open(target, 'wb+')
    f.write(pub_key.exportKey('PEM'))
    f.close()

    return pub_key

#---------PEM파일에서 키값 읽기------------
def read_pri_pem(target):
    prikey = RSA.import_key(open(target).read())
    return prikey

def read_pub_pem(target):
    pubkey = RSA.import_key(open(target).read())
    return pubkey

#----------공개키 공유를 위한 따로 읽기 기능------------
def share_read_pub(target):

    return open(target).read()


#-------------암 복호화 부분----------------
def encrypt_msg(pubkey, msg):

    cipher = PKCS1_OAEP.new(pubkey)
    ciphertext = cipher.encrypt(msg.encode('utf-8'))
    enc_cipher_msg = base64.b64encode(ciphertext)

    return enc_cipher_msg.decode('utf-8')

def decrypt_msg(prikey, cipher):
    
    msg = PKCS1_OAEP.new(prikey)
    dec_cipher = base64.b64decode(cipher)

    msg_str = msg.decrypt(dec_cipher)

    return msg_str.decode('utf-8')
