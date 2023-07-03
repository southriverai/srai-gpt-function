class ExecuteCode:
    @staticmethod
    def execute_code(code: str) -> str:
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

    def descriptor() -> dict:
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
