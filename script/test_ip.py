import os
import sys

import importlib
from typing import List
from srai_gpt_function.function.create_function import CreateFunction
from srai_gpt_function.function_client import FunctionClient
from srai_gpt_function.function.gpt_function import GptFunction
import srai_gpt_function.function
from srai_gpt_function.rate_limiting_model import RateLimitingModel
from srai_core.jsondict_store import JsondictStore
from srai_core.file_store_disk import FileStoreDisk
import inspect


def find_list_gpt_function(module_namespaces) -> List[GptFunction]:
    return find_derived_classes(GptFunction, module_namespaces)


def find_derived_classes(base_class, path_dir_function) -> List[object]:
    function_objects = []
    for filename in os.listdir(path_dir_function):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # Remove the .py extension
            module_path = os.path.join(path_dir_function, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, base_class)
                    and obj != base_class
                ):
                    function_objects.append(obj())
    return function_objects


if __name__ == "__main__":
    client = FunctionClient(
        api_key=os.environ["OPENAI_API_KEY"],
        rate_limiting_model=RateLimitingModel(),
        call_cache=JsondictStore(FileStoreDisk("call_cache")),
        verbose=False,
    )
    # Step 1: send the conversation and available functions to GPT
    path_dir_function = os.path.abspath(
        os.path.join(os.getcwd(), "..", "srai_gpt_function", "function")
    )

    module_namespaces = [srai_gpt_function.function]
    function_object = CreateFunction()
    function_object.initialize(client, path_dir_function, "frame.py")
    client.register_function(function_object)

    list_function_object = find_list_gpt_function(path_dir_function)
    for function_object in list_function_object:
        client.register_function(function_object)

    response = client.call_chain("Use my ip to find my world ip")
    response_message_content = response["choices"][0]["message"]["content"]
    print(response_message_content)
    # Step 4 ask for the ip
    # response = client.call_chain("What is my ip?")


# if __name__ == "__main__":
#     client = FunctionClient()
#     # Step 1: send the conversation and available functions to GPT
#     path_dir_function = os.path.abspath(
#         os.path.join(os.getcwd(), "..", "srai_gpt_function", "function")
#     )s
#     client.register_function(CreateFunction(client, path_dir_function, "frame.py"))

#     response = client.call_chain(
#         "Create a function called 'get_my_ip' that finds my world ip and returns it"
#     )
#     response_message = response["choices"][0]["message"]

#     # Step 2: check if GPT wanted to call a function
#     if response_message.get("function_call"):
#         # Step 3: call the function
#         # Note: the JSON response may not always be valid; be sure to handle errors
#         response = client.call_function(response_message)

#     # Step 4 ask for the ip
#     response = client.call_chain("What is my ip?")

#     print(response)
