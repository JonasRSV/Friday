import requests
import phue


def get_ipaddr():
    return requests.get("https://discovery.meethue.com").json()[0]["internalipaddress"]


def get_credentials():
    """This should create the credentials.json file"""
    bridge = phue.Bridge(ip=get_ipaddr(), username="friday", config_file_path="credentials.json")
    bridge.register_app()


if __name__ == "__main__":
    get_credentials()
