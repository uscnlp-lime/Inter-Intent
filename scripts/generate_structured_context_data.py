import os
import random
import pandas as pd

import config_utils
from utils import *
import constants


def get_role_extra_info(role, chart_to_player):
    if role == "Merlin":
        return f"{chart_to_player['Morgana']} and {chart_to_player['Assassin']} are evil players"
    elif role == "Percival":
        return f"{chart_to_player['Merlin']} and {chart_to_player['Morgana']} are Merlin and Morgana, but you don't know which is Merlin and which is Morgana."
    elif role == "Servant":
        return ""
    elif role == "Morgana":
        return f"Assassin is {chart_to_player['Assassin']}"
    return f"Morgana is {chart_to_player['Morgana']}"


def format_context_v2(data, template, inclued_extra_role_details=False, include_discussion=False):
    char_to_player = data['char_to_player']
    # other_players = ", ".join([f"{val} = {key}" for key, val in sorted(char_to_player.items(), key=lambda x: x[1]) if val != data['name']])

    previous_results = "No previous results."
    if len(data['previous_results']) > 0:
        previous_results = '\n'.join(
            [f"Round {key}: Team = {', '.join(val['team'])}, Result = {val['result']}" for key, val in
             data['previous_results'].items()])

    previous_votes = "No previous team votes. This is the first round."
    if len(data['previous_votes']) > 0:
        previous_votes = data['previous_votes']

    previous_summaries = "No previous summaries. This is the first round."
    if len(data['previous_summaries']) > 0:
        previous_summaries = data['previous_summaries']

    if inclued_extra_role_details:
        role_extra_info = get_role_extra_info(data['role'], char_to_player)
        role_details = data['role_details'] + '\n- ' + role_extra_info
    else:
        role_details = data['role_details']

    formatted_context = template.format(
        data['name'],
        data['role'],
        role_details,
        int(data['round']) % 10,
        data['round_leader'],
        ', '.join(data['round_team']),
        previous_votes,
        previous_results,
        previous_summaries
    )

    if include_discussion:
        previous_discussions = "No previous discussions."
        if len(data['previous_discussions']) > 0:
            previous_discussions = data['previous_discussions']
        formatted_context += constants.reasonable_intent_context_template_extn.format(previous_discussions)

    return formatted_context

def format_context(data, include_discussion=False):
    char_to_player = data['char_to_player']
    # other_players = ", ".join([f"{val} = {key}" for key, val in sorted(char_to_player.items(), key=lambda x: x[1]) if val != data['name']])

    previous_results = "No previous results."
    if len(data['previous_results']) > 0:
        previous_results = '\n'.join([f"Round {key}: Team = {', '.join(val['team'])}, Result = {val['result']}" for key, val in data['previous_results'].items()])

    previous_votes = "No previous team votes. This is the first round."
    if len(data['previous_votes']) > 0:
        previous_votes = data['previous_votes']

    previous_summaries = "No previous summaries. This is the first round."
    if len(data['previous_summaries']) > 0:
        previous_summaries = data['previous_summaries']

    role_extra_info = get_role_extra_info(data['role'], char_to_player)
    role_details_enriched = data['role_details'] + '\n- ' + role_extra_info

    context = constants.context_template.format(
        data['name'],
        data['role'],
        role_details_enriched,
        int(data['round'])%10,
        data['round_leader'],
        ', '.join(data['round_team']),
        previous_votes,
        previous_results,
        previous_summaries
    )

    if include_discussion:
        previous_discussions = "No previous discussions."
        if len(data['previous_discussions']) > 0:
            previous_discussions = data['previous_discussions']
        context += constants.reasonable_intent_context_template_extn.format(previous_discussions)

    return context


def format_context_for_intent_guessing(data, include_discussion=False):
    char_to_player = data['char_to_player']
    # other_players = ", ".join([f"{val} = {key}" for key, val in sorted(char_to_player.items(), key=lambda x: x[1]) if val != data['name']])

    previous_results = "No previous results."
    if len(data['previous_results']) > 0:
        previous_results = '\n'.join([f"Round {key}: Team = {', '.join(val['team'])}, Result = {val['result']}" for key, val in data['previous_results'].items()])

    previous_votes = "No previous team votes. This is the first round."
    if len(data['previous_votes']) > 0:
        previous_votes = data['previous_votes']

    previous_summaries = "No previous summaries. This is the first round."
    if len(data['previous_summaries']) > 0:
        previous_summaries = data['previous_summaries']
    
    role_details_player = data['role_details']

    context = constants.intent_guessing_context_template.format(
        data['name'],
        data['role'],
        role_details_player,
        int(data['round'])%10,
        data['speaker_name'],
        data['round_leader'],
        ', '.join(data['round_team']),
        previous_votes,
        previous_results,
        previous_summaries
    )

    if include_discussion:
        previous_discussions = "No previous discussions."
        if len(data['previous_discussions']) > 0:
            previous_discussions = data['previous_discussions']
        context += constants.reasonable_intent_context_template_extn.format(previous_discussions)

    return context


def format_context_for_second_order_intent_guessing(data, include_discussion=False):
    # char_to_player = data['char_to_player']

    # other_players = ", ".join([f"{val} = {key}" for key, val in sorted(char_to_player.items(), key=lambda x: x[1]) if val != data['name']])
    previous_results = "No previous results."
    if len(data['previous_results']) > 0:
        previous_results = '\n'.join([f"Round {key}: Team = {', '.join(val['team'])}, Result = {val['result']}" for key, val in data['previous_results'].items()])

    previous_votes = "No previous team votes. This is the first round."
    if len(data['previous_votes']) > 0:
        previous_votes = data['previous_votes']

    previous_summaries = "No previous summaries. This is the first round."
    if len(data['previous_summaries']) > 0:
        previous_summaries = data['previous_summaries']
    
    role_details_speaker = data['speaker_role_details']

    context = constants.second_order_intent_guessing_context_template.format(
        data['speaker_name'],
        data['speaker_role'],
        role_details_speaker,
        int(data['round']) % 10,
        data['name'],
        data['round_leader'],
        ', '.join(data['round_team']),
        previous_votes,
        previous_results,
        previous_summaries
    )

    if include_discussion:
        previous_discussions = "No previous discussions."
        if len(data['previous_discussions']) > 0:
            previous_discussions = data['previous_discussions']
        context += constants.reasonable_intent_context_template_extn.format(previous_discussions)

    return context


player_order = {
    '1': [1, 2, 3, 4, 5],
    '2': [2, 3, 4, 5, 1],
    '3': [3, 4, 5, 1, 2],
    '4': [4, 5, 1, 2, 3],
    '5': [5, 1, 2, 3, 4]
}


players = ['Player' + str(num) for num in range(1, 6)]
rounds = [str(num) for num in range(1, 6)]
rounds.extend([str(num) for num in range(11, 16)])


def get_previous_discussions(cur_player, cur_rnd, data, round_leader):
    player_id = int(cur_player.replace('Player', ''))
    round_leader_id = round_leader.replace('Player', '')

    idx = 0
    for i, val in enumerate(player_order[round_leader_id]):
        if val == player_id:
            idx = i
            break


    previous_players = [f'Player{i}' for i in player_order[round_leader_id][:idx]]

    discussions = []
    for player in previous_players:
        discussions.append(f"{player}: {data[player][cur_rnd]['discussion'][0]['speech']}")
    return '\n'.join(discussions)


summary_questions = [
    "Who was the leader for this round?",
    "What was the proposed team for this round?",
    "Why do you think the leader proposed the current team?",
    "Did everyone agree for the proposed team?",
    "If some people disagreed, why do you think they disagreed?",
    "Was the quest successful?",
    "If the quest was successful, was any evil player part of the team? If yes, then why did they vote success?",
    "If the quest failed, how do you plan to protect the evil player in the next round?",
    "What do the evil side need to do from here to win the game?"
]


def get_previous_round_summaries(name, cur_round, data):
    summaries = {}
    cur_round_mod = int(cur_round)%10
    for rnd in rounds:
        if int(rnd)%10 <= cur_round_mod:
            if rnd in data[name] and 'summary' in data[name][rnd]:
                summary = json.loads(data[name][rnd]['summary'][0]['summary'])['Answers']
                summary_txt = ''
                for idx in range(len(summary)):
                    summary_txt += f"{summary[idx]}\n"
                summaries[rnd] = summary_txt
    
    summaries_list = [(round, summaries[round]) for round in sorted(summaries.keys(), key=lambda x: int(x[-1]))]

    disagreement_msg = '(players didn\"t agree on team)'
    res = '\n'.join(f"Round {int(rnd)%10} {disagreement_msg if str(int(rnd)+10) in summaries else ''}: \n{val} \n" for rnd, val in summaries_list)
    sum_q_txt = '\n'.join(summary_questions)
    res = f"Summary questions: \n\n{sum_q_txt}\n\n{res}"
    return res


def check_int_fol(int_fol):
    fol_think, fol_speech = int_fol[0], int_fol[1]
    for a, b in zip(fol_think, fol_speech):
        if a < 3 or b < 3:
            return False
    return True


def get_summarization_data_point(sample_id, all_intents, formulation_con_data, refinement_con_data, context_intnt_following, int_fol_form, int_fol_ref):
    if len(all_intents["modified"]) == 0 or set(all_intents["original"]) == set(all_intents["modified"]):
        if check_int_fol(int_fol_form):
            sample_id = sample_id + "_form"
            complete_intent_following = {
                'id': sample_id,
                'context': context_intnt_following,
                'intents': all_intents["original"],
                'think': formulation_con_data['think'],
                'speak': formulation_con_data['speech'],
            }
            return [complete_intent_following]
    
    res = []
    if check_int_fol(int_fol_form):
        form_intent_following = {
            'id': sample_id + "_form",
            'context': context_intnt_following,
            'intents': all_intents["original"],
            'think': formulation_con_data['think'],
            'speak': formulation_con_data['speech'],
        }
        res.append(form_intent_following)

    if check_int_fol(int_fol_ref):
        ref_intent_following = {
            'id': sample_id + "_ref",
            'context': context_intnt_following,
            'intents': all_intents["modified"],
            'think': refinement_con_data['think'],
            'speak': refinement_con_data['speech'],
        }
        res.append(ref_intent_following)

    return res


def get_context_for_intent_guessing(context1):
    context = context1.copy()
    character_to_player = context['char_to_player']
    roles = list(character_to_player.keys())
    player_role = context['role']
    player_name = context['name']
    player_role_details = constants.role_details[player_role]

    role_choices = [v for v in roles if v != player_role]
    selected_role = random.choice(role_choices)
    selected_player = character_to_player[selected_role]

    selected_role_details = constants.role_details[selected_role]
    extra_role_info = get_role_extra_info(selected_role, character_to_player)
    selected_role_details = selected_role_details + '\n- ' + extra_role_info

    context['speaker_name'] = player_name
    context['speaker_role'] = player_role
    context['speaker_role_details'] = player_role_details
    context['name'] = selected_player
    context['role'] = selected_role
    context['role_details'] = selected_role_details

    # return format_context_for_intent_guessing(context, include_discussion=True)
    return format_context_for_second_order_intent_guessing(context, include_discussion=True)


def get_single_round_data(
        gameplay_id,
        cur_round,
        gameplay_data,
        raw_data,
        role,
        name,
        complete_results,
        vote_results,
        int_following_form,
        int_following_ref
):
    intent_data = raw_data['intent'][0]
    intents = intent_data['intents']
    intents = [remove_non_alphabets(intent) for intent in intents]
    reason = intent_data['think']

    round_leader = gameplay_data['round_leaders'][cur_round]

    previous_discussions = get_previous_discussions(name, cur_round, complete_results, round_leader)
    previous_summaries = get_previous_round_summaries(name, cur_round, complete_results)

    formulation_con_data = raw_data['formulation_con'][0]

    modified_intents = intents
    if 'intent_modification' in raw_data:
        intent_modification_data = raw_data['intent_modification'][0]
        modified_intents = intent_modification_data['new_intents']
        modified_intents = [remove_non_alphabets(intent) for intent in modified_intents]

    refinement_con_data = raw_data['discussion'][0]

    quest_results = gameplay_data['team_quest_result']

    cur_team = []

    previous_votes = {}
    for rnd in vote_results.keys():
        if int(rnd) % 10 <= int(cur_round)%10:
            vote_txt = ', '.join([f"{player} = {vote}" for player, vote in vote_results[rnd].items()])
            previous_votes[rnd] = vote_txt

    previous_votes_list = [(round, previous_votes[round]) for round in sorted(previous_votes.keys(), key=lambda x: int(x[-1]))]

    disagreement_msg = '(players didn\"t agree on team)'
    previous_votes_str = '\n'.join(f"Round {int(rnd)%10}: {val} {disagreement_msg if str(int(rnd)+10) in previous_votes else ''}" for rnd, val in previous_votes_list)

    previous_results = {}
    for rnd in quest_results.keys():
        if int(rnd)%10 < int(cur_round)%10:
            team = list(quest_results[rnd].keys())
            result = 'success'
            if 'failure' in quest_results[rnd].values():
                result = 'failure'
            previous_results[rnd] = {'team': team, 'result': result}
        if int(rnd) == int(cur_round) and name != round_leader:
            cur_team = list(quest_results[rnd].keys())

    context = {
        'char_to_player': gameplay_data['character_to_player'],
        'round': str(int(cur_round)),
        'name': name, 
        'role': role, 
        'role_details': constants.role_details[role],
        'round_leader': round_leader,
        'round_team': cur_team,
        'previous_votes': previous_votes_str,
        'previous_results': previous_results,
        'previous_discussions': previous_discussions,
        'previous_summaries': previous_summaries
    }

    context_intent_guessing = get_context_for_intent_guessing(context)

    context_intnt_following_with_discussion = format_context_v2(
        context, constants.context_template, inclued_extra_role_details=True, include_discussion=True
    )

    context_reasonable = context_intnt_following_with_discussion

    all_intents = {'original': intents, 'modified': modified_intents}

    id_ = f"{gameplay_id}-{name.lower()}-{cur_round}"

    reasonable_intent = {
        'id': id_,
        'context': context_reasonable,
        'intents': intents,
        'reason': reason
    }

    formulation_con_intent_following = {
        'id': id_,
        'context': context_intnt_following_with_discussion,
        'intents': intents,
        'think': formulation_con_data['think'],
        'speak': formulation_con_data['speech']
    }

    refinement_con_intent_following = {
        'id': id_,
        'context': context_intent_guessing,
        'intents': modified_intents,
        'think': refinement_con_data['think'],
        'speak': refinement_con_data['speech']
    }
    
    
    complete_intent_following = get_summarization_data_point(
        id_, 
        all_intents, 
        formulation_con_data, 
        refinement_con_data, 
        context_intnt_following_with_discussion, 
        int_following_form, 
        int_following_ref
    )

    return reasonable_intent, formulation_con_intent_following, refinement_con_intent_following, complete_intent_following



def get_vote_results(results):
    vote_results = {}
    for rnd in rounds:
        for player in players:
            if rnd in results[player]:
                vote = results[player][rnd]['vote'][0]['vote_result']
                if rnd not in vote_results:
                    vote_results[rnd] = {}
                vote_results[rnd][player] = vote

    return vote_results


def is_intent_following_good(row, to_retain_player_rounds=None, for_guessing=False):
    if to_retain_player_rounds:
        player, round, is_secondary_round = row['player'], row['round'], row['is_secondary_round']
        key = (player, round, is_secondary_round)
        # print(key)

        if key not in to_retain_player_rounds:
            return False

    intent_fol_think_1, intent_fol_speech_1 = row['intent_fol_think_1'], row['intent_fol_speech_1']
    intent_fol_think_2, intent_fol_speech_2 = row['intent_fol_think_2'], row['intent_fol_speech_2']

    form_check = True
    ref_check = True

    if not for_guessing:
        for ele in intent_fol_think_1.split(','):
            if ele == 'nan':
                # form_check = False
                break
            if ele != '':
                if int(ele) < 3:
                    form_check = False
        
        for ele in intent_fol_speech_1.split(','):
            if ele == 'nan':
                # form_check = False
                break
            if ele != '':
                if int(ele) < 3:
                    form_check = False

        for ele in intent_fol_think_2.split(','):
            if ele == 'nan':
                # ref_check = False
                break
            if ele != '':
                if int(ele) < 3:
                    ref_check = False

    for ele in intent_fol_speech_2.split(','):
        if ele == 'nan':
            # ref_check = False
            break
        if ele != '':
            if int(ele) < 3:
                ref_check = False

    if for_guessing:
        return ref_check
    return form_check or ref_check


def convert_ann_to_num_list(ann):
    res = []
    for ele in ann.split(','):
        if ele == 'nan':
            return []
        if ele == '':
            return []
        res.append(int(ele))
    return res


def filter_out_non_impactful_rows(evaluation_df, annotation_df):

    for_guessing = True

    if 'is_secondary_round' not in evaluation_df:
        evaluation_df['is_secondary_round'] = False

        found_player_round = {}
        # setting secondary round to True for second occurence of the key, so first one will be set to False
        for idx, row in evaluation_df.iterrows():
            player, round = row['player'], row['round']
            key = (player, round)
            if key in found_player_round:
                evaluation_df.at[idx, 'is_secondary_round'] = True
            else:
                found_player_round[key] = True
 
        to_retain_player_rounds = {}
        for idx, row in annotation_df.iterrows():
            player, round, is_secondary_round = row['player'], row['round'], row['is_secondary_round']
            key = (player, round, is_secondary_round)
            if key not in to_retain_player_rounds:
                to_retain_player_rounds[key] = True

        evaluation_df_filtered = evaluation_df[evaluation_df.apply(lambda row: is_intent_following_good(row, to_retain_player_rounds, for_guessing=for_guessing), axis=1)]
    else:
        evaluation_df_filtered = evaluation_df[evaluation_df.apply(lambda row: is_intent_following_good(row, for_guessing=for_guessing), axis=1)]

    final_player_rounds = {}
    for idx, row in evaluation_df_filtered.iterrows():
        player, round, is_secondary_round = row['player'], row['round'], row['is_secondary_round']
        intent_fol_think_1, intent_fol_speech_1 = convert_ann_to_num_list(row['intent_fol_think_1']), convert_ann_to_num_list(row['intent_fol_speech_1'])
        intent_fol_think_2, intent_fol_speech_2 = convert_ann_to_num_list(row['intent_fol_think_2']), convert_ann_to_num_list(row['intent_fol_speech_2'])
        key = (player, round, is_secondary_round)
        if key not in final_player_rounds:
            final_player_rounds[key] = ((intent_fol_think_1, intent_fol_speech_1), (intent_fol_think_2, intent_fol_speech_2))

    return final_player_rounds


def read_data(gameplay_folder):
    game_ts = gameplay_folder.split("_")[-1]
    gameplay_data, results = {}, {}
    with open(gameplay_folder + '/results.json') as f:
        results = json.load(f)

    gp_file_name = 'game_play_data.json'
    annotation_file = None
    for x in os.listdir(gameplay_folder):
        if x.startswith('game_play_data'):
            gp_file_name = x
        if x.startswith('empty-'):
            annotation_file = x
    with open(gameplay_folder + f'/{gp_file_name}') as f:
        gameplay_data = json.load(f)
        
    if not annotation_file:
        annotation_file = f'annotation-{game_ts}.csv'
    evaluation_df = pd.read_csv(gameplay_folder + f'/annotation-{game_ts}.csv')
    annotation_df = pd.read_csv(gameplay_folder + f'/{annotation_file}')

    evaluation_df.dropna(subset=['intent_selection'])
    
    evaluation_df['intent_selection'] = evaluation_df['intent_selection'].astype(str).apply(lambda x: x.replace('.', ','))
    evaluation_df['intent_fol_think_1'] = evaluation_df['intent_fol_think_1'].astype(str).apply(lambda x: x.replace('.', ','))
    evaluation_df['intent_fol_speech_1'] = evaluation_df['intent_fol_speech_1'].astype(str).apply(lambda x: x.replace('.', ','))
    evaluation_df['intent_selection_mod'] = evaluation_df['intent_selection_mod'].astype(str).apply(lambda x: x.replace('.', ','))
    evaluation_df['intent_fol_think_2'] = evaluation_df['intent_fol_think_2'].astype(str).apply(lambda x: x.replace('.', ','))
    evaluation_df['intent_fol_speech_2'] = evaluation_df['intent_fol_speech_2'].astype(str).apply(lambda x: x.replace('.', ','))
    return gameplay_data, results, evaluation_df, annotation_df


reasonable_intent_data = []
form_con_intent_following_data = []
refine_con_intent_following_data = []
complete_intent_following_data = []


def process_results(gameplay_id, gameplay_data, results, final_player_rounds):
    vote_results = get_vote_results(results)
    for player in players:
        for rnd in rounds:
            if rnd in results[player]:
                is_secondary_round = False
                if int(rnd) > 10:
                    is_secondary_round = True
                key = (player, int(rnd) % 10, is_secondary_round)
                if key not in final_player_rounds:
                    continue
                # print(gameplay_id, rnd, player)
                reasonable_intent, form_con_intent_following, refine_con_intent_following, complete_intent_following = get_single_round_data(
                    gameplay_id,
                    rnd,
                    gameplay_data,
                    results[player][rnd],
                    results[player]['role'],
                    player,
                    results,
                    vote_results,
                    final_player_rounds[key][0],
                    final_player_rounds[key][1]
                )

                reasonable_intent_data.append(reasonable_intent)
                form_con_intent_following_data.append(form_con_intent_following)
                refine_con_intent_following_data.append(refine_con_intent_following)
                complete_intent_following_data.extend(complete_intent_following)


if __name__ == "__main__":
    ANNOTATED_GAMES_PATH = config_utils.get_config_value("annotated_data_save_path")
    SAVE_FOLDER = config_utils.get_config_value("structured_context_save_path")

    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    if not os.path.exists(f"{SAVE_FOLDER}/summarization_data"):
        os.makedirs(f"{SAVE_FOLDER}/summarization_data")
    if not os.path.exists(f"{SAVE_FOLDER}/guessing_data"):
        os.makedirs(f"{SAVE_FOLDER}/guessing_data")

    experiment_folders = []

    for x in os.listdir(ANNOTATED_GAMES_PATH):
        if x.startswith('game_') and os.path.isdir(os.path.join(ANNOTATED_GAMES_PATH, x)):
            experiment_folders.append(os.path.join(ANNOTATED_GAMES_PATH, x))

    for folder in experiment_folders:
        print(folder)
        gameplay_data, results, evaluation_df, annotation_df = read_data(folder)
        final_player_rounds = filter_out_non_impactful_rows(evaluation_df, annotation_df)
        process_results(folder.split('/')[-1], gameplay_data, results, final_player_rounds)

    # impactful intents
    refine_con_intent_following_impactful_data = []
    intent_count = 0
    for data in refine_con_intent_following_data:
        intents = data['intents']
        filtered_intents = []
        for intent in intents:
            if intent not in constants.impactful_intents:
                continue
            filtered_intents.append(intent)
        final_data = data.copy()
        final_data['intents'] = filtered_intents
        if len(filtered_intents) == 0:
            continue
        refine_con_intent_following_impactful_data.append(final_data)
        intent_count += len(filtered_intents)

    SUFFIX = "_all"

    save_data(reasonable_intent_data, f"{SAVE_FOLDER}/reasonable_intent{SUFFIX}.json")
    save_data(form_con_intent_following_data, f"{SAVE_FOLDER}/frm_con_intent_following{SUFFIX}.json")
    save_data(refine_con_intent_following_data, f"{SAVE_FOLDER}/guessing_data/intent_guessing{SUFFIX}.json")
    save_data(complete_intent_following_data, f"{SAVE_FOLDER}/summarization_data/intent_summarization{SUFFIX}.json")

    refine_con_intent_following_df = pd.DataFrame(refine_con_intent_following_impactful_data)
    refine_con_intent_following_df = refine_con_intent_following_df.drop(['think'], axis=1)

    refine_con_intent_following_df.to_csv(f"{SAVE_FOLDER}/guessing_data/intent_guessing{SUFFIX}_impactful.csv", index=False)
    save_data(refine_con_intent_following_impactful_data, f"{SAVE_FOLDER}/guessing_data/intent_guessing{SUFFIX}_impactful.json")

    refine_con_intent_following_without_intents_df = refine_con_intent_following_df.drop(['intents'], axis=1)

    refine_con_intent_following_without_intents_df.to_csv(
        f"{SAVE_FOLDER}/guessing_data/intent_guessing_without_intent{SUFFIX}_impactful.csv", index=False)

    complete_intent_following_df = pd.DataFrame(complete_intent_following_data)
    complete_intent_following_df.head()

    complete_intent_following_df.to_csv(f"{SAVE_FOLDER}/summarization_data/intent_summarization{SUFFIX}.csv", index=False)

    complete_intent_following_without_intents_df = complete_intent_following_df.drop(['intents'], axis=1)
    complete_intent_following_without_intents_df.head()

    complete_intent_following_without_intents_df.to_csv(
        f"{SAVE_FOLDER}/summarization_data/intent_summarization_without_intent{SUFFIX}.csv", index=False)

    print(f"Data saved to {SAVE_FOLDER}")




