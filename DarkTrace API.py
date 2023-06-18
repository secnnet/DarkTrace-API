import hmac
import hashlib
import requests
import json
from datetime import datetime


class DarkTrace:
    def __init__(self, ip, token, private):
        """
        Initialize the DarkTrace API wrapper.

        Args:
            ip (str): The IP address of the DarkTrace system.
            token (str): The API token used for authentication.
            private (str): The private key used for generating the signature.
        """
        self.ip = ip
        self.token = token
        self.private = private.encode()
        self.baseUrl = f"https://{ip}"
        self.session = requests.Session()
        
    def api_call(self, type, parameters=None):
        """
        Make an API call to the DarkTrace system.

        Args:
            type (str): The type of API call to make.
            parameters (dict, optional): Additional parameters for the API call.

        Returns:
            dict: The JSON response from the API call.
        """
        if not isinstance(parameters, dict):
            raise ValueError("parameters parameter must be type: dict")

        paramStr = "&".join([f"{k}={v}" for k, v in parameters.items()])

        apiStr = f"/{type}?{paramStr}" if paramStr else f"/{type}"
        url = f"{self.baseUrl}{apiStr}"
        dateStr = datetime.utcnow().isoformat(timespec="seconds")
        macStr = f"{apiStr}\n{self.token}\n{dateStr}".encode()
        sigStr = hmac.new(key=self.private, digestmod=hashlib.sha1, msg=macStr).hexdigest()
        headers = {
            "DTAPI-Token": self.token,
            "DTAPI-Date": dateStr,
            "DTAPI-Signature": sigStr
        }

        try:
            response = self.session.get(url, verify=False, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred during the API call: {str(e)}")

        return response.json()
