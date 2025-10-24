#######################################################################################
# Yourname:
# Your student ID:
# Your GitHub Repo:

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

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


#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

last_message_id = None

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.

    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        continue

    # store the array of messages
    messages = json_data["items"]
    # store the ID of the first message
    message_id = messages[0]["id"]
    # store the text of the first message in the array
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

                    # ส่งไฟล์ถ้ามี
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

