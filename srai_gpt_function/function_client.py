from typing import Optional
import openai
import json
from srai_gpt_function.function.gpt_function import GptFunction
from tenacity import retry, wait_random_exponential, stop_after_attempt
from srai_gpt_function.rate_limiting_model import RateLimitingModel
from srai_core.jsondict_store import JsondictStore


class FunctionClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        call_cache: Optional[JsondictStore] = None,
        rate_limiting_model: Optional[RateLimitingModel] = None,
        verbose: bool = False,
    ):
        self.api_key = api_key
        self.call_cache = call_cache
        self.rate_limiting_model = rate_limiting_model
        self.verbose = verbose
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
        if function.name in self.function_dict:
            return

        if self.verbose:
            print(f"registering function: {function.name}")
        self.function_dict[function.name] = function.run
        self.function_descriptor_list.append(function.descriptor)

    def call_chain(self, prompt: str):
        if self.verbose:
            print(f"Calling chain with promt: {prompt}")
        self.message_list.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        response = self.call()
        response_message = response["choices"][0]["message"]
        if response_message.get("function_call"):
            if self.verbose:
                print("Found function call")
            response = self.call_function(response_message)
        else:
            if self.verbose:
                print("No function call found")
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
        if self.rate_limiting_model is not None:
            self.rate_limiting_model.await_timer()
            self.rate_limiting_model.call()

        if self.api_key is None:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=message_list,
            )
        else:
            response = openai.ChatCompletion.create(
                api_key=self.api_key,
                model="gpt-3.5-turbo-0613",
                messages=message_list,
            )
        print("end call")
        return response["choices"][0]["message"]["content"]

    # @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def _call(self, call_dict: dict) -> openai.ChatCompletion:
        if self.call_cache is not None:
            if self.verbose:
                print("Found call cache, checking cache")
            if self.call_cache.exists(call_dict):
                if self.verbose:
                    print("Found call in cache")
                return self.call_cache.read_jsondict(call_dict)

        if self.verbose:
            print("Not found in cache, no cache present or cache ignored")
        if self.verbose:
            print("Begin call")
            print("Message_list: ", call_dict["messages"])

        if self.rate_limiting_model is not None:
            self.rate_limiting_model.await_timer()
            self.rate_limiting_model.call()
        response_dict = openai.ChatCompletion.create(**call_dict)
        if self.verbose:
            print("End call")
            print(response_dict)
        self.call_cache.write_jsondict(call_dict, response_dict)
        return response_dict

    def call(self) -> openai.ChatCompletion:
        call_dict = {}
        call_dict["model"] = "gpt-3.5-turbo-0613"
        call_dict["messages"] = self.message_list
        call_dict["functions"] = self.function_descriptor_list
        call_dict["function_call"] = "auto"  # auto is default, but we'll be explicit

        if self.api_key is not None:
            call_dict["api_key"] = self.api_key

        response_dict = self._call(call_dict)
        response_message = response_dict["choices"][0]["message"]
        self.message_list.append(response_message)
        return response_dict

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
        if self.verbose:
            print(f"Calling function {function_name}")
            print(response_message["function_call"]["arguments"])

        function_args = self.parse_arguments_to_json(
            response_message["function_call"]["arguments"]
        )
        function_response = self.function_dict[function_name](**function_args)

        self.message_list.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        if self.verbose:
            print(f"Done calling function {function_name}")
            print("alling api again")
        return self.call()
