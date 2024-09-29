import pandas as pd
import os


import config_utils
from ast import literal_eval


def set_secondary_round(idx, secondary_round_index_ranges):
    for start, end in secondary_round_index_ranges:
        if start <= idx <= end:
            return True
    return False

def set_team_proposal_change_message_type(idx, conversation_df):
    found = False
    idx_discussion = idx
    while conversation_df.iloc[idx_discussion]['msg_type'] != 'discussion':
        idx_discussion += 1
    conversation_df.at[idx_discussion, 'msg_type'] = 'reconsider_team'

def check_is_start_of_player_discussion(content: str):
    if "respond with your views on the team proposal" in content:
        return True
    if "Now the leader choose your teammates" in content:
        return True
    if "This is round" in content:
        return True
    return False

def filter_out_non_impactful_intents(intents, all=False):
    final_intents = []
    non_impactful_present = False
    for intent in intents:
        final_intents.append(intent)
        # elif all: non_impactful_present = True
    if all and non_impactful_present:
        return []
    return final_intents


def process_player_discussion(start_idx, end_idx, df):
    # print(conversation_df.iloc[start_idx: end_idx+1]['msg_type'])
    intent_count = 0
    cur_idx = start_idx
    msg_type = ''
    while cur_idx <= end_idx:
        msg_type = df.iloc[cur_idx]['msg_type']
        if msg_type == 'intent':
            intent_count += 1
            if intent_count == 2:
                break
        cur_idx += 1

    if msg_type != 'intent':
        return
    orig_intent_idx = cur_idx
    orig_selected_intents = literal_eval(df.iloc[orig_intent_idx]['content'])
    # print(f"{orig_selected_intents=}")

    intent_mod_prompt_idx = -1
    intent_count = 0
    while cur_idx <= end_idx:
        msg_type = df.iloc[cur_idx]['msg_type']
        if msg_type == 'intent_modification':
            intent_mod_prompt_idx = cur_idx
        if msg_type == 'intent' and intent_mod_prompt_idx != -1:
            break
        cur_idx += 1
    
    if msg_type != 'intent':
        return
    mod_intent_idx = cur_idx
    modified_intents = literal_eval(df.iloc[mod_intent_idx]['content'])
    # print(f"{modified_intents=}")

    total_intent_count = len(orig_selected_intents) + len(modified_intents)

    retained_orig_intents = filter_out_non_impactful_intents(orig_selected_intents)
    retained_mod_intents = filter_out_non_impactful_intents(modified_intents)

    annotation_data = {
        "round": df.loc[orig_intent_idx]['round'],
        "is_secondary_round": df.loc[orig_intent_idx]['is_secondary_round'],
        "player": df.loc[orig_intent_idx]['name'],
        "updated_orig_intents": (orig_intent_idx, retained_orig_intents),
        "updated_mod_intents": (mod_intent_idx, retained_mod_intents),
        "was_intent_modified": len(modified_intents) > 0
    }

    retained_annotation_data = {}
    if len(retained_orig_intents) > 0 or len(retained_mod_intents) > 0:
        retained_annotation_data = annotation_data

    # print(f"{retained_orig_intents=}\n{retained_mod_intents=}")

    # print(intent_mod_prompt_idx)

    to_drop_indices = []

    if len(retained_orig_intents) == 0 and len(retained_mod_intents) == 0:
        to_drop_indices.extend(df.index[start_idx + 1: end_idx].tolist())
        # df.drop(index=df.index[start_idx + 1: end_idx], inplace=True)
    elif len(retained_orig_intents) == 0:
        to_drop_indices.extend(df.index[start_idx + 1: intent_mod_prompt_idx].tolist())
        # df.drop(index=df.index[start_idx + 1: intent_mod_prompt_idx], inplace=True)
    elif len(modified_intents) != 0 and len(retained_mod_intents) == 0:
        to_drop_indices.extend(df.index[intent_mod_prompt_idx: end_idx].tolist())
        # df.drop(index=df.index[intent_mod_prompt_idx: end_idx], inplace=True)

    # print(df.loc[start_idx: end_idx]['msg_type'])
    return annotation_data, to_drop_indices, retained_annotation_data, total_intent_count

def get_row_data(ann, columns):
    row_data = {col:None for col in columns}
    row_data["player"] = ann["player"]
    row_data["round"] = ann["round"]
    row_data["is_secondary_round"] = ann["is_secondary_round"]
    row_data["intent"] = ann["updated_orig_intents"][1]
    if ann["was_intent_modified"]:
        row_data["intent_mod"] = ann["updated_mod_intents"][1]
    else:
        row_data["intent_mod"] = ann["updated_orig_intents"][1]

    return row_data

def process_conversation(game_folder):
    timestamp = game_folder.split("_")[-1]

    conversation_df = pd.read_csv(f'{game_folder}/conversation.csv')


    conversation_df['content'] = conversation_df['content'].astype(str)
    conversation_df['name'] = conversation_df['agent_name'].apply(lambda x: x.split('(')[0])
    conversation_df['round'] = conversation_df['turn']

    secondary_round_start_indices = conversation_df[conversation_df['content'].str.startswith("Now the leader of this round is")].index.tolist()

    next_round_start_indices = conversation_df[conversation_df['content'].str.startswith("This is round")].index[1:].tolist()
    # appending end of game index
    next_round_start_indices.append(len(conversation_df) - 1)


    secondary_round_index_ranges = []
    next_round_pointer = 0
    for idx in secondary_round_start_indices:
        next_round_idx = next_round_start_indices[next_round_pointer]
        while next_round_idx < idx and next_round_pointer < len(next_round_start_indices) - 1:
            next_round_pointer += 1
            next_round_idx = next_round_start_indices[next_round_pointer]
        
        secondary_round_index_ranges.append((idx, next_round_idx - 1))

    # print(f"Number of secondary rounds = {len(secondary_round_index_ranges)})")

    conversation_df['index'] = conversation_df.index
    conversation_df['is_secondary_round'] = conversation_df['index'].apply(lambda idx: set_secondary_round(idx, secondary_round_index_ranges))

    team_proposal_mod_prompt_indices = conversation_df[conversation_df['content'].str.contains("do you want to change your team proposal?")].index.tolist()
    for idx in team_proposal_mod_prompt_indices:
        set_team_proposal_change_message_type(idx, conversation_df)

    conversation_df.to_csv(f'{game_folder}/conv-processed-{timestamp}.csv', index=False)


if __name__ == '__main__':

    GAMEPLAY_FOLDERS_PATH = config_utils.get_config_value("annotated_data_save_path")

    # selected_games = {'game_2024-03-14-16-27-7': True, 'game_2024-03-14-15-31-20': True, 'game_2024-03-14-2-18-30': True, 'game_2024-03-13-19-22-32': True, 'game_2024-03-13-23-54-39': True, 'game_2024-03-13-13-45-50': True, 'game_2024-03-14-13-17-36': True, 'game_2024-03-14-0-32-40': True, 'game_2024-03-13-23-28-4': True, 'game_2024-03-14-13-25-43': True, '.DS_Store': True, 'game_2024-03-09-20-6-42': True, 'game_2024-03-13-20-19-44': True, 'game_2024-03-14-14-1-13': True, 'game_2024-03-13-14-44-2': True, 'game_2024-03-21-1-31-27': True, 'game_2024-03-14-13-35-33': True, 'game_2024-03-14-15-14-35': True, 'game_2024-03-09-19-22-33': True, 'game_2024-03-13-21-20-40': True, 'game_2024-03-09-19-32-51': True, 'game_2024-03-14-2-33-55': True, 'game_2024-03-13-16-6-5': True, 'game_2024-03-14-2-18-25': True, 'game_2024-03-09-20-26-59': True, 'game_2024-03-13-21-32-32': True, 'game_2024-03-14-15-53-56': True, 'game_2024-03-14-14-46-42': True, 'game_2024-03-14-15-25-12': True, 'game_2024-03-14-14-46-43': True, 'game_2024-03-14-1-1-56': True, 'game_2024-03-09-19-50-34': True, 'game_2024-03-14-15-8-30': True, 'game_2024-03-09-19-1-13': True, 'game_2024-03-14-14-54-54': True, 'game_2024-03-13-23-28-6': True, 'game_2024-03-13-19-33-25': True, 'game_2024-03-13-15-49-42': True, 'game_2024-03-14-1-2-3': True, 'game_2024-03-14-2-43-59': True, 'game_2024-03-14-13-7-1': True, 'game_2024-03-13-16-22-17': True, 'game_2024-03-14-14-1-11': True, 'game_2024-03-13-23-54-42': True, 'game_2024-03-09-20-4-44': True, 'game_2024-03-09-14-44-25': True}

    for x in os.listdir(GAMEPLAY_FOLDERS_PATH):
        if x.startswith('game_'):
            gameplay_folder = f"{GAMEPLAY_FOLDERS_PATH}/{x}"
            print(x)
            process_conversation(gameplay_folder)

    print("\nProcessing complete!!")




