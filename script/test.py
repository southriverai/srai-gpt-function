import openai
import json


from srai_gpt_function.function.execute_code import ExecuteCode
from srai_gpt_function.function_client import FunctionClient

# TODO use pydantic to do this

if __name__ == "__main__":
    client = FunctionClient()
    # Step 1: send the conversation and available functions to GPT
    client.register_function(
        "execute_code", ExecuteCode.execute_code, ExecuteCode.descriptor()
    )

    response = client.call_chain(
        "Please run a python program that writes 'aran is ugly' to my disk in 'help.json'"
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        response = client.call_function(response_message)

    print(response)
