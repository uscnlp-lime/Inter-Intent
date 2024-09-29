import json
import logging
import ast
import re

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def parse_json_response(response, schema=None):
    try:
        match = re.search(r'{[^{}]*}', response)
        if match:
            extracted_json_object = match.group()
            parsed_response = ast.literal_eval(extracted_json_object)
            return parsed_response
        else:
            raise RuntimeError

    except Exception:
        if schema:
            parsed_response = parse_invalid_json(response, schema)
            return parsed_response
        raise NotImplementedError


def parse_invalid_json(json_string, schema):
    pattern = re.compile(r'"([^"]+)"\s*:\s*({[^{}]*}|"([^"]+)"|"([^"]+)$),?')
    matches = pattern.findall(json_string)

    keys = schema.keys()
    parsed_response = {}
    if matches:
        for match in matches:
            key = match[0]
            if key in keys:
                value = match[2] if match[3] == '' else match[3]
                parsed_response[key] = value
    if len(keys) > len(parsed_response):
        print(f"Parsed response - {parsed_response}")
        print(f"Error in parsing - {json_string}")

    return parsed_response


def remove_non_alphabets(input_string):
    # Use regular expression to remove non-alphabetic characters
    return re.sub(r'[^a-zA-Z\s]', '', input_string).lower()


def calculate_f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0
    else:
        return 2 * (precision * recall) / (precision + recall)
