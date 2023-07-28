import requests


from srai_gpt_function.function.gpt_function import GptFunction


class SendVoiceMessage(GptFunction):
    """Send a telegram message"""

    def __init__(self):
        self.descriptor = self.create_descriptor()
        super().__init__("send_voice_message")
        self.dict_recipient = {}
        self.api_token = ""

    def create_descriptor(self) -> dict:
        return {
            "name": "send_voice_message",
            "description": "Sends a voice message to a given number",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "The number that should receive the message",
                    },
                    "message": {
                        "type": "string",
                        "description": "The message that should be transmitted",
                    },
                },
                "required": ["number", "message"],
            },
        }

    def initialize(self, api_token: str):
        self.api_token = api_token

    def add_recipient(self, name: str, number: str) -> None:
        self.dict_recipient[number] = name
        self.descriptor["description"] += name + ": " + number + "\n"

    def get_descriptor(self) -> dict:
        return self.descriptor

    def run(
        self,
        number: str,
        message: str,
    ) -> str:
        if number not in self.dict_recipient:
            return "unknown number"
        else:
            print("Sending message")

            url = "https://api.voipfabric.io/v1/flow/trigger/message2number/invoke"

            payload = {"number": number, "message": message}
            headers = {
                "cookie": "__cflb=02DiuGF5HT1rZCUj8ZLCv2Pn42N2CJD2EwCAV23WtmNuy",
                "Cloud-Api-Token": self.api_token,
                "Content-Type": "application/json",
            }

            response = requests.request("POST", url, json=payload, headers=headers)

            print(response.text)
            """
            Sends the message to a target number in speach
            Returns:
                succes
            """
            return "completed"
