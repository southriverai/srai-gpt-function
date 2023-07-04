import os


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
