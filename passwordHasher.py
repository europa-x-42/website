#!/usr/bin/env python3

import hashlib,binascii,getpass

username=input("Username: ")
password=getpass.getpass("Password: ")
salt="qd>BqùoJDBNùLJQDNBùeqnvgùqV%QBDv%JQLNBqBVmkqjdbvkljQD,N"+username+"AOZDBObÙOUojbnegozgboQegbIgojHqouehNObNiuJNgouinboBOQBGpioBGouNbO<NojbnoujbGUOjivbOULNV"
salt=hashlib.sha256(bytes(salt,"UTF-8")).hexdigest()
password=hashlib.pbkdf2_hmac('sha256',bytes(password,"UTF-8"),bytes(salt,"UTF-8"),100000) #type:ignore
password=str(binascii.hexlify(password),"UTF-8") #type:ignore
print(password)
