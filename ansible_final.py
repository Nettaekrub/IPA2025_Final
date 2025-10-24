import subprocess
import os

def showrun():
    studentID = "66070118"
    router_name = "R1-Exam"
    filename = f"show_run_{studentID}_{router_name}.txt"

    command = [
        "ansible-playbook",
        "-i", "inventory.ini",
        "backup_cisco_router_playbook.yaml"
    ]
    
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    result = subprocess.run(command, cwd=os.getcwd(), capture_output=True, text=True)
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