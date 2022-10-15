from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import base64

def pri_key_gen(path, target):
    
    pri_key = RSA.generate(1024)
    #print(type(pri_key))
    f=open("%s/%s_prikey.pem" % (path, target), 'wb+')
    f.write(pri_key.exportKey('PEM'))
    f.close
 
def pub_key_gen(pri_key):
    pub_key = pri_key.public_key()
    return pub_key

def save_pub_key(path, target, pub_key):
    f=open("%s/%s_pubkey.pem" % (path, target), 'wb+')
    f.write(pub_key.exportKey('PEM'))
    f.close

def read_pri_pem(path, target):
    prikey = RSA.import_key(open('%s/%s_prikey.pem' % (path, target)).read())
    return prikey

def read_pub_pem(path, target):
    pubkey = RSA.import_key(open('%s/%s_pubkey.pem' % (path, target)).read())
    return pubkey



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

if __name__ == '__main__':


    pri_key_gen("./", "test")
    '''
    msg = 'HelloBlockChain'
    
    print("메시지: ", end='')
    print(msg, end="\n")

    cipher = encrypt_msg(msg.encode('utf-8'))
    decrypt_msg(cipher)
    '''