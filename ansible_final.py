import subprocess
import os
import tempfile
import json

def showrun(ip):
    studentID = "66070118"
    router_name = ip.replace(".", "_")
    filename = f"show_run_{studentID}_{router_name}.txt"

    inventory_content = f"""
    [routers]
    R1-Exam ansible_host={ip} ansible_user=admin ansible_password=cisco ansible_connection=network_cli ansible_network_os=cisco.ios.ios ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    """

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_inventory:
        tmp_inventory.write(inventory_content)
        tmp_inventory_path = tmp_inventory.name
        
    command = [
        "ansible-playbook",
        "-i", tmp_inventory_path,
        "backup_cisco_router_playbook.yaml"
    ]
    
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    result = subprocess.run(command, cwd=os.getcwd(), capture_output=True, text=True, env=env)
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)
    print("--------------\n")

    if result.returncode == 0:
        print("Playbook executed successfully (Return Code: 0).")
        if os.path.exists(filename):
            print(f"Backup file found: {filename}")
            return filename
    else:
        print(f"Playbook failed (Return Code: {result.returncode}).")
        return f"Error: Ansible"
def motd_set_ansible(ip, message):
    inventory_content = f"""
    [routers]
    R1-Exam ansible_host={ip} ansible_user=admin ansible_password=cisco ansible_connection=network_cli ansible_network_os=cisco.ios.ios ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    """
    extra_vars_json = json.dumps({"motd_message": message})

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_inventory:
        tmp_inventory.write(inventory_content)
        tmp_inventory_path = tmp_inventory.name

    command = [
        "ansible-playbook",
        "-i", tmp_inventory_path,
        "motd_config.yaml",
        "-e", extra_vars_json
    ]

    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    result = subprocess.run(command, cwd=os.getcwd(), capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        return "Ok: success"
    else:
        print(f"[DEBUG] Ansible return code {result.returncode} -> FAILED")
        return f"Error: Ansible failed (Return code {result.returncode})"