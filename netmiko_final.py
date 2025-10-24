import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

from netmiko import ConnectHandler
from pprint import pprint
import paramiko
import re

paramiko.transport.Transport._preferred_kex = (
    'diffie-hellman-group14-sha1',
    'diffie-hellman-group-exchange-sha1',
)
paramiko.transport.Transport._preferred_keys = (
    'ssh-rsa',
)

username = "admin"
password = "cisco"


def gigabit_status(ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": username,
        "password": password, 
        "conn_timeout": 20,
    }

    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        interface_list = []
        result = ssh.send_command("show ip interface brief", use_textfsm=True)
        pprint(result)
        for status in result:
            if "GigabitEthernet" in status["interface"]:
                intf = status["interface"]
                if status["proto"] == "up":
                    up += 1
                    interface_list.append(f"{intf} up")
                elif status["status"] == "administratively down":
                    admin_down += 1
                    interface_list.append(f"{intf} administratively down")
                elif status["proto"] == "down":
                    down += 1
                    interface_list.append(f"{intf} down")
                
        interface_summary = ", ".join(interface_list)
        summary = f"-> {up} up, {down} down, {admin_down} administratively down"
        ans = f"{interface_summary}\n{summary}"
        pprint(ans)
        return ans

def motd_reader(ip, student_id="66070118"):
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": "admin",
        "password": "cisco",
        "conn_timeout": 20,
    }

    try:
        with ConnectHandler(**device_params) as ssh:
            output = ssh.send_command("show running-config")
            match = re.search(r"banner motd (\^C|\S)(.*?)\1", output, re.DOTALL)
            if not match:
                return "Error: No MOTD Configured"

            motd_text = match.group(2).strip()

            if student_id in motd_text:
                return motd_text
            else:
                return "Error: No MOTD Configured"
    except Exception as e:
        return f"Error: {str(e)}"
