import requests


from srai_gpt_function.function.gpt_function import GptFunction


class GetMyIp(GptFunction):
    """Create a function"""

    def __init__(self):
        super().__init__("get_my_ip")

    def get_descriptor(self) -> dict:
        return {
            "name": "get_my_ip",
            "description": "Retrieves the public IP address of the current machine.\n\n",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }

    def run() -> str:
        """
        Retrieves the public IP address of the current machine.

        Returns:
            str: The public IP address of the machine.
        """
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json()["ip"]
        return ip
