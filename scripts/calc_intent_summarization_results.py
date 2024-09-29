import json
from ast import literal_eval
import config_utils

import pandas as pd
import re

import utils
from constants import similar_intent_map

uniq_intents = set(similar_intent_map.values())
for intent in uniq_intents:
    if intent not in similar_intent_map:
        similar_intent_map[intent] = intent

intent_stats_dic = {}


def calc_intent_stats(summarized_intents, selected_intents):
    for intent in summarized_intents:
        if intent not in intent_stats_dic:
            intent_stats_dic[intent] = {'count': 0, 'summary': 0, 'selection': 0, 'both': 0}
        intent_stats_dic[intent]['count'] += 1
        intent_stats_dic[intent]['summary'] += 1
        if intent in selected_intents:
            intent_stats_dic[intent]['selection'] += 1
            intent_stats_dic[intent]['both'] += 1

    for intent in selected_intents:
        if intent not in intent_stats_dic:
            intent_stats_dic[intent] = {'count': 0, 'summary': 0, 'selection': 0, 'both': 0}
        if intent not in summarized_intents:
            intent_stats_dic[intent]['count'] += 1
            intent_stats_dic[intent]['selection'] += 1


def clean_annotation(annotation):
    # sy
    split_intents = annotation.split('\n')
    summarized_intents = []
    for line in split_intents:
        summarized_intents.extend(
            [utils.remove_non_alphabets(val.split('. ')[-1]) for val in line.split(",") if val.strip() != ""])
    summarized_intents_final = []
    for intent in summarized_intents:
        split_intents = intent.strip().split("  ")
        split_intents = [i.strip() for i in split_intents]
        summarized_intents_final.extend(split_intents)

    return ','.join(summarized_intents_final)


def clean_annotation_v2(annotation):
    # javin
    summarized_intents = [utils.remove_non_alphabets(intent.split('. ')[-1]) for intent in annotation.split('\n')]
    summarized_intents_final = []
    for intent in summarized_intents:
        split_intents = intent.strip().split("  ")
        split_intents = [i.strip() for i in split_intents]
        summarized_intents_final.extend(split_intents)
    return ','.join(summarized_intents_final)


def clean_annotation_v3(annotation):
    # deepayan
    summarized_intents = [utils.remove_non_alphabets(intent).strip() for intent in annotation.split('\n')]
    return ','.join(summarized_intents)


def clean_annotation_v4(annotation):
    # just comma separated
    if type(annotation) != str:
        return ''
    split_intents = re.split(',', annotation)
    sum_intents = []
    for line in split_intents:
        if len(line) > 10:
            processed_intent = utils.remove_non_alphabets(line.strip())
            sum_intents.append(processed_intent)

    return ','.join(sum_intents)


def compute_human_results(preds_file, gold_label_file):
    summarization_annotated_df = pd.read_csv(preds_file)
    summarization_annotated_df['summarized_intents'] = summarization_annotated_df['summarized_intents'].apply(
        lambda x: clean_annotation_v4(x))
    summarization_annotated_df = summarization_annotated_df.dropna(subset=["id"])

    all_samples_df = pd.read_csv(gold_label_file)
    annotation_results = summarization_annotated_df[['id', 'summarized_intents']].values.tolist()

    all_data = all_samples_df[['id', 'intents']].values.tolist()

    all_data_dic = {key: literal_eval(intents) for key, intents in all_data}

    annotated_samples = []
    for r in annotation_results:
        if r[0] not in all_data_dic:
            continue
        data = {}
        data['id'] = r[0]
        data['intents'] = all_data_dic[r[0]]
        split_intents = r[1].split('\n')
        data['summarized_intents'] = r[1].split(',')
        annotated_samples.append(data)

    results = []
    for sample in annotated_samples:
        if 'summarized_intents' not in sample:
            print('not found')
            continue
        intents = [utils.remove_non_alphabets(intent) for intent in sample['intents']]
        intents = [similar_intent_map[intent] for intent in intents if intent in similar_intent_map]
        summarized_intents = [similar_intent_map[utils.remove_non_alphabets(intent)] for intent in
                              sample['summarized_intents'] if utils.remove_non_alphabets(intent) in similar_intent_map]

        results.append({'summarized_intents': summarized_intents, 'intents': intents})

    count_sum, count_sel = 0, 0
    for r in results:
        count_sum += len(r['summarized_intents'])
        count_sel += len(r['intents'])

    intent_stats_dic = {}
    for res in results:
        calc_intent_stats(res['summarized_intents'], res['intents'])

    total_selection_count = 0
    selection_in_summary_count = 0
    total_summary_count = 0
    for key, value in intent_stats_dic.items():
        total_selection_count += value['selection']
        selection_in_summary_count += value['both']
        total_summary_count += value['summary']

    recall = selection_in_summary_count / total_selection_count
    precision = selection_in_summary_count / total_summary_count

    print(utils.calculate_f1_score(recall, precision))


def compute_model_results(preds_file):

    with open(preds_file) as f:
        data = json.load(f)
    samples = list(data.values())

    samples_list = []
    total_sum_intents = 0
    total_sel_intents = 0
    for s in samples:
        if 'summarized_intents' not in s:
            continue
        total_sum_intents += len(s['summarized_intents'])
        total_sel_intents += len(s['intents'])
        samples_list.append([s['id'], s['summarized_intents'], s['intents']])

    uniq_sum_intents = []
    for ann in samples_list:
        for intent in ann[1]:
            intent = utils.remove_non_alphabets(intent)
            uniq_sum_intents.append(intent)

    count = 0
    for intent in uniq_sum_intents:
        if intent not in similar_intent_map.keys():
            print(intent)
            count += 1

    annotated_samples = []
    missing_count = 0
    for r in samples_list:
        data = {}
        data['intents'] = r[2]
        # split_intents = r[1].split('\n')

        data['summarized_intents'] = [similar_intent_map[utils.remove_non_alphabets(intent)] for intent in r[1] if
                                      utils.remove_non_alphabets(intent) in similar_intent_map]
        if len(data['summarized_intents']) != len(r[1]):
            print(len(data['summarized_intents']) - len(r[1]))
        annotated_samples.append(data)

    results = []
    for sample in annotated_samples:
        intents = [similar_intent_map[utils.remove_non_alphabets(intent)] for intent in sample['intents'] if
                   utils.remove_non_alphabets(intent) in similar_intent_map]
        summarized_intents = [utils.remove_non_alphabets(intent) for intent in sample['summarized_intents']]

        results.append({'summarized_intents': summarized_intents, 'intents': intents})

    intent_stats_dic = {}
    for res in results:
        calc_intent_stats(res['summarized_intents'], res['intents'])

    total_selection_count = 0
    selection_in_summary_count = 0
    total_summary_count = 0
    for key, value in intent_stats_dic.items():
        total_selection_count += value['selection']
        selection_in_summary_count += value['both']
        total_summary_count += value['summary']

    recall = selection_in_summary_count / total_selection_count
    precision = selection_in_summary_count / total_summary_count

    print(utils.calculate_f1_score(recall, precision))


if __name__ == '__main__':
    HUMAN_PREDS = f"{config_utils.get_config_value('structured_context_save_path')}/summarization_annotations/intent_summarization_gpt4_without_intent_50_Abhi.csv"
    MODEL_PREDS = f"{config_utils.get_config_value('structured_context_save_path')}/summarization_model_results/intent_summarization_all_results.json"
    GOLD_LABEL_FILE_HUMAN = f"{config_utils.get_config_value('structured_context_save_path')}/structured_context_files/intent_summarization_gpt4_50.csv"

    compute_human_results(HUMAN_PREDS, GOLD_LABEL_FILE_HUMAN)
    compute_model_results(MODEL_PREDS)
