import jsonschema
import json
import sys
import datetime
import os

def validate(message, schema_version = "2021-05-27"):
    with open("{}/etc/message-{}.schema.json".format(os.path.dirname(os.path.realpath(__file__)), schema_version)) as fp:
        reference = json.load(fp)

        try:
            ret = jsonschema.validate(instance=message, schema=reference)
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(e)
            return False

def validate_file(message_file, schema_version = "2021-05-27"):
    if message_file == '-':
        return validate(json.load(sys.stdin), schema_version)

    with open(message_file) as fp:
        return validate(json.load(fp), schema_version)

if __name__ == "__main__":
    if validate_file(sys.argv[1]):
        print("Success!")
