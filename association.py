from torchmetrics.nominal import TheilsU
import torch
_ = torch.manual_seed(0)
preds = torch.randint(2, (10,))
target = torch.randint(2, (10,))
metric = TheilsU(num_classes=2)
print(metric(preds, target))

import json
json_data=json.load(open('output/gpt-3-5-turbo-0125/annotated_game_files_data.json', 'r'))
loyal=['Servant','Merlin','Percival']
evil=['Morgana','Assassin']
evil_quest_result=[]
evil_intention_selection=[]
loyal_quest_results=[]
loyal_intention_selections=[]
loyal_intention_followings=[]
for game in json_data:
    print(game)
    for round in json_data[game]:
        print(round)
        if round=='round_winning_side':
            break
        first_half=json_data[game][round]['primary']
        
        first_result=0 if first_half['quest_result']=='failure' else 1
          
        loyal_quest_results.append(first_result)
        loyal_player_number=0
        loyal_player_selection=0
        evil_player_number=0
        evil_player_selection=0
        loyal_intention_following=0
        evil_intention_following=0
        for player_name in first_half['turns']:
            if player_name in loyal:
                loyal_player_number+=1
                intent_selection_mod=first_half['turns'][player_name]['intent_selection_mod']
                intention_follow_speech=first_half['turns'][player_name]['intent_fol_speech_2']
                if intention_follow_speech==['nan']:
                        continue
                if intent_selection_mod==['nan']:
                    continue
                for index,selection in enumerate(intent_selection_mod):
                    if selection=='nan':
                        continue
                    if int(intention_follow_speech[index])>=3:
                        loyal_player_selection+=int(selection)
                for index,following in enumerate(intention_follow_speech):
                    if int(intent_selection_mod[index])==1:
                        loyal_intention_following+=int(following)
            if player_name in evil:
                evil_player_number+=1
                intent_selection_mod=first_half['turns'][player_name]['intent_selection_mod']
                intention_follow_speech=first_half['turns'][player_name]['intent_fol_speech_2']
                if intention_follow_speech==['nan']:
                        continue
                if intent_selection_mod==['nan']:
                    continue
                for index,selection in enumerate(intent_selection_mod):
                    if selection=='nan':
                        continue
                    if int(intention_follow_speech[index])>=3:
                        evil_player_selection+=int(selection)
                for index,following in enumerate(intention_follow_speech):
                    if int(intent_selection_mod[index])==1:
                        evil_intention_following+=int(following)
        if 'secondary' in json_data[game][round]:
            second_half=json_data[game][round]['secondary']
            for player_name in second_half['turns']:
                if player_name in loyal:
                    loyal_player_number+=1
                    intent_selection_mod=second_half['turns'][player_name]['intent_selection_mod']
                    intention_follow_speech=second_half['turns'][player_name]['intent_fol_speech_2']
                    if intention_follow_speech==['nan']:
                        continue
                    if intent_selection_mod==['nan']:
                        continue
                    for index,selection in enumerate(intent_selection_mod):
                        if selection=='nan':
                            continue
                        if int(intention_follow_speech[index])>=3:
                            loyal_player_selection+=int(selection)
                    for index,following in enumerate(intention_follow_speech):
                        if int(intent_selection_mod[index])==1:
                            loyal_intention_following+=int(following)
                if player_name in evil:
                    evil_player_number+=1
                    intent_selection_mod=second_half['turns'][player_name]['intent_selection_mod']
                    intention_follow_speech=second_half['turns'][player_name]['intent_fol_speech_2']
                    if intention_follow_speech==['nan']:
                        continue
                    if intent_selection_mod==['nan']:
                        continue
                    for index,selection in enumerate(intent_selection_mod):
                        if selection=='nan':
                            continue
                        if int(intention_follow_speech[index])>=3:
                                 evil_player_selection+=int(selection)
                    for index,following in enumerate(intention_follow_speech):
                        if int(intent_selection_mod[index])==1:
                            evil_intention_following+=int(following)
        if loyal_player_number==0:
            loyal_ratio=0
        else:
            loyal_ratio=loyal_player_selection/loyal_player_number
            loyal_following_ratio=loyal_intention_following/loyal_player_number
        if evil_player_number==0:
            evil_ratio=0
        else:
            evil_ratio=evil_player_selection/evil_player_number
            evil_following_ratio=evil_intention_following/evil_player_number

        loyal_selection_result=0 if loyal_ratio<evil_ratio else 1
        loyal_following_result=0 if loyal_following_ratio<evil_following_ratio else 1
        loyal_intention_selections.append(loyal_selection_result)
        loyal_intention_followings.append(loyal_following_result)
print(metric(torch.tensor(loyal_intention_selections), torch.tensor(loyal_quest_results)))
print(metric(torch.tensor(loyal_intention_followings), torch.tensor(loyal_quest_results)))
