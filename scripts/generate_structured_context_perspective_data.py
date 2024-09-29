import json

import config_utils
from utils import save_data
from constants import impactful_intents
from collections import defaultdict


if __name__ == "__main__":
    STRUCTURED_CONTEXT_PATH = config_utils.get_config_value("structured_context_save_path")
    SUFFIX = "_all"

    with open(f'{STRUCTURED_CONTEXT_PATH}/guessing_data/intent_guessing{SUFFIX}_impactful.json',
              'r') as f:
        intent_guessing_data = json.loads(f.read())

    with open(f'{STRUCTURED_CONTEXT_PATH}/summarization_data/intent_summarization{SUFFIX}.json',
              'r') as f:
        intent_summarization_data = json.loads(f.read())

    intent_summarization_impactful_data = []
    intent_count = 0
    for data in intent_summarization_data:
        intents = data['intents']
        filtered_intents = []
        for intent in intents:
            if intent not in impactful_intents:
                continue
            filtered_intents.append(intent)
        final_data = data.copy()
        final_data['intents'] = filtered_intents
        if len(filtered_intents) == 0:
            continue
        intent_summarization_impactful_data.append(final_data)
        intent_count += len(filtered_intents)

    intent_summarization_data = intent_summarization_impactful_data

    intent_guessing_dict = {}
    for sample in intent_guessing_data:
        data = sample
        id_ele = sample['id'].split('-')
        player = id_ele[-2]
        game_id = '-'.join(id_ele[:-2])

        data['game_id'] = game_id
        data['player'] = player
        intent_guessing_dict[sample['id']] = data

    intent_summarization_dict = {}
    for sample in intent_summarization_data:
        data = sample
        id_ele = sample['id'].split('-')
        game_id = '-'.join(id_ele[:-2])
        player = data['context'].split('\n')[0].split(': ')[-1].strip().lower()

        data['game_id'] = game_id
        data['player'] = player
        intent_summarization_dict[sample['id']] = data

    intent_sum_game_grouped = defaultdict(list)
    for key, val in intent_summarization_dict.items():
        intent_sum_game_grouped[val['game_id']].append(val)


    intent_guessing_perspective_data = []
    for key, val in intent_guessing_dict.items():
        game_id = val['game_id']
        player = val['player']
        sum_data = intent_sum_game_grouped[game_id]
        cur_idx = 0
        while sum_data[cur_idx]['player'] == player:
            cur_idx += 1

        perspective_player = sum_data[cur_idx]['player']
        perspective_player_role_details = sum_data[cur_idx]['context'][:sum_data[cur_idx]['context'].find('**Round**:')]

        intent_guess_context = val['context'][val['context'].find('**Round**:'):]

        context = perspective_player_role_details + '\n' + intent_guess_context
        persp_player_intents = sum_data[cur_idx]['intents']
        persp_player_think = sum_data[cur_idx]['think']
        persp_player_speak = sum_data[cur_idx]['speak']

        val['context'] = context
        val['persp_player_intents'] = persp_player_intents
        val['persp_player_think'] = persp_player_think
        val['persp_player_speak'] = persp_player_speak
        val['persp_player'] = perspective_player

        intent_guessing_perspective_data.append(val)

    save_data(intent_guessing_perspective_data,
              f"{STRUCTURED_CONTEXT_PATH}/guessing_data/intent_guessing{SUFFIX}_impactful_reflective.json")