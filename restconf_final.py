import json
import requests
requests.packages.urllib3.disable_warnings()

header_restconf = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create(ip):
    api_url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces"
    specific_interface_url = f"{api_url}/interface=Loopback66070118"

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback66070118",
            "description": "Interface created by RESTCONF",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.1.18.1",  
                        "netmask": "255.255.255.0" 
                    }
                ]
            }
        }
    }

    resp = requests.put(
        specific_interface_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False,
        timeout=5
        )

    if resp.status_code == 201:
        print(f"[{ip}] STATUS OK: {resp.status_code}")
        return f"Interface loopback 66070118 is created successfully using Restconf"
    elif resp.status_code == 204:
        print(f"[{ip}] STATUS CONFLICT: {resp.status_code}")
        return f"Cannot create: Interface loopback 66070118"
    else:
        print(f"[{ip}] Error. Status Code: {resp.status_code}")
        return f"Cannot create: Interface loopback 66070118"



def delete(ip):
    api_url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces"
    specific_interface_url = f"{api_url}/interface=Loopback66070118"
    resp = requests.delete(
        specific_interface_url, 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070118 is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot delete: Interface loopback 66070118"


def enable(ip):
    api_url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces"
    specific_interface_url = f"{api_url}/interface=Loopback66070118"
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    resp = requests.patch(
        specific_interface_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070118 is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot enable: Interface loopback 66070118 (checked by Restconf)"


def disable(ip):
    api_url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces"
    specific_interface_url = f"{api_url}/interface=Loopback66070118"
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    resp = requests.patch(
        specific_interface_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070118 is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot shutdown: Interface loopback 66070118 (checked by Restconf)"


def status(ip):
    api_url_status = f"https://{ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback66070118"

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        iface = response_json.get("ietf-interfaces:interface", {})
        enabled_flag = iface.get("enabled")
        if enabled_flag is True:
            return "Interface loopback 66070118 is enabled (checked by Restconf)"
        elif enabled_flag is False:
            return "Interface loopback 66070118 is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "No Interface loopback 66070118 (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Huh? what happened? (checked by Restconf)"
