import requests


from srai_gpt_function.function.gpt_function import GptFunction


class GetMyIp(GptFunction):
    """Create a function"""

    def __init__(self):
        super().__init__("get_my_ip")

    def get_descriptor(self) -> dict:
        return {
            "name": "get_my_ip",
            "description": "This function retrieves the current IP address of the user.\n\n",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }

    def get_my_ip() -> str:
        """
        This function retrieves the current IP address of the user.

        Returns:
            str: The current IP address.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the API request.
        """
        try:
            response = requests.get("https://api.ipify.org")
            ip = response.text
            return ip
        except requests.exceptions.RequestException as e:
            return str(e)
