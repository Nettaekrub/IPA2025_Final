import os
import time
import json

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

import restconf_final
import netconf_final
import netmiko_final
import ansible_final

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

last_message_id = None

while True:
    time.sleep(1)
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    json_data = r.json()

    if len(json_data["items"]) == 0:
        continue

    messages = json_data["items"]
    message_id = messages[0]["id"]
    message = messages[0]["text"]
    print("Received message: " + message)

    if message_id == last_message_id:
        continue
    else:
        last_message_id = message_id

    command_or_method = None

    if message.startswith("/66070118"):
        parts = message.split(" ")
        responseMessage = None

        if len(parts) < 2:
            responseMessage = "Error: No method specified"
        else:
            command_or_method = parts[1].lower()
            selected_method = globals().get("selected_method", None)

            if command_or_method in ["restconf", "netconf"]:
                selected_method = command_or_method
                globals()["selected_method"] = selected_method
                responseMessage = f"Ok: {selected_method.capitalize()}"

            elif len(parts) >= 3:
                ip = parts[1]
                command = parts[2].lower()

                if command == "motd":
                    if len(parts) > 3:
                        message_text = " ".join(parts[3:])
                        responseMessage = ansible_final.motd_set_ansible(ip, message_text)
                    else:
                        responseMessage = netmiko_final.motd_reader(ip)

                elif command == "showrun":
                    result = ansible_final.showrun(ip)
                    if os.path.isfile(result):
                        responseMessage = "Show running-config"
                        filename = result
                    else:
                        responseMessage = result
                        filename = None

                    if filename and os.path.exists(filename):
                        with open(filename, "rb") as fileobject:
                            postData = MultipartEncoder({
                                "roomId": roomIdToGetMessages,
                                "files": (os.path.basename(filename), fileobject, "text/plain"),
                            })
                            HTTPHeaders = {
                                "Authorization": f"Bearer {ACCESS_TOKEN}",
                                "Content-Type": postData.content_type
                            }
                            r = requests.post(
                                "https://webexapis.com/v1/messages",
                                data=postData,
                                headers=HTTPHeaders,
                            )
                            if r.status_code == 200:
                                print("File sent successfully")
                            else:
                                print(f"File send failed, status code {r.status_code}")

                elif command == "gigabit_status":
                    responseMessage = netmiko_final.gigabit_status(ip)

                else:
                    if selected_method is None:
                        responseMessage = "Error: No method specified"
                    else:
                        if command == "create":
                            responseMessage = restconf_final.create(ip) if selected_method == "restconf" else netconf_final.create(ip)
                        elif command == "delete":
                            responseMessage = restconf_final.delete(ip) if selected_method == "restconf" else netconf_final.delete(ip)
                        elif command == "enable":
                            responseMessage = restconf_final.enable(ip) if selected_method == "restconf" else netconf_final.enable(ip)
                        elif command == "disable":
                            responseMessage = restconf_final.disable(ip) if selected_method == "restconf" else netconf_final.disable(ip)
                        elif command == "status":
                            responseMessage = restconf_final.status(ip) if selected_method == "restconf" else netconf_final.status(ip)
                        else:
                            responseMessage = "Error: Unknown command"

            elif len(parts) == 2 and "." in parts[1]:
                responseMessage = "Error: No command found."
            elif len(parts) == 2:
                responseMessage = "Error: No method specified"
            else:
                print(len(parts))
                responseMessage = "Error: Invalid command format"

        
        postData = json.dumps({
            "roomId": roomIdToGetMessages,
            "text": responseMessage
        })
        HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )

        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )

