import json
import os

import pandas as pd

from scripts import config_utils


def read_data(conv_file_path, results_path):
    conv_df = pd.read_csv(conv_file_path)
    with open(results_path) as f:
        results_data = json.loads(f.read())
    return conv_df, results_data

def check_team_proposal_statement(content: str):
    return "The proposed team is -" in content

def get_team(content):
    content_lines = content.split('\n')
    for line in content_lines:
        if 'The proposed team is -' in line:
            line = line.replace('The proposed team is -', '').strip().replace('.', '')
            players = [player.strip() for player in line.split(',')]
            return ','.join(players).lower()
    print(content)

def get_team_reconsideration_results(conv_file_path, results_file_path):
    conv_df, results_data = read_data(conv_file_path, results_file_path)

    conv_df['content'] = conv_df['content'].astype(str)

    mask = conv_df['content'].apply(lambda x: check_team_proposal_statement(x))
    conv_df = conv_df[mask]
    conv_df['team'] = conv_df['content'].apply(lambda x: get_team(x))
    conv_df_min = conv_df[['agent_name', 'msg_type','name','round','index','is_secondary_round', 'team']].copy()
    
    player_to_char = dict((val,key) for key, val in results_data['character_to_player'].items())
    conv_df_min['role'] = conv_df_min['name'].apply(lambda name: player_to_char[name])

    evil_roles = ['Assassin', 'Morgana']
    conv_df_min['side'] = conv_df_min['role'].apply(lambda role: 'evil' if role in evil_roles else 'loyal')

    discussion_df = conv_df_min[conv_df_min['msg_type'] == 'discussion'][['name', 'round', 'side', 'is_secondary_round', 'team']]
    reconsider_df = conv_df_min[conv_df_min['msg_type'] == 'reconsider_team'][['name', 'round', 'is_secondary_round', 'side', 'team']]

    discussion_dict = {}
    for idx, row in discussion_df.iterrows():
        key = (row['name'], row['round'], row['is_secondary_round'])
        discussion_dict[key] = row['team']

    evil_change_count, loyal_change_count = 0, 0
    evil_total_count, loyal_total_count = 0, 0
    for idx, row in reconsider_df.iterrows():
        key = (row['name'], row['round'], row['is_secondary_round'])
        first_team = discussion_dict[key]
        reconsider_team = row['team']
        if first_team != reconsider_team:
            if row['side'] == 'evil':
                evil_change_count += 1
            else:
                loyal_change_count += 1

        if row['side'] == 'evil':
            evil_total_count += 1
        else:
            loyal_total_count += 1

    return evil_change_count, loyal_change_count, evil_total_count, loyal_total_count


    # print(conv_df_min.head())
    # print(len(conv_df[~conv_df['team'].str.startswith('player')]))

if __name__ == '__main__':
    gameplay_files = {}
    conv_files = {}

    ANNOTATED_RESULTS_PATH = config_utils.get_config_value("annotated_data_save_path")

    for d in os.listdir(ANNOTATED_RESULTS_PATH):
        if d.startswith('game_'):
            gameplay_folder = f"{ANNOTATED_RESULTS_PATH}/{d}"
            key = d.split('_')[-1]
            for x in os.listdir(gameplay_folder):
                if x.startswith('game_play_data'):
                    gameplay_files[key] = f"{gameplay_folder}/{x}"
                elif x.startswith('conv-processed') and x.endswith('.csv'):
                    conv_files[key] = f"{gameplay_folder}/{x}"
                # for gpt 3.5
                # elif x.startswith('annotation-') and x.endswith('.csv'):
                #     evaluation_files[key] = f"{gameplay_folder}/{x}"
    
    print(len(gameplay_files), len(conv_files))

    print("Processing files...")

    agg_evil_change_count, agg_loyal_change_count = 0, 0
    agg_evil_total_count, agg_loyal_total_count = 0, 0

    for key in conv_files.keys():
        # print(f"Processed: {key}")
        evil_change_count, loyal_change_count, evil_total_count, loyal_total_count = get_team_reconsideration_results(conv_files[key], gameplay_files[key])
        agg_evil_change_count += evil_change_count
        agg_evil_total_count += evil_total_count
        agg_loyal_change_count += loyal_change_count
        agg_loyal_total_count += loyal_total_count

    print(agg_evil_change_count, agg_evil_total_count)
    print(agg_loyal_change_count, agg_loyal_total_count)

    print(f"Evil: {agg_evil_change_count/agg_evil_total_count:.4f} \nLoyal:  {agg_loyal_change_count/agg_loyal_total_count:.4f}")