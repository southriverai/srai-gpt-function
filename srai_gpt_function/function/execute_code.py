from srai_gpt_function.function.gpt_function import GptFunction


class ExecuteCode(GptFunction):
    def __init__(self):
        super().__init__("execute_code")

    def get_descriptor(self) -> dict:
        return {
            "name": "execute_code",
            "description": "Runs the given python code on my platform",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The python code that should be executed",
                    },
                },
                "required": ["code"],
            },
        }

    def run(self, code: str) -> str:
        """Get the current weather in a given location"""

        # sanitize code
        code = code.replace("\n", "\\n")
        code = code.replace('"', '\\"')
        code = code.replace("'", "\\'")
        code = code.replace("\\\\n", "\n")
        code = code.replace("\\n", "\n")
        code = code.replace("\\", "")

        with open("temp.py", "w") as file:
            file.write(code)

        print("code_start")
        lines = code.split("\n")
        for line in lines:
            print(line)
        print("code_end: ")
        exec(code)

        return "completed"
