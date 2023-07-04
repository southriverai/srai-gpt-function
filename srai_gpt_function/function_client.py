import openai
import json
from srai_gpt_function.function.gpt_function import GptFunction
from tenacity import retry, wait_random_exponential, stop_after_attempt


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
        self,
        function: GptFunction,
    ):
        self.function_dict[function.name] = function.run
        self.function_descriptor_list.append(function.descriptor)

    def call_chain(self, prompt: str):
        self.message_list.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        response = self.call()

        return response

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def promt_seperate(self, prompt: str) -> openai.ChatCompletion:
        print("begin call")
        message_list = [
            {
                "role": "user",
                "content": prompt,
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=message_list,  # auto is default, but we'll be explicit
        )  # get a new response from GPT where it can see the function response
        print("end call")
        return response["choices"][0]["message"]["content"]

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def call(self) -> openai.ChatCompletion:
        print("begin call")
        print("message_list: ", self.message_list)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.message_list,
            functions=self.function_descriptor_list,
            function_call="auto",  # auto is default, but we'll be explicit
        )  # get a new response from GPT where it can see the function response
        response_message = response["choices"][0]["message"]
        self.message_list.append(response_message)
        print("end call")
        return response

    def parse_arguments_to_json(self, json_string: str) -> str:
        with open("arguments.json", "w") as file:
            file.write(json_string)
        json_string = json_string.replace("\n", "\\n")
        json_string = json_string.replace("{\\n", "{")
        json_string = json_string.replace("\\n}", "}")
        json_string = json_string.replace(",\\n", ",")
        try:
            return json.loads(json_string)
        except Exception as e:
            with open("json_error.json", "w") as file:
                file.write(json_string)
            raise e

    def call_function(self, response_message: dict):
        function_name = response_message["function_call"]["name"]
        print(response_message["function_call"]["arguments"])

        function_args = self.parse_arguments_to_json(
            response_message["function_call"]["arguments"]
        )
        function_response = self.function_dict[function_name](**function_args)

        # Step 4: send the info on the function call and function response to GPT
        self.message_list.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        response = self.call()
