from __future__ import print_function

import os
from ast import literal_eval
from collections import defaultdict

import pandas as pd
from krippendorff import alpha
from statsmodels.stats import inter_rater as irr
from statsmodels.stats.inter_rater import fleiss_kappa

try:
    import numpy as np
except ImportError:
    np = None

def read_data_files(files):
    dfs = {}
    for file in files:
        print(file)
        df = pd.read_csv(file)
        df.dropna(subset=["intent_selection"])
        df['intent'] = df['intent'].astype(str)
        df['intent_mod'] = df['intent_mod'].astype(str)
        df['intent'] = df['intent'].apply(lambda x: literal_eval(x))
        df['intent_mod'] = df['intent_mod'].apply(lambda x: literal_eval(x))
        df['intent_selection'] = df['intent_selection'].astype(str).apply(lambda x: x.replace('.', ','))
        df['intent_fol_think_1'] = df['intent_fol_think_1'].astype(str).apply(lambda x: x.replace('.', ','))
        df['intent_fol_speech_1'] = df['intent_fol_speech_1'].astype(str).apply(lambda x: x.replace('.', ','))
        df['intent_selection_mod'] = df['intent_selection_mod'].astype(str).apply(lambda x: x.replace('.', ','))
        df['intent_fol_think_2'] = df['intent_fol_think_2'].astype(str).apply(lambda x: x.replace('.', ','))
        df['intent_fol_speech_2'] = df['intent_fol_speech_2'].astype(str).apply(lambda x: x.replace('.', ','))
        # dfs.append(df)
        name = file.split('/')[-2]
        dfs[name] = df


    def store_in_dic_form(row, ann):
        key = (row['player'], row['round'], row['is_secondary_round'])
        ann_int_sel[ann][key] = [val for val in row['intent_selection'].split(',') if val != '']
        ann_int_fol1[ann][key] = [val for val in row['intent_fol_think_1'].split(',') if val != '']
        ann_int_spk1[ann][key] = [val for val in row['intent_fol_speech_1'].split(',') if val != '']


    def store_in_dic_ref(row, ann):
        key = (row['player'], row['round'], row['is_secondary_round'])
        ann_int_sel[ann][key] = [val for val in row['intent_selection_mod'].split(',') if val != '']
        ann_int_fol1[ann][key] = [val for val in row['intent_fol_think_2'].split(',') if val != '']
        ann_int_spk1[ann][key] = [val for val in row['intent_fol_speech_2'].split(',') if val != '']


    ann_int_sel = {f'ann{idx+1}': {} for idx in range(len(dfs))}
    ann_int_fol1 = {f'ann{idx+1}': {} for idx in range(len(dfs))}
    ann_int_spk1 = {f'ann{idx+1}': {} for idx in range(len(dfs))}

    for idx, (key, df) in enumerate(dfs.items()):
        df.apply(lambda row: store_in_dic_form(row, f'ann{idx+1}'), axis=1)

    int_sel_anns = []
    for key in ann_int_sel['ann1'].keys():
        ann_vals = []
        found_nan = False
        for ann_key, ann_val in ann_int_sel.items():
            val = ann_val[key]
            if val[0] == 'nan':
                found_nan = True
                break
            val_int = [int(x) for x in val]
            ann_vals.append(val_int)

        if found_nan:
            continue

        for annotations in zip(*ann_vals):
            int_sel_anns.append(annotations)

    int_fol_think_anns = []
    for key in ann_int_fol1['ann1'].keys():
        ann_vals = []
        found_nan = False
        for ann_key, ann_val in ann_int_fol1.items():
            val = ann_val[key]
            if val[0] == 'nan' or val[0] == '':
                found_nan = True
                break
            
            val_int = [int(x) for x in val]
            val_int = [1 if x > 3 else 0 for x in val_int]
            ann_vals.append(val_int)

        if found_nan:
            continue

        for annotations in zip(*ann_vals):
            int_fol_think_anns.append(annotations)

    int_fol_sp_anns = []
    for key in ann_int_spk1['ann1'].keys():
        ann_vals = []
        found_nan = False
        for ann_key, ann_val in ann_int_spk1.items():
            val = ann_val[key]
            if val[0] == 'nan' or val[0] == '':
                found_nan = True
                break
            val_int = [int(x) for x in val]
            val_int = [1 if x > 3 else 0 for x in val_int]
            ann_vals.append(val_int)

        if found_nan:
            continue
        
        for annotations in zip(*ann_vals):
            int_fol_sp_anns.append(annotations)
        
 
    return int_sel_anns, int_fol_think_anns, int_fol_sp_anns


def convert_to_df(data):
    data_dict = {
        'doc_id': [],
        'ann_id': [],
        'annot': []
    }
    for idx, (x, y) in enumerate(data):
        data_dict['doc_id'].append(idx)
        data_dict['doc_id'].append(idx)
        data_dict['ann_id'].append(0)
        data_dict['ann_id'].append(1)
        data_dict['annot'].append(x)
        data_dict['annot'].append(y)

    return pd.DataFrame(data_dict)


def nominal_metric(a, b):
    return a != b

def interval_metric(a, b):
    return (a-b)**2

def ratio_metric(a, b):
    return ((a-b)/(a+b))**2


if __name__ == '__main__':

    file_pairs = defaultdict(list)

    ANNOTATED_RESULTS_PATH = '../output/annotator_agreement_files'

    for d in os.listdir(ANNOTATED_RESULTS_PATH):
        annotator = d
        folder = f"{ANNOTATED_RESULTS_PATH}/{annotator}"
        for x in os.listdir(folder):
            if x.startswith('annotation'):
                game = x.split('_')[0]
                file_pairs[game].append(f"{folder}/{x}")

    int_sel_total, int_fol_think_total, int_fol_sp_total  = [], [], []
    for files in file_pairs.values():
        int_sel_anns, int_fol_think_anns, int_fol_sp_anns = read_data_files(files)
        int_sel_total.extend(int_sel_anns)
        int_fol_think_total.extend(int_fol_think_anns)
        int_fol_sp_total.extend(int_fol_sp_anns)

    # print(int_sel_total[5:10], len(int_sel_total))
    uniq_ann = defaultdict(int)
    for items in int_fol_think_total:
        uniq_ann[items] += 1


    int_sel_total_np = np.array(int_sel_total).transpose()
    alpha_value = alpha(int_sel_total_np, value_domain=[1,0])
    print(f"Intent selection: Krippendorff's Alpha: {alpha_value:.3f}")

    agg = irr.aggregate_raters(int_sel_total)
    kappa = fleiss_kappa(agg[0])
    print(f"Fleiss' kappa: {kappa}")

    int_fol_think_total_np = np.array(int_fol_think_total).transpose()
    alpha_value = alpha(int_fol_think_total_np, level_of_measurement='ordinal')
    print(f"Intent following think: Krippendorff's Alpha: {alpha_value:.3f}")
    
    agg = irr.aggregate_raters(int_fol_think_total)
    kappa = fleiss_kappa(agg[0])
    print(f"Fleiss' kappa: {kappa}")

    int_fol_sp_total_np = np.array(int_fol_sp_total).transpose()
    alpha_value = alpha(int_fol_sp_total_np, level_of_measurement='ordinal')
    print(f"Intent following speak: Krippendorff's Alpha: {alpha_value:.3f}")

    agg = irr.aggregate_raters(int_fol_sp_total)
    kappa = fleiss_kappa(agg[0])
    print(f"Fleiss' kappa: {kappa}")