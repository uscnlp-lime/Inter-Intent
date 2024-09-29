
import pandas as pd
import numpy as np
import json
import os
import re

from collections import Counter, defaultdict
from collections.abc import MutableMapping
from ast import literal_eval

import config_utils

# Update the file paths here.
EVAL_FILE_PATH = './evaluation_2024-03-06-16-21-42.csv'
GAMEPLAY_RESULTS_PATH = './game_play_data_2024-03-06-16-21-42.json'

similar_intent_map = {
    "express concerns about a player from a failed quest team and suggest to not include them in current team": "express concerns about a player from a failed quest team and suggest to not include them in the current team",
    "express concerns about a player from a failed quest team and suggest not including them in the current team": "express concerns about a player from a failed quest team and suggest to not include them in the current team",
    "express disagreement and vote disagree if not in the proposed team": "express disagreement and vote disagree only if you are not in the proposed team",
    "question a player on why they changed their statements": "question a player about why they changed their statements",
    "question player about their sudden change in stance": "question a player about why they changed their statements",
    "question a player on why he didnt vote for the last team": "question a player on why they didnt vote for the last team",
    "question why a player didnt vote for the last team": "question a player on why they didnt vote for the last team",
    "question the leader why they didnt put themselves on the quest team": "question player why they didnt include themselves in the proposed team",
    "question the leader why they selected player for the team": "question the leader why they selected a particular player for the team",
    "express concerns about an evil player": "share concerns about an evil player",
    "strongly convince the team leader to choose you on the team": "strongly convince the team leader to choose you on team",
}

impactful_intents1 = {}

impactful_intents = {
    'cast suspicion on innocent players': True, 
    'counter the team proposal because you think a player on the team is evil': True, 
    'express concerns about a player from a failed quest team and suggest to not include them in the current team': True, 
    'express confusion for failure of mission': True, 
    'express disagreement and vote disagree only if you are not in the proposed team': True, 
    'express you are a loyal player': True, 
    'pretend to be merlin by providing hints on who is evil': True, 
    'question a player about why they changed their statements': True, 
    'question a player on why they didnt vote for the last team': True, 
    'question the leader why they selected a particular player for the team': True, 
    'reveal identity by telling others you are servant to persuade other loyal players': True, 
    'share concerns about an evil player': True, 
    'strongly convince the team leader to choose you on team': True, 
    'support loyal players of the previous quest team if the mission failed': True, 
    'support your teammate by expressing that he is good': True
}

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

def get_final_intent(intent_mod, intent):
    if intent_mod is not np.NaN:
        return intent_mod
    return intent

def remove_non_alphabets(input_string):
    # Use regular expression to remove non-alphabetic characters
    return re.sub(r'[^a-zA-Z\s]', '', input_string).lower()

def get_intent_level_metrics(eval_df):
    # for grouping by intent
    eval_df_no_int_mod = eval_df[~eval_df['intent_mod'].notnull()][['player', 'side', 'round', 'intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1', 'round_quest_result']].copy()
    
    eval_df_only_int_mod = eval_df[eval_df['intent_mod'].notnull()][['player', 'side', 'round', 'intent_mod', 'intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2', 'round_quest_result']].copy()
    eval_df_only_int_mod.columns = ['player', 'side', 'round', 'intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1', 'round_quest_result']
    
    eval_df_int = pd.concat([eval_df_no_int_mod, eval_df_only_int_mod], axis=0)

    # eval_df_int['intent'] = eval_df_int['intent'].apply(lambda x: literal_eval(x))
    eval_df_int_denorm = eval_df_int.explode(['intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1'])
    eval_df_int_denorm['intent'] = eval_df_int_denorm['intent'].apply(lambda x: remove_non_alphabets(x))

    eval_df_int_denorm['intent_fol_speech_1'] = eval_df_int_denorm['intent_fol_speech_1'].astype(int)
    eval_df_int_denorm['intent_fol_think_1'] = eval_df_int_denorm['intent_fol_think_1'].astype(int)

    eval_df_int_denorm = eval_df_int_denorm[eval_df_int_denorm['intent_fol_speech_1'] >= 3]
    eval_df_int_denorm = eval_df_int_denorm[eval_df_int_denorm['intent_fol_think_1'] >= 3]
    
    count_metrics = eval_df_int_denorm.groupby(['intent', 'side', 'round_quest_result']).size().reset_index(name='count')
    
    intent_level_metrics = {}
    def aggregate_side_wise_results(row):
        side = row['side']
        intent = row['intent']
        quest_result = row['round_quest_result']
        count = row['count']
        if intent not in intent_level_metrics:
            intent_level_metrics[intent] = {side: {quest_result: count}}
        elif side not in intent_level_metrics[intent]:
            intent_level_metrics[intent][side] = {quest_result: count}
        elif quest_result not in intent_level_metrics[intent][side]:
            intent_level_metrics[intent][side][quest_result] = count
        else:
            intent_level_metrics[intent][side][quest_result] += count
    
    count_metrics.apply(lambda row: aggregate_side_wise_results(row), axis=1)
    return intent_level_metrics

def drop_rows_non_matching_columns_count(col1, col2, col3):
    if len(col1) == len(col2) and len(col2) == len(col3):
        if col1[0] != 'nan' and col2[0] != 'nan' and col3[0] != 'nan':
            return True
    return False

def separate_frm_ref_contemplation(eval_df):
    # separating formulation contemplation and refinement contemplation to handle intent modificaiton, Will combine later
    eval_df_form_cnt = eval_df[['player', 'side', 'round', 'intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1', 'round_quest_result']].copy()
    filtered_rows = eval_df_form_cnt.apply(lambda row: drop_rows_non_matching_columns_count(row['intent_selection'], row['intent_fol_think_1'], row['intent_fol_speech_1']), axis=1)
    eval_df_form_cnt = eval_df_form_cnt[filtered_rows]

    eval_df_ref_cnt = eval_df[['player', 'side', 'round', 'intent', 'intent_mod', 'intent_selection', 'intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2', 'round_quest_result']].copy()
    filtered_rows = eval_df_ref_cnt.apply(lambda row: drop_rows_non_matching_columns_count(row['intent_selection_mod'], row['intent_fol_think_2'], row['intent_fol_speech_2']), axis=1)
    eval_df_ref_cnt = eval_df_ref_cnt[filtered_rows]
    eval_df_ref_cnt = eval_df_ref_cnt.dropna(subset=["intent_selection_mod"])


    # ## Processing dfs for analysis (splitting values into separate rows)
    # #### Formulation contemplation

    # exploding would create separate rows for our annotation and help to aggregate

    # all intents
    eval_df_form_cnt_denorm = eval_df_form_cnt.explode(['intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1'])
    
    # remove non impactful intents
    # eval_df_form_cnt_denorm = eval_df_form_cnt.explode(['intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1'])
    # eval_df_form_cnt_denorm['intent'] = eval_df_form_cnt_denorm['intent'].apply(lambda x: remove_non_alphabets(x))
    # eval_df_form_cnt_denorm = eval_df_form_cnt_denorm[(eval_df_form_cnt_denorm['intent'].isin(impactful_intents.keys()))]
    # eval_df_form_cnt_denorm.drop(['intent'], axis=1)

    eval_df_form_cnt_denorm['intent_selection'] = eval_df_form_cnt_denorm['intent_selection'].astype(int)
    eval_df_form_cnt_denorm['intent_fol_think_1'] = eval_df_form_cnt_denorm['intent_fol_think_1'].astype(int)
    eval_df_form_cnt_denorm['intent_fol_speech_1'] = eval_df_form_cnt_denorm['intent_fol_speech_1'].astype(int)

    # #### Refinement Contemplation

    # setting intent selection reasonability on whether the intent was modified or not.
    # if it was modified we use the modified intents reasonability else we use the original intents reasonability annotation
    eval_df_ref_cnt_int_mod = eval_df_ref_cnt[eval_df_ref_cnt['intent_mod'].notnull()].copy()

    # eval_df_ref_cnt['intent_selection_final'] = eval_df_ref_cnt.apply(lambda row: update_intent_selection_vals(row.intent_mod, row.intent_selection, row.intent_selection_mod), axis=1)
    eval_df_ref_cnt['intent_selection_final'] = eval_df_ref_cnt['intent_selection_mod']
    
    # for filtering non-impactful intents
    # eval_df_ref_cnt['final_intent'] = eval_df_ref_cnt.apply(lambda row: get_final_intent(row.intent_mod, row.intent), axis=1)
    # eval_df_ref_cnt_int_mod['final_intent'] = eval_df_ref_cnt_int_mod.apply(lambda row: get_final_intent(row.intent_mod, row.intent), axis=1)
    
    eval_df_ref_cnt.drop(['intent_selection','intent_selection_mod'], axis=1, inplace=True)
    eval_df_ref_cnt_int_mod.drop(['intent_selection'], axis=1, inplace=True)

    # all intents
    eval_df_ref_cnt_denorm = eval_df_ref_cnt.explode(['intent_selection_final', 'intent_fol_think_2', 'intent_fol_speech_2'])

    # remove non impactful intents
    # eval_df_ref_cnt_denorm = eval_df_ref_cnt.explode(['final_intent', 'intent_selection_final', 'intent_fol_think_2', 'intent_fol_speech_2'])
    # eval_df_ref_cnt_denorm['final_intent'] = eval_df_ref_cnt_denorm['final_intent'].apply(lambda x: remove_non_alphabets(x))
    # eval_df_ref_cnt_denorm = eval_df_ref_cnt_denorm[(eval_df_ref_cnt_denorm['final_intent'].isin(impactful_intents.keys()))]
    # eval_df_ref_cnt_denorm.drop(['final_intent'], axis=1)

    # all intents for intent modification only
    eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod.explode(['intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2'])

    # remove non impactful intents
    # eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod.explode(['final_intent', 'intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2'])
    # eval_df_ref_cnt_int_mod_denorm['final_intent'] = eval_df_ref_cnt_int_mod_denorm['final_intent'].apply(lambda x: remove_non_alphabets(x))
    # eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod_denorm[(eval_df_ref_cnt_int_mod_denorm['final_intent'].isin(impactful_intents.keys()))]
    # eval_df_ref_cnt_int_mod_denorm.drop(['final_intent'], axis=1)

    eval_df_ref_cnt_denorm['intent_selection_final'] = eval_df_ref_cnt_denorm['intent_selection_final'].astype(int)
    eval_df_ref_cnt_denorm['intent_fol_think_2'] = eval_df_ref_cnt_denorm['intent_fol_think_2'].astype(int)
    eval_df_ref_cnt_denorm['intent_fol_speech_2'] = eval_df_ref_cnt_denorm['intent_fol_speech_2'].astype(int)

    eval_df_ref_cnt_int_mod_denorm['intent_selection_mod'] = eval_df_ref_cnt_int_mod_denorm['intent_selection_mod'].astype(int)
    eval_df_ref_cnt_int_mod_denorm['intent_fol_think_2'] = eval_df_ref_cnt_int_mod_denorm['intent_fol_think_2'].astype(int)
    eval_df_ref_cnt_int_mod_denorm['intent_fol_speech_2'] = eval_df_ref_cnt_int_mod_denorm['intent_fol_speech_2'].astype(int)

    return eval_df_form_cnt_denorm, eval_df_ref_cnt_denorm, eval_df_ref_cnt_int_mod_denorm

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


    eval_df['round'] = eval_df['round'].astype(int)

    num_times_intent_modified = len(eval_df[eval_df['intent_mod'].notnull()])
    return_vals['num_times_intent_modified'] = num_times_intent_modified
    return_vals['total_turns'] = len(eval_df)

    # Each quest results dictionary
    quest_results = results_data['quest_results']

    evil_roles = ['Assassin', 'Morgana']
    # dictionary with {'name': 'role'}
    player_to_char = dict((val,key) for key, val in results_data['character_to_player'].items())
    # ## Failure vote rate
    # counting the number of time an evil player votes failure from their voting chances
    evil_players = [key for key, val in player_to_char.items() if val in evil_roles]

    fail_vote, total_vote = get_failure_rate(results_data, evil_players)
    return_vals['failure_rate'] = {'fail_votes': fail_vote, 'total_votes': total_vote}

    evil_quest_wins, loyal_quest_wins = get_quest_win_rate(quest_results)
    return_vals['quest_win_rate'] = {'total': evil_quest_wins + loyal_quest_wins, 'evil': evil_quest_wins, 'loyal': loyal_quest_wins}

    win_side = 'loyal'
    if evil_quest_wins > loyal_quest_wins:
        win_side = 'evil'
    return_vals['game_win'] = win_side

    round_leaders = results_data['round_leaders']
    round_team_members = {rnd: [player.strip() for player in team] for rnd, team in results_data['round_team_members'].items()}

    total_evil, total_loyal, evil_correct, loyal_correct, incorrect_rnds = get_team_selection_accuracy(round_team_members, round_leaders, player_to_char, evil_roles, evil_players)
    return_vals['team_selection_acc'] = {'total_evil': total_evil, 'total_loyal': total_loyal, 'evil_correct': evil_correct, 'loyal_correct': loyal_correct}

    char_qe_count, num_rounds = get_quest_engagement_rate(round_team_members, player_to_char)
    return_vals['char_qe_count'] = char_qe_count
    return_vals['num_rounds'] = num_rounds
    # ## Detailed analysis

    # calculating detailed analysis metrics for total and round wise stats
    # separating our annotation comma separated to list of values
    eval_df['intent'] = eval_df['intent'].apply(lambda x: literal_eval(x))
    eval_df['intent_mod'] = eval_df['intent_mod'].apply(lambda x: literal_eval(x) if x is not np.nan else x )

    eval_df['intent_selection'] = eval_df['intent_selection'].astype(str).apply(comma_string_to_list)
    eval_df['intent_selection_mod'] = eval_df['intent_selection_mod'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_think_1'] = eval_df['intent_fol_think_1'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_speech_1'] = eval_df['intent_fol_speech_1'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_think_2'] = eval_df['intent_fol_think_2'].astype(str).apply(comma_string_to_list)
    eval_df['intent_fol_speech_2'] = eval_df['intent_fol_speech_2'].astype(str).apply(comma_string_to_list)
    eval_df['round_quest_result'] = eval_df['round'].apply(lambda x: 'success' if quest_results[str(x)] == 1 else 'failure')

    # creating a column whether player is evil or loyal
    eval_df['side'] = eval_df['player'].apply(lambda x: find_player_side(x, player_to_char, evil_roles))

    eval_df_form_cnt_denorm, eval_df_ref_cnt_denorm, eval_df_ref_cnt_int_mod_denorm = separate_frm_ref_contemplation(eval_df)

    # intent_level_metrics = get_intent_level_metrics(eval_df)
    # return_vals['intent_level_round_result'] = intent_level_metrics

    num_intents = len(eval_df_form_cnt_denorm) + len(eval_df_ref_cnt_int_mod_denorm)

    num_reasonable_intents = len(eval_df_form_cnt_denorm[eval_df_form_cnt_denorm['intent_selection'] == 1]) + len(eval_df_ref_cnt_int_mod_denorm[eval_df_ref_cnt_int_mod_denorm['intent_selection_mod'] == 1])

    return_vals['num_intents'] = num_intents
    return_vals['num_reasonable_intents'] = num_reasonable_intents
    # ## Metrics

    # ### Calculating stats

    # grouping by loyal/evil, reasonalbe/unreasonable, following rating and getting the count for each think and speak stage

    metrics_form_cnt_think = eval_df_form_cnt_denorm.groupby(['side', 'intent_selection', 'intent_fol_think_1']).size().reset_index(name='count')
    metrics_form_cnt_speech = eval_df_form_cnt_denorm.groupby(['side', 'intent_selection', 'intent_fol_speech_1']).size().reset_index(name='count')

    metrics_ref_cnt_think = eval_df_ref_cnt_denorm.groupby(['side', 'intent_selection_final', 'intent_fol_think_2']).size().reset_index(name='count')
    metrics_ref_cnt_speech = eval_df_ref_cnt_denorm.groupby(['side', 'intent_selection_final', 'intent_fol_speech_2']).size().reset_index(name='count')

    # ## Final metrics calc

    # renaming columns to combine formulation contemplation and refine contemplation data

    metrics_form_cnt_think = metrics_form_cnt_think.rename(columns={'intent_fol_think_1': 'intent_fol_think'})
    metrics_ref_cnt_think = metrics_ref_cnt_think.rename(columns={'intent_fol_think_2': 'intent_fol_think', 'intent_selection_final': 'intent_selection'})
    metrics_form_cnt_speech = metrics_form_cnt_speech.rename(columns={'intent_fol_speech_1': 'intent_fol_speech'})
    metrics_ref_cnt_speech = metrics_ref_cnt_speech.rename(columns={'intent_fol_speech_2': 'intent_fol_speech', 'intent_selection_final': 'intent_selection'})


    # combining the data

    metrics_think = pd.concat([metrics_form_cnt_think, metrics_ref_cnt_think])
    metrics_speech = pd.concat([metrics_form_cnt_speech, metrics_ref_cnt_speech])

    # getting the total think and speech count for intent selection grouped by loyal/evil, reasonable/unreasonable

    total_think = metrics_think.groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')
    total_speech = metrics_speech.groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')

    # getting the intent following >=3 think and speech count for intent selection grouped by loyal/evil, reasonable/unreasonable
    greater_than_3_think = metrics_think[metrics_think['intent_fol_think'] >= 3].groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')
    greater_than_3_speech = metrics_speech[metrics_speech['intent_fol_speech'] >= 3].groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')


    # getting the intent following = 5 think and speech count for intent selection grouped by loyal/evil, reasonable/unreasonable
    think_5 = metrics_think[metrics_think['intent_fol_think'] == 5].groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')
    speech_5 = metrics_speech[metrics_speech['intent_fol_speech'] == 5].groupby(['side', 'intent_selection'])['count'].sum().reset_index(name='count')


    # calucating the final metrics required for detailed analysis table and printing out a json
    # 0 = unresonable, 1 = unreasonable

    keys = [('evil', 0), ('evil', 1), ('loyal', 0), ('loyal', 1)]

    final_total_metrics_gt_3 = {'evil': {}, 'loyal': {}}

    final_total_metrics_5 = {'evil': {}, 'loyal': {}}

    def get_safe_count(df):
        if len(df) > 0:
            return df.values[0]
        return 0

    for side, is_reas in keys:
        total_think_count = get_safe_count(total_think[(total_think['side'] == side) & (total_think['intent_selection'] == is_reas)]['count'])
        total_speech_count = get_safe_count(total_speech[(total_speech['side'] == side) & (total_speech['intent_selection'] == is_reas)]['count'])

        greater_than_3_think_count = get_safe_count(greater_than_3_think[(greater_than_3_think['side'] == side) & (greater_than_3_think['intent_selection'] == is_reas)]['count'])

        greater_than_3_speech_count = get_safe_count(greater_than_3_speech[(greater_than_3_speech['side'] == side) & (greater_than_3_speech['intent_selection'] == is_reas)]['count'])
        
        think_5_count = get_safe_count(think_5[(think_5['side'] == side) & (think_5['intent_selection'] == is_reas)]['count'])

        speech_5_count = get_safe_count(speech_5[(speech_5['side'] == side) & (speech_5['intent_selection'] == is_reas)]['count'])
        
        intent_reas = 'reasonable' if is_reas == 1 else 'unreasonable'
        
        final_total_metrics_gt_3[side][intent_reas] = {
            'following': {'think': greater_than_3_think_count, 'speak': greater_than_3_speech_count},
            'not_following': {'think': total_think_count - greater_than_3_think_count, 'speak': total_speech_count - greater_than_3_speech_count}
        }
        
        final_total_metrics_5[side][intent_reas] = {
            'following': {'think': think_5_count, 'speak': speech_5_count},
            'not_following': {'think': total_think_count - think_5_count, 'speak': total_speech_count - speech_5_count}
        }

    return_vals['gt_3_detailed'] = final_total_metrics_gt_3
    return_vals['equal_5_detailed'] = final_total_metrics_5

    # ### Round metrics
    metrics_form_cnt_think_rnd = eval_df_form_cnt_denorm.groupby(['side', 'intent_selection', 'intent_fol_think_1', 'round', 'round_quest_result']).size().reset_index(name='count')
    metrics_form_cnt_speech_rnd = eval_df_form_cnt_denorm.groupby(['side', 'intent_selection', 'intent_fol_speech_1', 'round', 'round_quest_result']).size().reset_index(name='count')

    metrics_ref_cnt_think_rnd = eval_df_ref_cnt_denorm.groupby(['side', 'intent_selection_final', 'intent_fol_think_2', 'round', 'round_quest_result']).size().reset_index(name='count')
    metrics_ref_cnt_speech_rnd = eval_df_ref_cnt_denorm.groupby(['side', 'intent_selection_final', 'intent_fol_speech_2', 'round', 'round_quest_result']).size().reset_index(name='count')


    metrics_form_cnt_think_rnd = metrics_form_cnt_think_rnd.rename(columns={'intent_fol_think_1': 'intent_fol_think'})
    metrics_ref_cnt_think_rnd = metrics_ref_cnt_think_rnd.rename(columns={'intent_fol_think_2': 'intent_fol_think', 'intent_selection_final': 'intent_selection'})
    metrics_form_cnt_speech_rnd = metrics_form_cnt_speech_rnd.rename(columns={'intent_fol_speech_1': 'intent_fol_speech'})
    metrics_ref_cnt_speech_rnd = metrics_ref_cnt_speech_rnd.rename(columns={'intent_fol_speech_2': 'intent_fol_speech', 'intent_selection_final': 'intent_selection'})

    metrics_think_rnd = pd.concat([metrics_form_cnt_think_rnd, metrics_ref_cnt_think_rnd])
    metrics_speech_rnd = pd.concat([metrics_form_cnt_speech_rnd, metrics_ref_cnt_speech_rnd])

    metrics_ref_rnd = pd.concat([metrics_ref_cnt_think_rnd, metrics_ref_cnt_speech_rnd])

    metrics_speech_rnd = metrics_speech_rnd.rename(columns={'intent_fol_speech': 'intent_fol'})
    metrics_think_rnd = metrics_think_rnd.rename(columns={'intent_fol_think': 'intent_fol'})
    metrics_ref_rnd = metrics_ref_rnd.rename(columns={'intent_fol_think': 'intent_fol'})


    metrics_rnd = pd.concat([metrics_think_rnd, metrics_speech_rnd])

    # metrics_rnd['intent_fol_bin'] = metrics_rnd['intent_fol'].apply(lambda x: 1 if x==5 else 0)
    

    # calucating the round final metrics with round results and percentage values and printing out a json
    # 0 = unresonable, 1 = unreasonable

    # total_rnd = metrics_rnd.groupby(['side', 'intent_selection', 'round', 'round_quest_result'])['count'].sum().reset_index(name='count')

    # for reasonalbe intent


    metrics_rnd['incorrect_team_sel'] = metrics_rnd['round'].apply(lambda x: incorrect_rnds[str(x)])

    # rnd_5 = metrics_rnd[metrics_rnd['intent_fol'] >= 3].groupby(['side', 'intent_selection', 'round', 'incorrect_team_sel'])['count'].sum().reset_index(name='count')

    metrics_rnd['int_fol_bin'] = metrics_rnd['intent_fol'].apply(lambda x: 1 if x >= 3 else 0)
    rnd_discussion = metrics_rnd.groupby(['side', 'int_fol_bin', 'round', 'round_quest_result'])['count'].sum().reset_index(name='count')

    # for intent following
    # metrics_rnd.drop(['intent_selection'], axis=1, inplace=True)
    # metrics_rnd.rename(columns={'intent_fol_bin': 'intent_selection'}, inplace=True)
    # print(metrics_rnd.head())

    # rnd_5 = metrics_rnd.groupby(['side', 'intent_selection', 'round', 'round_quest_result'])['count'].sum().reset_index(name='count')

    # rnd_5['rnd'] = rnd_5['round'].astype(int)
    # rnd_5['sd'] = rnd_5['side'].astype(str)

    rnd_discussion['rnd'] = rnd_discussion['round'].astype(int)
    rnd_discussion['sd'] = rnd_discussion['side'].astype(str)


    round_metrics_dict = {}

    def round_metrics(side, intent_sel, rnd, count):
        if side not in round_metrics_dict:
            round_metrics_dict[side] = {}
        if rnd not in round_metrics_dict[side]:
            round_metrics_dict[side][rnd] = {}
        round_metrics_dict[side][rnd][intent_sel] = count


    for index, row in rnd_discussion.iterrows():
        round_metrics(row['sd'], row['int_fol_bin'], row['rnd'], row['count'])


    final_round_metrics = {}

    for key in quest_results.keys():
        if quest_results[key] is None:
            continue
       
        result = 'success' if quest_results[key] == 1 else 'failure'

        # if quest_results[key] is None or incorrect_rnds[key] == 'none':
        #     continue
        # result = 'success' if incorrect_rnds[key] == 'loyal' else 'failure'

        int_key = int(key)
        
        evil_reas = 0
        evil_unreas = 0
        loyal_reas = 0
        loyal_unreas = 0
        
        if 'evil' in round_metrics_dict:
            if int_key in round_metrics_dict['evil']:
                if 0 in round_metrics_dict['evil'][int_key]:
                    evil_unreas = round_metrics_dict['evil'][int_key][0]
                    
                if 1 in round_metrics_dict['evil'][int_key]:
                    evil_reas = round_metrics_dict['evil'][int_key][1]
            
        if 'loyal' in round_metrics_dict:
            if int_key in round_metrics_dict['loyal']: 
                if 0 in round_metrics_dict['loyal'][int_key]:
                    loyal_unreas = round_metrics_dict['loyal'][int_key][0]
                    
                if 1 in round_metrics_dict['loyal'][int_key]:
                    loyal_reas = round_metrics_dict['loyal'][int_key][1]
            
        total_evil_intents = evil_unreas + evil_reas
        total_loyal_intents = loyal_unreas + loyal_reas
        
        final_round_metrics[int_key] = {
            'result': result, 
            'evil': {'total': total_evil_intents, 'reasonable': evil_reas, 'unreasonable': evil_unreas},
            'loyal': {'total': total_loyal_intents, 'reasonable': loyal_reas, 'unreasonable': loyal_unreas}
        }

    return_vals['round_level'] = final_round_metrics

    return return_vals

###################

def _flatten_dict_gen(d, parent_key, sep):
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            yield from flatten_dict(v, new_key, sep=sep).items()
        else:
            yield new_key, v


def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.'):
    return dict(_flatten_dict_gen(d, parent_key, sep))

def print_flat_dict(dictionary):
    for key, val in dictionary.items():
        print(f"{key}: {val}")

def calc_intent_impact(metrics):
    agg_intent_metrics = {}
    for m in metrics:
        for intent, val in m.items():
            if intent in similar_intent_map:
                intent = similar_intent_map[intent]
            if intent not in agg_intent_metrics:
                agg_intent_metrics[intent] = val
            else:
                for side in ('evil', 'loyal'):
                    if side in val:
                        if side not in agg_intent_metrics[intent]:
                            agg_intent_metrics[intent][side] = val[side]
                        else:
                            for result in ('success', 'failure'):
                                agg_intent_metrics[intent][side][result] = agg_intent_metrics[intent].get(side, {}).get(result, 0) + val.get(side, {}).get(result, 0)
                    
    total = 0
    sorted_intnt_keys = sorted(agg_intent_metrics.keys())
    rev_similar_int_map = defaultdict(list)

    for key, val in similar_intent_map.items():
        rev_similar_int_map[val].append(key)

    for i, key in enumerate(sorted_intnt_keys):
        val = agg_intent_metrics[key]
        evil_favor, evil_fail_count, evil_total = 0, 0, 0
        loyal_favor, loyal_success_count, loyal_total = 0, 0, 0
        high_impact = False
        for side in ('evil', 'loyal'):
            if side in val:
                if side == 'evil':
                    evil_total = val[side].get('success', 0) + val[side].get('failure', 0)
                    evil_fail_count = val[side].get('failure', 0)
                    evil_favor = round(val[side].get('failure', 0)/evil_total, 2)
                else:
                    loyal_total = val[side].get('success', 0) + val[side].get('failure', 0)
                    loyal_success_count = val[side].get('success', 0)
                    loyal_favor = round(val[side].get('success', 0)/loyal_total, 2)

            if (evil_total >= 2 and evil_favor > 0.7) or (loyal_total >= 2 and loyal_favor > 0.7):
                high_impact = True
            if (evil_total >= 2 and evil_favor < 0.3) or (loyal_total >= 2 and loyal_favor < 0.3):
                high_impact = True
            
        total += evil_total + loyal_total
        
        if high_impact:
            # print(f"{key} -> Impact: Evil = {evil_favor}({evil_fail_count}/{evil_total}), Loyal = {loyal_favor}({loyal_success_count}/{loyal_total})")
            impactful_intents1[key] = True
            # if key in rev_similar_int_map:
            #     for intent in rev_similar_int_map[key]:
            #         impactful_intents[intent] = True
        print(f"{i+1}. {key} -> Impact: Evil = {evil_favor}({evil_fail_count}/{evil_total}), Loyal = {loyal_favor}({loyal_success_count}/{loyal_total})")



if __name__ == '__main__':
    gameplay_files = {}
    evaluation_files = {}

    # ANNOTATED_RESULTS_PATH = 'output/gpt-4-games/annotated'
    ANNOTATED_RESULTS_PATH = config_utils.get_config_value("annotated_data_save_path")
    for d in os.listdir(ANNOTATED_RESULTS_PATH):
        if d.startswith('game_'):
            gameplay_folder = f"{ANNOTATED_RESULTS_PATH}/{d}"
            key = d.split('_')[-1]
            for x in os.listdir(gameplay_folder):
                if x.startswith('game_play_data'):
                    gameplay_files[key] = f"{gameplay_folder}/{x}"
                # elif x.startswith('evaluation_') and x.endswith('.csv'):
                #     evaluation_files[key] = f"{gameplay_folder}/{x}"
                # for gpt 3.5
                elif x.startswith('annotation-') and x.endswith('.csv'):
                    evaluation_files[key] = f"{gameplay_folder}/{x}"
    
    print(len(gameplay_files), len(evaluation_files))

    failure_rate_metrics = []
    quest_win_metrics = []
    team_sel_acc_metrics = []
    gt_3_metrics = []
    eq_5_metrics = []

    round_metrics = []

    total_intents = 0
    total_reasonable_intents = 0

    num_times_intent_modified = 0
    total_turns = 0

    total_rounds = 0
    quest_eng_metrics = []

    intent_level_metrics = []
    game_wins = []


    print("Processing files...")
    for key in evaluation_files.keys():
        # print(f"Processed: {key}")
        metrics = process_game(evaluation_files[key], gameplay_files[key])
        failure_rate_metrics.append(metrics['failure_rate'])
        quest_win_metrics.append(metrics['quest_win_rate'])
        team_sel_acc_metrics.append(metrics['team_selection_acc'])
        gt_3_metrics.append(metrics['gt_3_detailed'])
        eq_5_metrics.append(metrics['equal_5_detailed'])
        round_metrics.append(metrics['round_level'])

        total_intents += metrics['num_intents']
        total_reasonable_intents += metrics['num_reasonable_intents']

        num_times_intent_modified += metrics['num_times_intent_modified']
        total_turns += metrics['total_turns']

        quest_eng_metrics.append(metrics['char_qe_count'])
        total_rounds += metrics['num_rounds']
        game_wins.append(metrics['game_win'])


        # intent level metrics
        # intent_level_metrics.append(metrics['intent_level_round_result'])
    print(f'\nTotal turns: {total_turns}')

    print(f"\nIntent selection (reasonable): {(total_reasonable_intents/total_intents)*100:.2f}% ({total_reasonable_intents}/{total_intents})\n")

    print(f"Intent modificaiton: {(num_times_intent_modified/total_turns)*100:.2f}% ({num_times_intent_modified}/{total_turns})\n")

    print("Intent Level Impact:\n")
    calc_intent_impact(intent_level_metrics)
    print(impactful_intents1)

    quest_eng_rate = Counter()
    for m in quest_eng_metrics:
        quest_eng_rate += Counter(m)

    quest_eng_rate = dict(quest_eng_rate)
    print("Character-wise Quest Engagement Rate:")
    print(f"Total rounds: {total_rounds}")
    print(quest_eng_rate)


    failure_rate = Counter()
    for m in failure_rate_metrics:
        failure_rate += Counter(m)

    print("\nFailure Vote Rate:")
    print(dict(failure_rate))

    quest_win_rate = Counter()
    for m in quest_win_metrics:
        quest_win_rate += Counter(m)

    print("\nQuest Win Rate:")
    print(dict(quest_win_rate))

    team_sel_acc = Counter()
    for m in team_sel_acc_metrics:
        team_sel_acc += Counter(m)

    print("\nTeam Selection Accuracy:")
    print(dict(team_sel_acc))

    gt_3_detailed = Counter()
    for m in gt_3_metrics:
        m = flatten_dict(m)
        gt_3_detailed += Counter(m)

    gt_3_detailed = dict(gt_3_detailed)
    
    gt_3_evil_total = 0
    gt_3_evil_total_following = 0
    gt_3_evil_total_reasonable = 0
    gt_3_loyal_total = 0
    gt_3_loyal_total_following = 0
    gt_3_loyal_total_reasonable = 0

    print("\nDetailed metrics (intent following >= 3)\n")
    print_flat_dict(gt_3_detailed)

    for key, val in gt_3_detailed.items():
        if 'evil' in key:
            gt_3_evil_total += val
            if '.following' in key:
                gt_3_evil_total_following += val
            if '.reasonable' in key:
                gt_3_evil_total_reasonable += val
        elif 'loyal' in key:
            gt_3_loyal_total += val
            if '.following' in key:
                gt_3_loyal_total_following += val
            if '.reasonable' in key:
                gt_3_loyal_total_reasonable += val

    gt_3_following_count = (gt_3_evil_total_following + gt_3_loyal_total_following) 
    gt_3_following_per = round(gt_3_following_count / (gt_3_evil_total + gt_3_loyal_total) , 4)

    eq_5_detailed = Counter()
    for m in eq_5_metrics:
        m = flatten_dict(m)
        eq_5_detailed += Counter(m)

    eq_5_detailed = dict(eq_5_detailed)

    print("\nDetailed metrics (intent following = 5)\n")
    print_flat_dict(eq_5_detailed)
    
    eq_5_evil_total = 0
    eq_5_evil_total_following = 0
    eq_5_evil_total_reasonable = 0
    eq_5_loyal_total = 0
    eq_5_loyal_total_following = 0
    eq_5_loyal_total_reasonable = 0

    for key, val in eq_5_detailed.items():
        if 'evil' in key:
            eq_5_evil_total += val
            if '.following' in key:
                eq_5_evil_total_following += val
            if '.reasonable' in key:
                eq_5_evil_total_reasonable += val
        elif 'loyal' in key:
            eq_5_loyal_total += val
            if '.following' in key:
                eq_5_loyal_total_following += val
            if '.reasonable' in key:
                eq_5_loyal_total_reasonable += val

    eq_5_following_count = (eq_5_evil_total_following + eq_5_loyal_total_following) 
    eq_5_following_per = round(eq_5_following_count / (eq_5_evil_total + eq_5_loyal_total) , 4)


    print(f"\nIntent selection and following:")
    print(f"Greater than >=3: {gt_3_following_per*100:.2f}% ({gt_3_following_count}/{(gt_3_evil_total + gt_3_loyal_total)})")
    print(f"Equal to 5: {eq_5_following_per*100:.2f}% ({eq_5_following_count}/{(eq_5_evil_total + eq_5_loyal_total)})")

    ## Round level aggregation
    success_rounds = []
    failure_rounds = []

    success_evil_more_reas_count = 0
    success_loyal_more_reas_count = 0
    success_eq_count = 0
    failure_evil_more_reas_count = 0
    failure_loyal_more_reas_count = 0
    failure_eq_count = 0

    evil_win_evil_more_reas_count = 0
    evil_win_loyal_more_reas_count = 0
    evil_win_eq_count = 0
    loyal_win_evil_more_reas_count = 0
    loyal_win_loyal_more_reas_count = 0
    loyal_win_eq_count = 0

    for m, win_side in zip(round_metrics, game_wins):
        game_loyal_reasonable = 0
        game_loyal_total = 0

        game_evil_reasonable = 0
        game_evil_total = 0

        for key, val in m.items():
            loyal_reasonable = val['loyal']['reasonable']
            loyal_total = val['loyal']['total']

            game_loyal_reasonable += loyal_reasonable
            game_loyal_total += loyal_total

            evil_reasonable = val['evil']['reasonable']
            evil_total = val['evil']['total']
            game_evil_reasonable += evil_reasonable
            game_evil_total += evil_total

            loyal_per = 0
            if loyal_total > 1:
                loyal_per = round(loyal_reasonable/loyal_total, 2)
            else:
                continue

            evil_per = 0
            if evil_total > 1:
                evil_per = round(evil_reasonable/evil_total, 2)
            else:
                continue

            metric = {'evil': evil_per, 'loyal': loyal_per}

            if val['result'] == 'success':
                success_rounds.append(metric)
                if evil_per == loyal_per:
                    success_eq_count += 1
                elif evil_per > loyal_per:
                    success_evil_more_reas_count += 1
                else:
                    success_loyal_more_reas_count += 1
            else:
                failure_rounds.append(metric)
                if evil_per == loyal_per:
                    failure_eq_count += 1
                elif evil_per > loyal_per:
                    failure_evil_more_reas_count += 1
                else:
                    failure_loyal_more_reas_count += 1
                    # print(loyal_reasonable, loyal_total, evil_reasonable, evil_total)
        
        if game_evil_total == 0 or game_loyal_total == 0:
            continue
        game_loyal_per = round(game_loyal_reasonable/game_loyal_total, 2)
        game_evil_per = round(game_evil_reasonable/game_evil_total, 2)

        if win_side == 'loyal':
            if game_loyal_per == game_evil_per:
                loyal_win_eq_count += 1
            elif game_loyal_per > game_evil_per:
                loyal_win_loyal_more_reas_count += 1
            else:
                loyal_win_evil_more_reas_count += 1
        else:
            if game_loyal_per == game_evil_per:
                evil_win_eq_count += 1
            elif game_loyal_per > game_evil_per:
                evil_win_loyal_more_reas_count += 1
            else:
                evil_win_evil_more_reas_count += 1



    print("\nSuccess rounds:")
    success_total = success_evil_more_reas_count + success_loyal_more_reas_count + success_eq_count
    print(success_total)
    # print(success_rounds)
    print(f"More following = Evil: {success_evil_more_reas_count/success_total:.3f}, Loyal: {success_loyal_more_reas_count/success_total:.3f}, Equal: {success_eq_count/success_total:.3f}")
    print("\nFailure rounds:")
    failure_total = failure_evil_more_reas_count + failure_loyal_more_reas_count + failure_eq_count
    print(failure_total)
    # print(failure_rounds)
    print(f"More following = Evil: {failure_evil_more_reas_count/failure_total:.3f}, Loyal: {failure_loyal_more_reas_count/failure_total:.3f}, Equal: {failure_eq_count/failure_total:.3f}")

    print("\nLoyal wins:")
    # print(success_rounds)
    print(f"More following = Evil: {loyal_win_evil_more_reas_count}, Loyal: {loyal_win_loyal_more_reas_count}, Equal: {loyal_win_eq_count}")
    print("\nEvil wins:")
    # print(failure_rounds)
    print(f"More following = Evil: {evil_win_evil_more_reas_count}, Loyal: {evil_win_loyal_more_reas_count}, Equal: {evil_win_eq_count}")















