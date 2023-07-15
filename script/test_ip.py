import os


from srai_gpt_function.function.create_function import CreateFunction
from srai_gpt_function.function_client import FunctionClient
from srai_gpt_function.function.gpt_function import GptFunction

# TODO use pydantic to do this

import inspect


def find_classes_extending(super_class, module_namespaces):
    """
    Finds all classes in the specified module namespaces that extend the specified super class.

    Args:
        super_class (type): The super class to check for inheritance.
        module_namespaces (list): A list of module namespaces to search for classes.

    Returns:
        list: A list of class objects that extend the super class.
    """
    classes_extending = []
    for namespace in module_namespaces:
        for name, obj in inspect.getmembers(namespace):
            if inspect.isclass(obj):
                print(name)
                print(obj)
            if (
                inspect.isclass(obj)
                and issubclass(obj, super_class)
                and obj != super_class
            ):
                classes_extending.append(obj)
    return classes_extending


if __name__ == "__main__":
    client = FunctionClient(api_key=os.environ["OPENAI_API_KEY"], verbose=True)

    # Step 1: send the conversation and available functions to GPT
    path_dir_function = os.path.abspath(
        os.path.join(os.getcwd(), "..", "srai_gpt_function", "function")
    )

    import srai_gpt_function.function

    module_namespaces = [srai_gpt_function.function]
    client.register_function(CreateFunction(client, path_dir_function, "frame.py"))
    list = find_classes_extending(GptFunction, module_namespaces)

    for function in list:
        client.register_function(function())
    exit()

    response = client.call_chain("Use my ip ")
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        response = client.call_function(response_message)

    # Step 4 ask for the ip
    response = client.call_chain("What is my ip?")
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        response = client.call_function(response_message)
    print(response)
import os
import sys

from srai_gpt_function.function.create_function import CreateFunction
from srai_gpt_function.function.execute_code import ExecuteCode
from srai_gpt_function.function_client import FunctionClient

# TODO use pydantic to do this

if __name__ == "__main__":
    client = FunctionClient()
    # Step 1: send the conversation and available functions to GPT
    path_dir_function = os.path.abspath(
        os.path.join(os.getcwd(), "..", "srai_gpt_function", "function")
    )
    client.register_function(ExecuteCode())
    client.register_function(CreateFunction(client, path_dir_function, "frame.py"))

    response = client.call_chain(
        "Create a function called 'get_my_ip' that finds my world ip and returns it"
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        response = client.call_function(response_message)

    # Step 4 ask for the ip
    response = client.call_chain("What is my ip?")

    print(response)
