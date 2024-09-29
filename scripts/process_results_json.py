import json
from collections import Counter

import config_utils


def read_data(file_path):
    with open(file_path) as f:
        data = json.loads(f.read())
    return data


def process_game(game_data):
    round_keys = ["round" + str(num) for num in range(1, 6)]
    round_types = ["primary", "secondary"]

    int_sel = {key: [] for key in round_keys}
    # int_sel_mod = []
    int_fol_think = {key: [] for key in round_keys}
    int_fol_speech = {key: [] for key in round_keys}

    mod_count = 0

    for rnd in round_keys:
        if rnd in game_data:
            rnd_data = game_data[rnd]
            for round_type in round_types:
                if round_type in rnd_data:
                    turns_data = rnd_data[round_type]["turns"]
                    for key, player_data in turns_data.items():
                        player_int_sel = [int(val) for val in player_data["intent_selection"] if val != "nan"]

                        player_int_fol_think_1 = [int(val) for val in player_data["intent_fol_think_1"] if val != "nan"]
                        player_int_fol_speech_1 = [int(val) for val in player_data["intent_fol_speech_1"] if
                                                   val != "nan"]

                        player_int_fol_think = []
                        player_int_fol_think.extend(player_int_fol_think_1)

                        player_int_fol_speech = []
                        player_int_fol_speech.extend(player_int_fol_speech_1)

                        if len(player_data["intent_mod"]) != 0:
                            player_int_fol_think_2 = [int(val) for val in player_data["intent_fol_think_2"] if
                                                      val != "nan"]
                            player_int_fol_speech_2 = [int(val) for val in player_data["intent_fol_speech_2"] if
                                                       val != "nan"]

                            player_int_fol_think.extend(player_int_fol_think_2)
                            player_int_fol_speech.extend(player_int_fol_speech_2)

                            selected_intents = set(player_data["intent"])
                            mod_intents = set(player_data["intent_mod"])

                            if selected_intents != mod_intents:
                                mod_count += 1
                                player_int_sel_mod = [int(val) for val in player_data["intent_selection_mod"]]
                                player_int_sel.extend(player_int_sel_mod)

                        int_sel[rnd].extend(player_int_sel)
                        int_fol_think[rnd].extend(player_int_fol_think)
                        int_fol_speech[rnd].extend(player_int_fol_speech)

    return int_sel, int_fol_think, int_fol_speech


def process_all_data(data):
    round_keys = ["round" + str(num) for num in range(1, 6)]

    all_int_sel = {key: [] for key in round_keys}
    all_int_fol_think = {key: [] for key in round_keys}
    all_int_fol_speech = {key: [] for key in round_keys}

    all_int_sel_agg = []
    all_int_fol_think_agg = []
    all_int_fol_speech_agg = []

    all_int_fol_agg = []

    for key, game_data in data.items():

        int_sel, int_fol_think, int_fol_speech = process_game(game_data)

        for rnd in round_keys:
            if rnd in int_sel:
                all_int_sel[rnd].extend(int_sel[rnd])
                all_int_fol_think[rnd].extend(int_fol_think[rnd])
                all_int_fol_speech[rnd].extend(int_fol_speech[rnd])

                all_int_sel_agg.extend(int_sel[rnd])
                all_int_fol_think_agg.extend(int_fol_think[rnd])
                all_int_fol_speech_agg.extend(int_fol_speech[rnd])

                all_int_fol_agg.extend(int_fol_think[rnd])
                all_int_fol_agg.extend(int_fol_speech[rnd])

    int_sel_counters = {}
    for rnd in round_keys:
        rnd_int_sel_counter = Counter(all_int_sel[rnd])
        int_sel_counters[rnd] = rnd_int_sel_counter
        print(rnd, [(i, rnd_int_sel_counter[i] / len(all_int_sel[rnd])) for i in rnd_int_sel_counter],
              len(all_int_sel[rnd]))

    int_fol_think_counters = {}
    for rnd in round_keys:
        rnd_int_fol_think_counter = Counter(all_int_fol_think[rnd])
        int_fol_think_counters[rnd] = rnd_int_fol_think_counter

    int_fol_speech_counters = {}
    for rnd in round_keys:
        rnd_int_fol_speech_counter = Counter(all_int_fol_speech[rnd])
        int_fol_speech_counters[rnd] = rnd_int_fol_speech_counter

    print("All rounds results")
    all_int_sel_counter = Counter(all_int_sel_agg)
    all_int_fol_think_counter = Counter(all_int_fol_think_agg)
    all_int_fol_speech_counter = Counter(all_int_fol_speech_agg)

    all_int_fol_counter = Counter(all_int_fol_agg)

    print([(i, all_int_sel_counter[i] / len(all_int_sel_agg)) for i in all_int_sel_counter], len(all_int_sel_agg))
    print([(i, all_int_fol_think_counter[i] / len(all_int_fol_think_agg)) for i in all_int_fol_think_counter],
          len(all_int_fol_think_agg))
    print([(i, all_int_fol_speech_counter[i] / len(all_int_fol_speech_agg)) for i in all_int_fol_speech_counter],
          len(all_int_fol_speech_agg))

    print([(i, all_int_fol_counter[i] / len(all_int_fol_agg)) for i in all_int_fol_counter], len(all_int_fol_agg))


if __name__ == '__main__':
    ANNOTATED_DATA_PATH = f"{config_utils.get_config_value('annotated_data_save_path')}/annotated_game_files_data.json"

    data = read_data(ANNOTATED_DATA_PATH)
    process_all_data(data)
