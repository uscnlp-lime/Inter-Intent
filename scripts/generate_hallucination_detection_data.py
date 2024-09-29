import json
import os

import config_utils
from utils import save_data


def filter_out_rows(data):
    keep = []
    for row in data:
        if 'express concerns about a player from a failed quest team and suggest to not include them in the current team' in \
                row['intents']:
            keep.append(row)

    return keep


if __name__ == "__main__":
    STRUCTURED_CONTEXT_PATH = config_utils.get_config_value("structured_context_save_path")
    SAVE_PATH = config_utils.get_config_value("hallucination_detection_save_path")
    SUFFIX = "_all"

    with open(f"{STRUCTURED_CONTEXT_PATH}/guessing_data/intent_guessing_all.json", 'r') as f:
        intent_guessing_data = json.loads(f.read())

    filtered_intent_guessing_data = filter_out_rows(intent_guessing_data)


    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    save_data(filtered_intent_guessing_data, f"{SAVE_PATH}/hallucination_detection.json")
