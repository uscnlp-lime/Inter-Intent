from ast import literal_eval
from collections import defaultdict

import pandas as pd
from sentence_transformers import SentenceTransformer, util
from tqdm import notebook

import config_utils
from constants import similar_intent_map
import utils

# Load a pre-trained sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

orig_intents = set(similar_intent_map.values())

orig_intents_embs = {}
for intent in orig_intents:
    orig_intents_embs[intent] = model.encode(intent)

intent_stats_dic = {}

def insert_phrase(sentence):
    max_score = 0
    max_score_intent = ''
    for intent in orig_intents:
        # Generate embeddings
        embeddings1 = model.encode(sentence)
        embeddings2 = orig_intents_embs[intent]

        # Compute cosine similarity
        similarity = util.cos_sim(embeddings1, embeddings2)
        if similarity > max_score:
            max_score = similarity
            max_score_intent = intent

    if max_score >= 0.6:
        similar_intent_map[sentence] = max_score_intent


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


def get_results(samples_list):
    results = []
    for r in samples_list:
        intents = [utils.remove_non_alphabets(intent) for intent in r[1]]
        intents = [similar_intent_map[intent] for intent in intents if intent in similar_intent_map]
        guessed_intents = [similar_intent_map[utils.remove_non_alphabets(intent)] for intent in r[2] if
                           utils.remove_non_alphabets(intent) in similar_intent_map]

        results.append({'guessed_intents': guessed_intents, 'intents': intents})

    for res in results:
        calc_intent_stats(res['guessed_intents'], res['intents'])

    total_selection_count = 0
    selection_in_summary_count = 0
    total_summary_count = 0
    for key, value in intent_stats_dic.items():
        total_selection_count += value['selection']
        selection_in_summary_count += value['both']
        total_summary_count += value['summary']
    recall = selection_in_summary_count / total_selection_count
    precision = selection_in_summary_count / total_summary_count
    f1score = utils.calculate_f1_score(recall, precision)
    return f1score, recall, precision


def clean_annotation(annotation):
    if (type(annotation) != str):
        return ''
    split_intents = utils.re.split(r"\d[.]+|\n", annotation)
    guessed_intents = []
    for line in split_intents:
        if len(line) > 10:
            processed_intent = utils.remove_non_alphabets(line.strip())
            guessed_intents.append(processed_intent)

    guessed_intents_final = []
    for intent in guessed_intents:
        split_intents = intent.strip().split("  ")
        split_intents = [i.strip() for i in split_intents]
        guessed_intents_final.extend(split_intents)

    return ','.join(guessed_intents_final)


def clean_annotation_v2(annotation):
    if (type(annotation) != str):
        return ''
    split_intents = utils.re.split(',', annotation)
    guessed_intents = []
    for line in split_intents:
        if len(line) > 10:
            processed_intent = utils.remove_non_alphabets(line.strip())
            guessed_intents.append(processed_intent)

    return ','.join(guessed_intents)


def compute_human_results(preds_file, gold_label_file):

    guessing_annotated_df = pd.read_csv(preds_file)

    guessing_gold_df = pd.read_csv(gold_label_file)

    guessing_annotated_df['guessed_intents'] = guessing_annotated_df['Unnamed: 3'].apply(lambda x: clean_annotation_v2(x))
    guessing_annotated_df.head()

    guessing_gold_data = guessing_gold_df[['id', 'intents']].values.tolist()
    guessing_gold_data_dic = {key: literal_eval(intents) for key, intents in guessing_gold_data}

    guessing_annotated_df = guessing_annotated_df.dropna(subset=["id"])

    annotation_results = guessing_annotated_df[['id', 'guessed_intents']].values.tolist()
    annotated_samples = []
    for r in annotation_results:
        if r[0] not in guessing_gold_data_dic:
            continue
        data = {}
        data['id'] = r[0]
        data['intents'] = guessing_gold_data_dic[r[0]]
        data['guessed_intents'] = r[1].split(',')
        annotated_samples.append(data)

    results = []
    for sample in annotated_samples:
        if 'guessed_intents' not in sample:
            continue
        intents = [utils.remove_non_alphabets(intent) for intent in sample['intents']]
        intents = [similar_intent_map[intent] for intent in intents if intent in similar_intent_map]
        summarized_intents = [utils.remove_non_alphabets(intent) for intent in sample['guessed_intents'] if intent != '']

        results.append({'guessed_intents': summarized_intents, 'intents': intents})

    intent_stats_dic = {}
    for res in results:
        calc_intent_stats(res['guessed_intents'], res['intents'])

    total_selection_count = 0
    selection_in_summary_count = 0
    total_summary_count = 0
    for key, value in intent_stats_dic.items():
        total_selection_count += value['selection']
        selection_in_summary_count += value['both']
        total_summary_count += value['summary']

    recall = selection_in_summary_count / total_selection_count

    precision = selection_in_summary_count / total_summary_count

    utils.calculate_f1_score(recall, precision)

    samples_list = []
    total_sel = 0
    total_guessed = 0
    for s in annotated_samples:
        if 'guessed_intents' in s:
            total_sel += len(s['intents'])
            total_guessed += len(s['guessed_intents'])
            samples_list.append([s['id'], s['intents'], s['guessed_intents']])

    rounds = defaultdict(list)
    for item in samples_list:
        round_no = int(item[0].split('-')[-1]) % 10
        rounds[round_no].append(item)

    for rnd in sorted(rounds.keys()):
        intent_stats_dic = {}
        f1score, recall, precision = get_results(rounds[rnd])
        f1score, recall, precision = f1score, recall * 100, precision * 100
        print(f"Round: {rnd} => {f1score=:.2f}")


def compute_model_results(preds_file, gold_label_file):

    with open(preds_file) as f:
        data = utils.json.load(f)
    samples = list(data.values())

    with open(gold_label_file) as f:
        first_order_data = utils.json.load(f)

    for sample in samples:
        first_order_intents = first_order_data[sample['id']]['guessed_intents']
        sample['first_order_intents'] = first_order_intents

    samples_list = []
    total_sel = 0
    total_guessed = 0
    for s in samples:
        if 'guessed_intents' in s:
            total_sel += len(s['first_order_intents'])
            total_guessed += len(s['guessed_intents'])
            samples_list.append([s['id'], s['first_order_intents'], s['guessed_intents']])

    uniq_sum_intents = []
    for ann in samples_list:
        for intent in ann[2]:
            intent = utils.remove_non_alphabets(intent)
            uniq_sum_intents.append(intent)

    count = 0
    rephrased_intents = set()
    for intent in uniq_sum_intents:
        if intent not in similar_intent_map:
            count += 1
            rephrased_intents.add(intent)

    for rephrased_intent in notebook.tqdm(rephrased_intents):
        insert_phrase(rephrased_intent)

    intent_stats_dic = {}
    get_results(samples_list)

    rounds = defaultdict(list)
    for item in samples_list:
        round_no = int(item[0].split('-')[-1]) % 10
        rounds[round_no].append(item)

    for rnd in sorted(rounds.keys()):
        intent_stats_dic = {}
        f1score, recall, precision = get_results(rounds[rnd])
        f1score, recall, precision = f1score, recall * 100, precision * 100
        print(f"Round: {rnd} => {f1score=:.2f}")


if __name__ == '__main__':
    HUMAN_PREDS = f"{config_utils.get_config_value('structured_context_save_path')}/guessing_annotations/intent_guessing_gpt4_without_intents_50_Ziyi.csv"
    MODEL_PREDS = f"{config_utils.get_config_value('structured_context_save_path')}/guessing_model_results/intent_guessing_second_order_5_games_results.json"
    GOLD_LABEL_FILE_HUMAN = f"{config_utils.get_config_value('structured_context_save_path')}/structured_context_files/intent_guessing_gpt4_50.csv"
    GOLD_LABEL_FILE_MODEL = f"{config_utils.get_config_value('structured_context_save_path')}/guessing_model_results/intent_guessing_results.json"

    compute_human_results(HUMAN_PREDS, GOLD_LABEL_FILE_HUMAN)
    compute_model_results(MODEL_PREDS, GOLD_LABEL_FILE_MODEL)
