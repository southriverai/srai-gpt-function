# import
from srai_gpt_function.function.gpt_function import GptFunction


class FunctionNameCapital(GptFunction):
    """Create a function"""

    def __init__(self):
        super().__init__("function_name_lower")

    def get_descriptor(self) -> dict:
        return {"description": "description"}
