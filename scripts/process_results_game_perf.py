
import json
import os
import re
from collections import Counter, defaultdict
from collections.abc import MutableMapping

import numpy as np
import pandas as pd

import config_utils

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

impactful_intents_new = {
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

impactful_intents = {
    'counter the team proposal because you think a player on the team is evil': True, 
    'defend yourself against allegations that you could be evil': True, 
    'express concerns about a player from a failed quest team and suggest to not include them in the current team': True, 
    'express confusion for failure of mission': True, 
    'express disagreement and vote disagree only if you are not in the proposed team': True, 
    'include loyal players on the quest team as leader': True, 
    'pretend to be merlin by providing hints on who is evil': True, 
    'pretend to have information and act like merlin': True, 
    'provide hints to loyal players about evil players': True, 
    'question a player about why they changed their statements': True, 
    'question a player on why they didnt vote for the last team': True, 
    'question the leader why they selected a particular player for the team': True, 
    'share concerns about an evil player': True, 
    'stay hidden in discussions and act like a loyal servant to protect yourself': True, 
    'support team proposal': True, 
    'support your teammate to be on the quest team': True
}


def read_data(results_path):
    with open(results_path) as f:
        results_data = json.loads(f.read())
    return results_data

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
    for key, val in round_team_members.items():
        if len(val) == 0:
            continue
        leader = round_leaders[key]
        
        if leader in evil_players:
            total_evil += 1
            for member in val:
                role = player_to_char[member]
                if role in evil_roles:
                    # if we fina an evil player, then team is accurate for evil player and we increase counta and break
                    evil_correct += 1
                    break
        else:
            total_loyal += 1
            found_evil = False
            for member in val:
                role = player_to_char[member]
                if role in evil_roles:
                    # if we fina an evil player, then team is wrong for loyal player and we set flag to true and break
                    found_evil = True
                    break
            if not found_evil:
                # according to flag we increase count of correct selection
                loyal_correct += 1

    return total_evil, total_loyal, evil_correct, loyal_correct

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



def separate_frm_ref_contemplaton(eval_df):
    # separating formulation contemplation and refinement contemplation to handle intent modificaiton, Will combine later
    eval_df_form_cnt = eval_df[['player', 'side', 'round', 'intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1', 'round_quest_result']].copy()
    eval_df_ref_cnt = eval_df[['player', 'side', 'round', 'intent', 'intent_mod', 'intent_selection', 'intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2', 'round_quest_result']].copy()

    # ## Processing dfs for analysis (splitting values into separate rows)
    # #### Formulation contemplation

    # exploding would create separate rows for our annotation and help to aggregate

    # all intents
    # eval_df_form_cnt_denorm = eval_df_form_cnt.explode(['intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1'])
    
    # remove non impactful intents
    eval_df_form_cnt_denorm = eval_df_form_cnt.explode(['intent', 'intent_selection', 'intent_fol_think_1', 'intent_fol_speech_1'])
    eval_df_form_cnt_denorm['intent'] = eval_df_form_cnt_denorm['intent'].apply(lambda x: remove_non_alphabets(x))
    eval_df_form_cnt_denorm = eval_df_form_cnt_denorm[(eval_df_form_cnt_denorm['intent'].isin(impactful_intents.keys()))]
    eval_df_form_cnt_denorm.drop(['intent'], axis=1)

    eval_df_form_cnt_denorm['intent_selection'] = eval_df_form_cnt_denorm['intent_selection'].astype(int)
    eval_df_form_cnt_denorm['intent_fol_think_1'] = eval_df_form_cnt_denorm['intent_fol_think_1'].astype(int)
    eval_df_form_cnt_denorm['intent_fol_speech_1'] = eval_df_form_cnt_denorm['intent_fol_speech_1'].astype(int)

    # #### Refinement Contemplation

    # setting intent selection reasonability on whether the intent was modified or not.
    # if it was modified we use the modified intents reasonability else we use the original intents reasonability annotation
    eval_df_ref_cnt_int_mod = eval_df_ref_cnt[eval_df_ref_cnt['intent_mod'].notnull()].copy()

    eval_df_ref_cnt['intent_selection_final'] = eval_df_ref_cnt.apply(lambda row: update_intent_selection_vals(row.intent_mod, row.intent_selection, row.intent_selection_mod), axis=1)
    
    # for filtering non-impactful intents
    eval_df_ref_cnt['final_intent'] = eval_df_ref_cnt.apply(lambda row: get_final_intent(row.intent_mod, row.intent), axis=1)
    eval_df_ref_cnt_int_mod['final_intent'] = eval_df_ref_cnt_int_mod.apply(lambda row: get_final_intent(row.intent_mod, row.intent), axis=1)
    
    eval_df_ref_cnt.drop(['intent_selection','intent_selection_mod'], axis=1, inplace=True)
    eval_df_ref_cnt_int_mod.drop(['intent_selection'], axis=1, inplace=True)

    # all intents
    # eval_df_ref_cnt_denorm = eval_df_ref_cnt.explode(['intent_selection_final', 'intent_fol_think_2', 'intent_fol_speech_2'])

    # remove non impactful intents
    eval_df_ref_cnt_denorm = eval_df_ref_cnt.explode(['final_intent', 'intent_selection_final', 'intent_fol_think_2', 'intent_fol_speech_2'])
    eval_df_ref_cnt_denorm['final_intent'] = eval_df_ref_cnt_denorm['final_intent'].apply(lambda x: remove_non_alphabets(x))
    eval_df_ref_cnt_denorm = eval_df_ref_cnt_denorm[(eval_df_ref_cnt_denorm['final_intent'].isin(impactful_intents.keys()))]
    eval_df_ref_cnt_denorm.drop(['final_intent'], axis=1)

    # all intents for intent modification only
    # eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod.explode(['intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2'])

    # remove non impactful intents
    eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod.explode(['final_intent', 'intent_selection_mod', 'intent_fol_think_2', 'intent_fol_speech_2'])
    eval_df_ref_cnt_int_mod_denorm['final_intent'] = eval_df_ref_cnt_int_mod_denorm['final_intent'].apply(lambda x: remove_non_alphabets(x))
    eval_df_ref_cnt_int_mod_denorm = eval_df_ref_cnt_int_mod_denorm[(eval_df_ref_cnt_int_mod_denorm['final_intent'].isin(impactful_intents.keys()))]
    eval_df_ref_cnt_int_mod_denorm.drop(['final_intent'], axis=1)

    eval_df_ref_cnt_denorm['intent_selection_final'] = eval_df_ref_cnt_denorm['intent_selection_final'].astype(int)
    eval_df_ref_cnt_denorm['intent_fol_think_2'] = eval_df_ref_cnt_denorm['intent_fol_think_2'].astype(int)
    eval_df_ref_cnt_denorm['intent_fol_speech_2'] = eval_df_ref_cnt_denorm['intent_fol_speech_2'].astype(int)

    eval_df_ref_cnt_int_mod_denorm['intent_selection_mod'] = eval_df_ref_cnt_int_mod_denorm['intent_selection_mod'].astype(int)
    eval_df_ref_cnt_int_mod_denorm['intent_fol_think_2'] = eval_df_ref_cnt_int_mod_denorm['intent_fol_think_2'].astype(int)
    eval_df_ref_cnt_int_mod_denorm['intent_fol_speech_2'] = eval_df_ref_cnt_int_mod_denorm['intent_fol_speech_2'].astype(int)

    return eval_df_form_cnt_denorm, eval_df_ref_cnt_denorm, eval_df_ref_cnt_int_mod_denorm

def comma_string_to_list(x):
    if x != 'NaN':
        return [val.strip() for val in x.split(',') if val != '']
    else:
        print('here')
        return np.NaN
    

def extract_values(dictionary, key, ignore_key=None):
    values_with_no_ignored_key = []
    values_with_ignored_key = []

    # Recursive function to traverse through the dictionary
    def traverse_dict(d):
        for k, v in d.items():
            if k == key:
                if ignore_key and ignore_key in d:
                    values_with_ignored_key.append(v)
                else:
                    values_with_no_ignored_key.append(v)
            elif isinstance(v, dict):
                traverse_dict(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        traverse_dict(item)

    traverse_dict(dictionary)
    return values_with_no_ignored_key, values_with_ignored_key

def get_retained_intents_count(selected_intents):
    count, intents_count, impact_intent_count = 0, 0, 0
    for intents in selected_intents:
        intents_count += len(intents)
        found = False
        for intent in impactful_intents_new.keys():
            if intent in intents:
                if not found:
                    count += 1
                    found = True
                
                impact_intent_count += 1

    return count, intents_count, impact_intent_count
    
def count_impactful_intents_sel(pipeline_data):
    intents_with_no_mod, intents_later_mod = extract_values(pipeline_data, "intent", "intent_modification")
    orig_intents_no_mod = [[remove_non_alphabets(x) for x in val[0]['intents']] for val in intents_with_no_mod]
    orig_intents_later_mod = [[remove_non_alphabets(x) for x in val[0]['intents']] for val in intents_later_mod]

    values2, _ = extract_values(pipeline_data, "intent_modification")
    mod_intents = [[remove_non_alphabets(x) for x in val[0]['new_intents']] for val in values2]

    orig_retained_count, orig_count, impact_count_1 = get_retained_intents_count(orig_intents_no_mod)
    orig_retained_later_mod_count, orig_later_mod_count, impact_count_2 = get_retained_intents_count(orig_intents_later_mod)
    mod_retained_count, mod_count, impact_count_3 = get_retained_intents_count(mod_intents)

    # sample count is sum of the following -> 
    # 4 * orig_retained_count (intents not modified - 2 think and 2 speech), 
    # 2 * orig_retained_later_mod_count (1 think, 1 speech -> intents modified)
    # 2 * mod_retained_count (1 think, 1 speech -> new modified intents)

    impact_count = impact_count_1 + impact_count_2 + impact_count_3

    return 4 * orig_retained_count + 2 * orig_retained_later_mod_count + 2 * mod_retained_count, orig_count + orig_later_mod_count, mod_count, impact_count
        
    

def process_game(results_path, pipeline_data_path):

    return_vals = {}

    results_data = read_data(results_path)
    pipeline_data = read_data(pipeline_data_path)

    num_annot_samples,  num_orig_intents, num_mod_intents, impact_count = count_impactful_intents_sel(pipeline_data)
    # print(num_annot_samples,  num_orig_intents, num_mod_intents)
    return_vals['num_annot_samples'] = num_annot_samples
    return_vals['num_orig_intents'] = num_orig_intents
    return_vals['num_mod_intents'] = num_mod_intents
    return_vals['impact_count'] = impact_count

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

    round_leaders = results_data['round_leaders']
    round_team_members = results_data['round_team_members']

    for key, val in round_team_members.items():
        round_team_members[key] = [member.strip() for member in val]

    total_evil, total_loyal, evil_correct, loyal_correct = get_team_selection_accuracy(round_team_members, round_leaders, player_to_char, evil_roles, evil_players)
    return_vals['team_selection_acc'] = {'total_evil': total_evil, 'total_loyal': total_loyal, 'evil_correct': evil_correct, 'loyal_correct': loyal_correct}

    char_qe_count, num_rounds = get_quest_engagement_rate(round_team_members, player_to_char)
    return_vals['char_qe_count'] = char_qe_count
    return_vals['num_rounds'] = num_rounds

    evil_win, loyal_win = 0, 0
    if evil_quest_wins > loyal_quest_wins:
        evil_win = 1
    else:
        loyal_win = 1
    return_vals['game_win'] = {"evil": evil_win, "loyal": loyal_win}
    # ## Detailed analysis

    # calculating detailed analysis metrics for total and round wise stats
    # separating our annotation comma separated to list of values

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

            if (evil_total >= 1 and evil_favor > 0.5) or (loyal_total >= 1 and loyal_favor > 0.5):
                high_impact = True
            if (evil_total >= 1 and evil_favor < 0.5) or (loyal_total >= 1 and loyal_favor < 0.5):
                high_impact = True
            
        total += evil_total + loyal_total
        
        if high_impact:
            # print(f"{key} -> Impact: Evil = {evil_favor}({evil_fail_count}/{evil_total}), Loyal = {loyal_favor}({loyal_success_count}/{loyal_total})")
            impactful_intents[key] = True
            # if key in rev_similar_int_map:
            #     for intent in rev_similar_int_map[key]:
            #         impactful_intents[intent] = True
        # print(f"{i+1}. {key} -> Impact: Evil = {evil_favor}({evil_fail_count}/{evil_total}), Loyal = {loyal_favor}({loyal_success_count}/{loyal_total})")



if __name__ == '__main__':
    gameplay_files = {}
    evaluation_files = {}
    pipeline_data_files = {}

    output_folder = config_utils.get_config_value("annotated_data_save_path")

    for x in os.listdir(output_folder):
        if x.startswith('game_'):
            for y in os.listdir(output_folder + x):
                if y.startswith('game_play_data'):
                    key = x.replace('game_', '').split('.')[0]
                    gameplay_files[key] = output_folder + x + '/' + y
                if y.startswith('results'):
                    key = x.replace('game_', '').split('.')[0]
                    pipeline_data_files[key] = output_folder + x + '/' + y

    print(len(gameplay_files))
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

    win_metrics = []

    total_samples_to_annotate = 0
    total_orig_intents = 0
    total_mod_intents = 0
    total_impact_sel = 0

    print("Processing files...")
    for key in gameplay_files.keys():
        print(f"Processed: {key}")
        metrics = process_game(gameplay_files[key], pipeline_data_files[key])
        failure_rate_metrics.append(metrics['failure_rate'])
        quest_win_metrics.append(metrics['quest_win_rate'])
        team_sel_acc_metrics.append(metrics['team_selection_acc'])

        quest_eng_metrics.append(metrics['char_qe_count'])
        total_rounds += metrics['num_rounds']

        total_samples_to_annotate += metrics['num_annot_samples']
        total_orig_intents += metrics['num_orig_intents']
        total_mod_intents += metrics['num_mod_intents']

        total_impact_sel += metrics['impact_count']

        win_metrics.append(metrics['game_win'])

    print(f"\nTotal samples to annotate = {total_samples_to_annotate}\n")
    print(f"\nTotal original intents = {total_orig_intents}\n")
    print(f"\nTotal modified intents = {total_mod_intents}\n")
    print(f"\nTotal impact intents = {total_impact_sel}\n")

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

    win_rate = Counter()
    for m in win_metrics:
        win_rate += Counter(m)

    print("\nWin Rate:")
    print(dict(win_rate))

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
















