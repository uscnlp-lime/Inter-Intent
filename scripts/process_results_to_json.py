import json
import os
from ast import literal_eval
from collections import defaultdict

import numpy as np
import pandas as pd

import config_utils


def read_data(eval_file_path, results_path):
    if eval_file_path.endswith('.csv'):
        eval_df = pd.read_csv(eval_file_path)
        eval_df.dropna(how="all", inplace=True)
    else:
        eval_df = pd.read_excel(eval_file_path, converters={'intent_selection': str, 'intent_fol_think_2': str})
    with open(results_path) as f:
        results_data = json.loads(f.read())
    return eval_df, results_data


def get_failure_rate(results_data, evil_players):
    total_vote = 0
    fail_vote = 0
    for val in results_data['team_quest_result'].values():
        for p in evil_players:
            if p in val:
                if val[p] == 'failure':
                    fail_vote += 1
                total_vote += 1

    return fail_vote, total_vote


def get_quest_win_rate(quest_results):
    # Simple count of quest success and failures
    evil = 0
    loyal = 0
    for key, val in quest_results.items():
        if val is None:
            continue
        if val == 0:
            evil += 1
        else:
            loyal += 1

    return evil, loyal


def get_quest_engagement_rate(round_team_members, player_to_char):
    total = 0
    char_qe_count = defaultdict(int)
    for round, team in round_team_members.items():
        if len(team) == 0:
            continue
        total += 1
        for player in team:
            char_qe_count[player_to_char[player]] += 1
    return char_qe_count, total


def get_team_selection_accuracy(round_team_members, round_leaders, player_to_char, evil_roles, evil_players):
    total_evil = 0
    evil_correct = 0

    total_loyal = 0
    loyal_correct = 0

    incorrect_dict = {}

    for key, val in round_team_members.items():
        if len(val) == 0:
            continue
        leader = round_leaders[key]
        incorrect_dict[key] = 'none'

        if leader in evil_players:
            total_evil += 1
            found = False
            for member in val:
                member = member.strip()
                role = player_to_char[member]
                if role in evil_roles:
                    # if we find an evil player, then team is accurate for evil player and we increase counta and break
                    evil_correct += 1
                    found = True
                    break
            if not found:
                incorrect_dict[key] = 'evil'

        else:
            total_loyal += 1
            found_evil = False
            for member in val:
                member = member.strip()
                role = player_to_char[member]
                if role in evil_roles:
                    # if we fina an evil player, then team is wrong for loyal player and we set flag to true and break
                    found_evil = True
                    break
            if not found_evil:
                # according to flag we increase count of correct selection
                loyal_correct += 1
                # incorrect_dict[key] = 'loyal'
            else:
                incorrect_dict[key] = 'loyal'
                # pass

    return total_evil, total_loyal, evil_correct, loyal_correct, incorrect_dict


def find_player_side(player_name, player_to_char, evil_roles):
    if player_to_char[player_name] in evil_roles:
        return 'evil'
    return 'loyal'


def update_intent_selection_vals(intent_mod, intent_sel, intent_sel_mod):
    if intent_mod is not np.NaN:
        return intent_sel_mod
    return intent_sel


def comma_string_to_list(x):
    if x != 'NaN':
        x = x.replace('.', ',')
        return [val.strip() for val in x.split(',') if val != '']
    else:
        print('here')
        return np.NaN


def process_game(eval_file_path, results_path):
    return_vals = {}

    eval_df, results_data = read_data(eval_file_path, results_path)

    eval_df = eval_df.drop(columns=[col for col in eval_df.columns if col.startswith('Unnamed')])

    eval_df['round'] = eval_df['round'].astype(int)

    # Each quest results dictionary
    quest_results = results_data['quest_results']

    evil_roles = ['Assassin', 'Morgana']
    # dictionary with {'name': 'role'}
    player_to_char = dict((val, key) for key, val in results_data['character_to_player'].items())
    # ## Failure vote rate
    # counting the number of time an evil player votes failure from their voting chances
    evil_players = [key for key, val in player_to_char.items() if val in evil_roles]

    fail_vote, total_vote = get_failure_rate(results_data, evil_players)
    return_vals['failure_rate'] = {'fail_votes': fail_vote, 'total_votes': total_vote}

    evil_quest_wins, loyal_quest_wins = get_quest_win_rate(quest_results)
    return_vals['quest_win_rate'] = {'total': evil_quest_wins + loyal_quest_wins, 'evil': evil_quest_wins,
                                     'loyal': loyal_quest_wins}

    win_side = 'loyal'
    if evil_quest_wins > loyal_quest_wins:
        win_side = 'evil'

    # ## Detailed analysis

    # calculating detailed analysis metrics for total and round wise stats
    # separating our annotation comma separated to list of values
    eval_df['intent'] = eval_df['intent'].apply(lambda x: literal_eval(x))
    eval_df['intent_mod'] = eval_df['intent_mod'].apply(lambda x: literal_eval(x) if x is not np.nan else x)

    eval_df['intent_selection'] = eval_df['intent_selection'].astype(str).apply(comma_string_to_list)
    eval_df['intent_selection_mod'] = eval_df['intent_selection_mod'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_think_1'] = eval_df['intent_fol_think_1'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_speech_1'] = eval_df['intent_fol_speech_1'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_think_2'] = eval_df['intent_fol_think_2'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_speech_2'] = eval_df['intent_fol_speech_2'].astype(str).apply(comma_string_to_list)
    eval_df['round_quest_result'] = eval_df['round'].apply(
        lambda x: 'success' if quest_results[str(x)] == 1 else 'failure')

    # creating a column whether player is evil or loyal
    eval_df['side'] = eval_df['player'].apply(lambda x: find_player_side(x, player_to_char, evil_roles))
    eval_df['role'] = eval_df['player'].apply(lambda x: player_to_char[x])

    eval_df = eval_df.drop('comments', axis=1)

    eval_dict = eval_df.groupby(['round', 'is_secondary_round']).apply(
        lambda x: x.set_index('role').to_dict(orient='index')).to_dict()

    final_dict = {}

    for key, val in eval_dict.items():
        player_data = list(val.values())[0]
        rnd = "round" + str(player_data['round'])
        rnd_type = 'secondary' if player_data['is_secondary_round'] else 'primary'
        quest_result = player_data["round_quest_result"]

        if rnd not in final_dict:
            final_dict[rnd] = {}
        for key, player_val in val.items():
            del player_val['round']
            del player_val['round_quest_result']
            del player_val['is_secondary_round']

        final_dict[rnd][rnd_type] = {"turns": val, "quest_result": quest_result}

    final_dict['round_winning_side'] = win_side

    if "assassin" in results_data:
        final_dict["assassin_guess"] = results_data["assassin"]
    elif win_side == 'loyal':
        final_dict["assassin_guess"] = 'failure'

    final_winning_side = win_side
    if win_side == 'loyal' and final_dict["assassin_guess"] == 'success':
        final_winning_side = 'evil'

    final_dict['winning_side'] = final_winning_side

    return final_dict


def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    gameplay_files = {}
    evaluation_files = {}

    ANNOTATED_RESULTS_PATH = config_utils.get_config_value("annotated_data_save_path")

    for d in os.listdir(ANNOTATED_RESULTS_PATH):
        if d.startswith('game_'):
            gameplay_folder = f"{ANNOTATED_RESULTS_PATH}/{d}"
            key = d.split('_')[-1]
            for x in os.listdir(gameplay_folder):
                if x.startswith('game_play_data'):
                    gameplay_files[key] = f"{gameplay_folder}/{x}"
                elif x.startswith('evaluation_') and x.endswith('.csv'):
                    evaluation_files[key] = f"{gameplay_folder}/{x}"
                # for gpt 3.5
                # elif x.startswith('annotation-') and x.endswith('.csv'):
                #     evaluation_files[key] = f"{gameplay_folder}/{x}"

    print(len(gameplay_files), len(evaluation_files))

    print("Processing files...")

    # arihant_games = ['2024-03-13-16-22-17', '2024-03-13-23-54-42', '2024-03-14-1-2-3', '2024-03-14-2-43-59', '2024-03-14-13-7-1', '2024-03-14-14-1-11']

    all_files_data = {}
    for key in evaluation_files.keys():
        # if key in arihant_games:
        game_data = process_game(evaluation_files[key], gameplay_files[key])
        print(f"Processed: {key}")
        all_files_data[key] = game_data

    save_data(all_files_data, f'{ANNOTATED_RESULTS_PATH}/annotated_game_files_data.json')
