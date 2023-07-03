import openai
import json


class FunctionClient:
    def __init__(self):
        self.message_list = []
        self.function_dict = {}
        self.function_descriptor_list = []

    def reset(self):
        self.message_list = []
        self.function_dict = {}
        self.function_descriptor_list = []

    def register_function(
        self, function_name: str, function, function_descriptor: dict
    ):
        self.function_dict[function_name] = function
        self.function_descriptor_list.append(function_descriptor)

    def call_chain(self, prompt: str):
        self.message_list.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        response = self.call()

        return response

    def call(self) -> openai.ChatCompletion:
        print("message_list: ", self.message_list)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.message_list,
            functions=self.function_descriptor_list,
            function_call="auto",  # auto is default, but we'll be explicit
        )  # get a new response from GPT where it can see the function response
        response_message = response["choices"][0]["message"]
        self.message_list.append(response_message)
        return response

    def call_function(self, response_message: dict):
        function_name = response_message["function_call"]["name"]
        function_to_call = self.function_dict[function_name]
        print(response_message["function_call"]["arguments"])

        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            code=function_args.get("code"),  # TODO
        )

        # Step 4: send the info on the function call and function response to GPT
        self.message_list.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        response = self.call()
