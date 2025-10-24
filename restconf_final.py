import json
import requests
requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.61-184
api_url = "https://10.0.15.61/restconf/data/ietf-interfaces:interfaces"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
header_restconf = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")

specific_interface_url = f"{api_url}/interface=Loopback66070118"

def create():
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
        verify=False
        )

    if(resp.status_code == 201):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070118 is created successfully"
    elif (resp.status_code == 204):
        print("STATUS CONFLICT: {}".format(resp.status_code))
        return "Cannot create: Interface loopback 66070118"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot create: Interface loopback 66070118"


def delete():
    resp = requests.delete(
        specific_interface_url, 
        auth=basicauth, 
        headers=header_restconf, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070118 is deleted successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot delete: Interface loopback 66070118"


def enable():
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
        return "Interface loopback 66070118 is enabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot enable: Interface loopback 66070118"


def disable():
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
        return "Interface loopback 66070118 is shutdowned successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Cannot shutdown: Interface loopback 66070118"


def status():
    api_url_status = f"https://10.0.15.61/restconf/data/ietf-interfaces:interfaces/interface=Loopback66070118"

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
            return "Interface loopback 66070118 is enabled"
        elif enabled_flag is False:
            return "Interface loopback 66070118 is disabled"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "No Interface loopback 66070118"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Huh? what happened?"
