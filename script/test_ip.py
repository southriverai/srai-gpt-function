import os
from srai_gpt_function.function.create_function import CreateFunction
from srai_gpt_function.function_client import FunctionClient
import srai_gpt_function.function
from srai_gpt_function.rate_limiting_model import RateLimitingModel
from srai_core.jsondict_store import JsondictStore
from srai_core.file_store_disk import FileStoreDisk
import inspect


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

    client.register_function_group(path_dir_function)

    response = client.call_chain("Use my ip to find my world ip")
    response_message_content = response["choices"][0]["message"]["content"]
    print(response_message_content)
