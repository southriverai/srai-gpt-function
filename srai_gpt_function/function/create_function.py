import os
from srai_gpt_function.function.gpt_function import GptFunction
from srai_gpt_function.function_client import FunctionClient
import json
import ast


class CreateFunction(GptFunction):
    """Create a function"""

    def __init__(
        self,
        function_client: FunctionClient,
        path_dir_function: str,
        path_file_frame: str,
    ):
        super().__init__("create_function")
        self.function_client = function_client
        self.path_dir_function = path_dir_function
        self.path_file_frame = path_file_frame

    def sanitize_code(self, code: str) -> str:
        print("code: ", code)

        if "```python" in code:
            code_start = code.find("```python") + len("```python")
            code_end = code.find("```", code_start)
            code = code[code_start:code_end]

        code = code.replace("\n", "\\n")
        code = code.replace('"', '\\"')
        code = code.replace("'", "\\'")
        code = code.replace("\\\\n", "\n")
        code = code.replace("\\n", "\n")
        code = code.replace("\\", "")

        try:
            ast.parse(code)
        except SyntaxError as e:
            with open("code_error.py", "w") as file:
                file.write(code)
            raise e
        return code
        # TODO parse code to make sure it is valid python code

    def capitalized_words(self, string: str) -> str:
        return "".join(x.capitalize() for x in string.split("_"))

    def insert_code(
        self,
        fuction_name_capital: str,
        fuction_name_lower: str,
        import_code: str,
        body_code: str,
        description: str,
    ) -> str:
        code = open(self.path_file_frame, "r").read()
        code = code.replace("FunctionNameCapital", fuction_name_capital)
        code = code.replace("function_name_lower", fuction_name_lower)
        code = code.replace("# import", import_code)
        code = code.replace("pass", "# body")
        code = code.replace('{"description": "description"}', description)
        body_lines = body_code.split("\n")
        code += f"\n    def run{body_lines[0]}\n"
        for line in body_lines[1:]:
            code += "    " + line + "\n"
        return code

    def split_code(self, function_name: str, code: str) -> str:
        code_part = code.split(f"def {function_name}")
        import_code = code_part[0]
        body_code = code_part[1]
        print("import_code: ", import_code)
        return import_code, body_code

    def extract_docstring_and_type_hints(self, code: str):
        module = ast.parse(code)
        functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

        for function in functions:
            function_name = function.name
            print("function_name: ", function_name)
            description = ast.get_docstring(function)
            # if description is None:
            description = description.split("Returns")[0]

            print(f"Function Name: {function_name}")
            print(f"Docstring: {description}")

            dict_argument = {}
            for arg in function.args.args:
                argument_name = arg.arg
                argument_type = ast.unparse(arg.annotation) if arg.annotation else None
                argument = {"type": argument_type}
                dict_argument[argument_name] = argument
                print(f"Argument Name: {argument_name}, Type Hint: {argument_type}")

            dict_return = {}
            return_type = ast.unparse(function.returns) if function.returns else None
            print(f"Return Type Hint: {return_type}")
            print("-" * 20)
            return description, dict_argument, dict_return

    def create_description(self, name_function: str, code: str) -> dict:
        print("############")
        # extract the discription abd arguments from the code
        description, dict_argument, dict_return = self.extract_docstring_and_type_hints(
            code
        )

        description_dict = {
            "name": name_function,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }

        for argument_name, argument in dict_argument.items():
            description_dict["parameters"]["properties"][argument_name] = {
                "type": argument["type"],
                "description": "The python code that should consitute the function",
            }
            description_dict["parameters"]["required"].append(argument_name)

        return json.dumps(description_dict)

    def run(
        self,
        function_name: str,
        code: str,
    ) -> str:
        """Get the current weather in a given location"""

        code = self.function_client.promt_seperate(
            f"please make sure the following code has comments, descriptions and type hints```{ code}```"
        )
        print("code: ", code)
        # sanitize code
        sanitized_code = self.sanitize_code(code)

        # split code
        import_code, body_code = self.split_code(function_name, sanitized_code)

        # get description
        description = self.create_description(function_name, sanitized_code)

        # insert code
        fuction_name_capital = self.capitalized_words(function_name)
        code = self.insert_code(
            fuction_name_capital, function_name, import_code, body_code, description
        )

        path_file_function = os.path.join(self.path_dir_function, function_name + ".py")
        with open(path_file_function, "w") as file:
            file.write(code)

        print("code_start")
        lines = code.split("\n")
        for line in lines:
            print(line)
        print("code_end: ")
        exec(code)

        classes = dict(globals())
        class_obj = classes.get(fuction_name_capital, None)
        if class_obj is not None:
            self.function_client.register_function(class_obj())
        return "completed"

    def get_descriptor(self) -> dict:
        return {
            "name": "create_function",
            "description": "Given a function name and python code provided by the argument function it creates a function that can be used by openai",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "The name that the function should have.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The python code that should consitute the function",
                    },
                },
                "required": ["code"],
            },
        }
