from ncclient import manager
import xmltodict

def netconf_edit_config(m, netconf_config):
    return m.edit_config(target="running", config=netconf_config)

def interface_exists(m, if_name):
    filter_xml = f"""
    <filter>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>{if_name}</name>
            </interface>
        </interfaces>
    </filter>
    """
    result = m.get(filter=filter_xml)
    data = xmltodict.parse(result.xml)

    try:
        interfaces = data.get("rpc-reply", {}).get("data", {}).get("interfaces")
        if not interfaces:
            return False

        iface = interfaces.get("interface")
        return iface is not None
    except Exception as e:
        print("interface_exists error:", e)
        return False

def create(ip):
    try: 
        with manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            if_name = "Loopback66070118"

            if interface_exists(m, if_name):
                return f"Cannot create: Interface {if_name}"
            
            netconf_config = f"""
            <config>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>Loopback66070118</name>
                        <description>Created by NETCONF</description>
                        <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                        <enabled>true</enabled>
                        <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                            <address>
                                <ip>172.1.18.1</ip>
                                <netmask>255.255.255.0</netmask>
                            </address>
                        </ipv4>
                    </interface>
                </interfaces>
            </config>
            """

            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return "Interface loopback 66070118 is created successfully using Netconf"
    except Exception as e:
        print("Error!", str(e))
        return f"Cannot create: Interface loopback 66070118"


def delete(ip):
    try: 
        with manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            if_name = "Loopback66070118"

            if not interface_exists(m, if_name):
                return f"Cannot delete: Loopback66070118"
            
            netconf_config = """
            <config>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface operation="remove">
                        <name>Loopback66070118</name>
                    </interface>
                </interfaces>
            </config>
            """

            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if "<ok/>" in xml_data:
                return f"Interface Loopback66070118 is deleted successfully using Netconf"

    except Exception as e:
        print("Error:", e)
        return f"Cannot delete: Loopback66070118"


def enable(ip):
    try: 
        with manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_config = """
            <config>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>Loopback66070118</name>
                        <enabled>true</enabled>
                    </interface>
                </interfaces>
            </config>
            """
            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if "<ok/>" in xml_data:
                return f"Interface Loopback66070118 is enabled successfully using Netconf"
            else:
                return f"Cannot shutdown: Interface loopback 66070118 (checked by Netconf)"
    except Exception as e:
        print("Error:", e)
        return f"Cannot enable: Interface loopback 66070118"



def disable(ip):
    try: 
        with manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
            netconf_config = """
            <config>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>Loopback66070118</name>
                        <enabled>false</enabled>
                    </interface>
                </interfaces>
            </config>
            """

            netconf_reply = netconf_edit_config(m, netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if "<ok/>" in xml_data:
                return f"Interface Loopback66070118 is shutdowned successfully using Netconf"
            else:
                return f"Cannot shutdown: Interface loopback 66070118 (checked by Netconf)"
    except Exception as e:
        print("Error:", e)
        return f"Cannot shutdown: Interface loopback 66070118 (checked by Netconf)"

def status(ip):
    with manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
        ) as m:
        netconf_filter = """
        <filter>
            <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>Loopback66070118</name>
                </interface>
            </interfaces-state>
        </filter>
        """
        try:
            netconf_reply = m.get(filter=netconf_filter)            
            netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

            interfaces_state = (
                netconf_reply_dict.get("rpc-reply", {})
                .get("data", {})
                .get("interfaces-state", {})
                .get("interface")
            )
            if interfaces_state:
                admin_status = interfaces_state.get("admin-status")
                oper_status = interfaces_state.get("oper-status")

                if admin_status == "up" and oper_status == "up":
                    return f"Interface loopback 66070118 is enabled (checked by Netconf)"
                elif admin_status == "down" and oper_status == "down":
                    return f"Interface loopback 66070118 is disabled (checked by Netconf)"
            else:
                return f"No Interface loopback 66070118 (checked by Netconf)"

        except Exception as e:
            print("Error!", e)
            return f"No Interface loopback 66070118 (checked by Netconf)"