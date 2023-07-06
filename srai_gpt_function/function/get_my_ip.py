import requests


from srai_gpt_function.function.gpt_function import GptFunction


class GetMyIp(GptFunction):
    """Create a function"""

    def __init__(self):
        super().__init__("get_my_ip")

    def get_descriptor(self) -> dict:
        return {"name": "get_my_ip", "description": "This function uses the requests library to get the IP address of the user.\n\n", "parameters": {"type": "object", "properties": {}, "required": []}}

    def run() -> str:
        """
        This function uses the requests library to get the IP address of the user.
    
        Returns:
            str: The IP address.
        """
        response = requests.get('https://api.ipify.org')
        return response.text
