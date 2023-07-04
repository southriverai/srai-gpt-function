import json

with open("argumetents.json", "r") as file:
    json_string = file.read()
print(json_string)
# remove line breask
json_string = json_string.replace("\n", "\\n")
json_string = json_string.replace("{\\n", "{")
json_string = json_string.replace("\\n}", "}")
json_string = json_string.replace(",\\n", ",")
with open("argumetents2.json", "w") as file:
    file.write(json_string)
print(json_string)
json.loads(json_string)
