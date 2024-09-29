from scripts import config_utils, utils
from chatarena.agent import Player
from chatarena.backends import OpenAIChat,LLamaChat
from chatarena.message import Message, MessagePool
from chatarena.environments.base import TimeStep, Environment
from typing import List, Union
from chatarena.arena import Arena
from prompts import Role_tips, game_description, Moderator_speech, intents, format_control, \
    format_control_schemas, intent_categories, Moderator_remember_speech, intents_total
import string
import sys
import datetime
import pandas as pd
import os
import json
import random

characters = string.ascii_letters + string.digits
folder_name = 'output/' + 'game_' + str(datetime.datetime.now().date()) + '-' + str(datetime.datetime.now().hour) + '-' + str(
    datetime.datetime.now().minute) + '-' + str(datetime.datetime.now().second)
file_name = folder_name + '/conversation'
USE_LLAMA = False
USE_INTENT_CATEGORY = False
USE_INTENT_GENERATION = False
USE_INTENT_EVAL = False

# f=open('output/'+filename+'.txt','w+')


class Avalon(Environment):
    type_name = 'Avalon'

    def __init__(self, char_to_name: dict = {}, name_to_char: dict = {}, output_folder_name: str = "", role_tips: dict = {}):
        super().__init__(player_names=["Player1", "Player2", "Player3", "Player4", "Player5"])

        self.results = {}

        self.char_to_name = char_to_name
        self.turn = 0
        self.round = 1
        self.message_pool = MessagePool()
        self._terminal = False
        self.name_to_char = name_to_char

        self.output_folder_name = output_folder_name

        # intent, first_order, formulation, second_order, intent modify, refinement, discussion, vote, action,assassin,summary
        # if the intent is picked randomly, then skip intent selection phase
        self.phase = 'intent'
        self.current_player = 1
        self.current_leader = 1
        self.previous_player = 1
        self.vote_count = 0
        self.current_quest = 1
        self.every_round_team_member = {1: [], 2: [], 3: [], 4: [], 5: []}
        self.every_round_team_result = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, }
        self.every_round_leader = {'1': 'Player' + str(self.current_leader)}
        self.every_round_team_no = {1: 2, 2: 3, 3: 2, 4: 3, 5: 3}
        self.quest_result = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.current_intent = {}
        self.if_finish_contemplation = False
        self.is_first_order_active = False
        self.vote_result = {}
        self.consecutive_vote_failure_count = 0

        self.role_tips = {
            "Merlin": "You are " + self.char_to_name['Merlin'] + " and your role is Merlin. " + self.char_to_name['Morgana'] + ' and ' + self.char_to_name[
                'Assassin'] + " are evil players",
            "Percival": "You are " + self.char_to_name['Percival'] + " and your role is Percival. " + self.char_to_name['Merlin'] + ' and ' + self.char_to_name[
                'Morgana'] + " are Merlin and Morgana, but you don't know which is Merlin and which is Morgana.",
            "Servant": "You are " + self.char_to_name['Servant'] + " and your role is of a loyal servant.",
            "Morgana": "You are " + self.char_to_name['Morgana'] + " and your role is Morgana and Assassin is " + self.char_to_name['Assassin'] + ".",
            "Assassin": "You are " + self.char_to_name['Assassin'] + " and your role is Assassin and Morgana is " + self.char_to_name['Morgana'] + "."
        }
        if len(role_tips) > 0:
            self.role_tips = role_tips
            role_tips["Merlin"] += "\n" + self.char_to_name['Morgana'] + " and " + self.char_to_name[
                'Assassin'] + " are evil players."
            role_tips["Percival"] += "\n" + self.char_to_name['Merlin'] + ' and ' + self.char_to_name[
                'Morgana'] + " are Merlin and Morgana, but you don't know which is Merlin and which is Morgana."
            role_tips["Morgana"] += "\n" + "Your teammate Assassin is " + self.char_to_name['Assassin'] + "."
            role_tips["Assassin"] += "\n" + "Your teammate Morgana is " + self.char_to_name['Morgana'] + "."

        self.if_propose = True
        self.intent_eval_results = {}
        self.cur_intent_eval_idx = (0, "")
        self.player_intent_options = {}
        self.first_order_player_options = []
        self.first_order_player_option_idx = 0
        self.reset()

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all", round: int = 0, msg_type=None):
        """
        moderator say something
        """
        if round == 0:
            message = Message(agent_name="Moderator", content=text, turn=0, visible_to=visible_to, msg_type=msg_type)
        else:
            message = Message(agent_name="Moderator", content=text, turn=self.round, visible_to=visible_to,
                              msg_type=msg_type)

        self.message_pool.append_message(message)

    # start the game, everyone knows who is leader first
    # for the first round, no deductive reasoning, only contemplation
    def reset(self):
        self.turn = 0
        self.message_pool.reset()
        self._terminal = False

        # self.set_intent(round=1)
        # announce the leader
        self._moderator_speak('This is round ' + str(self.round) + '. For this round, the leader is ' + 'Player' + str(
            self.current_leader), round=self.round)

        # propose team prompt
        remember_speech = self.get_remember_speech('Player' + str(self.current_player))
        moderator_speech = Moderator_speech['discussion']['first'].replace('[remember]', '')
        self._moderator_speak(
            moderator_speech + str(self.every_round_team_no[self.current_quest]) + f".\n\nRemember: You need to pick {str(self.every_round_team_no[self.round])} team members.",
            round=self.round)
        self._moderator_speak(remember_speech, round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='role_tips')
        # intent prompts for first player
        self._moderator_speak(self.role_tips[self.name_to_char['Player' + str(self.current_player)]], round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='role_tips')
        if USE_INTENT_CATEGORY:
            self.phase = 'intent_category'
            self.prompt_for_intent_category_selection(self.current_player, self.turn, self.round)
        else:
            self.phase = 'intent'
            self.prompt_for_intent_selection(self.current_player, self.turn, self.round)

        observation = self.get_observation('Player' + str(self.current_player))

        return TimeStep(observation=observation, reward=self.get_zero_rewards(), terminal=False)

    # for each player, only get the intent of current round (for now), and filter the explanation (for now)
    def get_observation(self, player_name=None) -> List[Message]:
        if player_name is None:
            messages = self.message_pool.get_all_messages()
        else:
            messages = self.message_pool.get_visible_messages(player_name, turn=self.round, phase=self.phase)
        return messages

    # get current player
    def get_next_player(self) -> str:
        current_player = self.current_player
        self.previous_player = current_player
        if self.if_finish_contemplation:
            if self.phase not in ('intent_evaluation', 'selected_intent_evaluation'):
                if self.phase != 'action':
                    if self.current_player != 5:
                        self.current_player += 1
                    else:
                        self.current_player = 1
                else:
                    for member in self.every_round_team_member[self.round]:
                        if member not in self.every_round_team_result[self.round]:
                            self.current_player = int(member[-1])
                            return 'Player' + str(self.current_player)

        return 'Player' + str(current_player)

    # update current player, phase, calculate the vote, form the team, put the observation in the message pool
    def process_speech(self, response_str, player_name):
        if len(self.first_order_player_options) == 0:
            if self.round == 1 and self.consecutive_vote_failure_count == 0:
                other_players = ['Player' + str(i + 1) for i in range(player_name - 1)]
            else:
                other_players = ['Player' + str(i + 1) for i in range(5) if (i+1) != player_name]
            self.first_order_player_options = other_players
            self.first_order_player_option_idx = 0
            self.is_first_order_active = True

        response_str = response_str.replace('[other players]', self.first_order_player_options[self.first_order_player_option_idx])

        self.first_order_player_option_idx += 1
        if self.first_order_player_option_idx == len(self.first_order_player_options):
            self.is_first_order_active = False
            self.first_order_player_options = []
            self.first_order_player_option_idx = 0
        return response_str

    def extract_team_members(self, action):
        action_list = action.split('\n')
        players = action_list[0]
        players_list = players.split(',')
        for player in players_list:
            self.every_round_team_member[self.round][player] = None

    def check_game_state(self):
        fail = len([item for item in self.quest_result if self.quest_result[item] == 0])
        success = len([item for item in self.quest_result if self.quest_result[item] == 1])

        if fail >= 3:
            self._moderator_speak('The game is over! Evil team wins!', round=self.round)
            self._terminal = True
        if success >= 3:
            self._moderator_speak('The game is over! The loyal team wins! We move to the assassin phase.',
                                  round=self.round)
            self.phase = 'assassin'

    def filter_intent_options_player(self, player_name, turn, cur_round) -> list:
        character = self.name_to_char[player_name]
        intent_options = intents[character]

        filtered_intent_options = []
        count = 1
        for intent_opt in intent_options:
            intent = intent_opt['intent']
            type = intent_opt['type']
            allowed_in_turn = intent_opt['turn'].get(turn, True)
            allowed_in_round = intent_opt['round'].get(cur_round, True)
            if allowed_in_turn and allowed_in_round:
                filtered_intent_options.append(f"{intent}")
                count += 1
        return filtered_intent_options

    def build_intent_selection_prompt(self, player_name, turn, cur_round):
        return "\n".join(self.filter_intent_options_player(player_name, turn, cur_round))

    def build_intent_category_selection_prompt(self):
        return "\n".join(intent_categories)

    def build_min_intent_selection_prompt(self, player_name, turn, cur_round):
        final_intent_options = self.current_intent[player_name].copy()
        intent_options = self.filter_intent_options_player(player_name, turn, cur_round)
        unselected_intents = list(set(intent_options).difference(set(final_intent_options)))
        sample_size = min(len(unselected_intents), 5 - len(final_intent_options))
        final_intent_options.extend(random.sample(unselected_intents, sample_size))
        random.shuffle(final_intent_options)

        return "\n".join(final_intent_options)

    def prompt_for_first_order(self, cur_player, cur_round):
        player_name = 'Player' + str(cur_player)
        character = self.name_to_char[player_name]
        role_options = filter(lambda x: x != character, list(self.role_tips.keys()))

        moderator_speech = Moderator_speech['first_order']
        format_text = format_control['first_order']
        if character == "Merlin":
            moderator_speech = Moderator_speech['first_order_merlin']
            format_text = format_control['first_order_merlin']

        speech = self.process_speech(moderator_speech, cur_player)
        speech = speech.replace('[role options]', ', '.join(role_options))
        speech = speech.replace('[role options list]', '\n'.join(role_options))

        self._moderator_speak(speech, round=cur_round, visible_to=player_name, msg_type='first_order')
        self._moderator_speak(format_text, round=self.round,
                              visible_to=player_name, msg_type='format')

    def prompt_for_intent_selection(self, cur_player, cur_turn, cur_round):
        intent_options = self.build_intent_selection_prompt("Player" + str(cur_player), cur_turn, cur_round)

        self.player_intent_options["Player" + str(cur_player)] = intent_options.split("\n")

        self._moderator_speak(Moderator_speech['intent'] + intent_options, round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='intent')
        self._moderator_speak(format_control['intent'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_intent_category_selection(self, cur_player, cur_turn, cur_round):
        intent_category_options = self.build_intent_category_selection_prompt()

        self._moderator_speak(Moderator_speech['intent_category'] + intent_category_options, round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='intent_category')
        self._moderator_speak(format_control['intent_category'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_intent_generation(self, cur_player, cur_round):
        player_name = 'Player' + str(cur_player)
        selected_intent_categories = self.current_intent[player_name]
        char_intents = intents_total['general'].copy()
        char_intents.extend(intents_total[self.name_to_char[player_name]])
        example_intents = '\n'.join(random.sample(char_intents, 1))

        self._moderator_speak(Moderator_speech['intent_generation'].replace("[example intents]", example_intents) + "\n".join(selected_intent_categories), round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='intent_generation')
        self._moderator_speak(format_control['intent_generation'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_voting(self, cur_player, cur_round):
        player_name = "Player" + str(cur_player)
        remember_speech = self.get_remember_speech(player_name)
        self._moderator_speak(self.role_tips[self.name_to_char[player_name]],
                              round=cur_round, visible_to='Player' + str(cur_player), msg_type='role_tips')
        self._moderator_speak(player_name + ", " + 'the proposed team members are: ' + ','.join(
                self.every_round_team_member[self.round]) + ". It is your turn to vote. " + remember_speech, round=cur_round,
                              visible_to=player_name)
        self._moderator_speak(format_control['vote'], round=cur_round,
                              visible_to=player_name, msg_type='format')

    def prompt_for_intent_summarization(self, cur_player, cur_turn, cur_round):
        intent_options = self.build_intent_selection_prompt("Player" + str(cur_player), cur_turn,
                                                            cur_round)
        self._moderator_speak(Moderator_speech['intent_summarization'] + intent_options, round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type="intent_summarization")
        self._moderator_speak(format_control['intent_summarization'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_intent_summarization_min(self, cur_player, cur_turn, cur_round):
        intent_options = self.build_min_intent_selection_prompt("Player" + str(cur_player), cur_turn, cur_round)
        self._moderator_speak(Moderator_speech['intent_summarization_min'] + intent_options, round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type="intent_summarization_min")
        self._moderator_speak(format_control['intent_summarization_min'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_intent_modification(self, cur_player, cur_round):
        self._moderator_speak(Moderator_speech['intent_modify'], round=cur_round, visible_to='Player' + str(cur_player), msg_type="intent_modification")
        self._moderator_speak(format_control['intent'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_intent_category_modification(self, cur_player, cur_round):
        intent_category_options = self.build_intent_category_selection_prompt()
        self._moderator_speak(Moderator_speech['intent_category_modification'] + intent_category_options, round=cur_round, visible_to='Player' + str(cur_player), msg_type="intent_category_modification")
        self._moderator_speak(format_control['intent_category'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')
        
    def prompt_for_intent_evaluation(self, cur_player, cur_turn, cur_round):
        intent_option = self.player_intent_options["Player" + str(cur_player)][0]
        self.cur_intent_eval_idx = (0, intent_option)
        self._moderator_speak(Moderator_speech['intent_evaluation'].format(intent_option), round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='intent_evaluation')
        self._moderator_speak(format_control['intent_evaluation'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def prompt_for_selected_intent_evaluation(self, cur_player, cur_turn, cur_round):
        intent_option = self.current_intent["Player" + str(cur_player)][0]
        self.cur_intent_eval_idx = (0, intent_option)
        self._moderator_speak(Moderator_speech['selected_intent_evaluation'].format(intent_option), round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='selected_intent_evaluation')
        self._moderator_speak(format_control['selected_intent_evaluation'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def is_evil(self, name):
        character = self.name_to_char[name]
        if character in ('Morgana', 'Assassin'):
            return True
        return False

    def prompt_for_summary(self, cur_player, cur_round):
        player_name = "Player" + str(cur_player)
        if self.is_evil(player_name):
            moderator_speech = Moderator_speech['summary']['evil']
        else:
            moderator_speech = Moderator_speech['summary']['loyal']
        self._moderator_speak(moderator_speech, round=cur_round,
                              visible_to=player_name)
        self._moderator_speak(format_control['summary'], round=cur_round,
                              visible_to=player_name, msg_type='format')

    def prompt_for_action(self, cur_round):
        message = ""
        if not self.is_evil(self.get_next_player()):
            message = "\nAs a loyal player you should always succeed the quest."

        # self._moderator_speak(self.role_tips[character] + message, round=cur_round,
        #                       visible_to='Player' + str(self.current_player))
        self._moderator_speak(Moderator_speech['action'] + message, round=self.round)
        self._moderator_speak(format_control['action'], round=cur_round,
                              visible_to='Player' + str(self.current_player), msg_type='format')

    def update_results_key_for_team_disagreement(self, cur_round):
        new_key = cur_round + 10
        for player_name in self.player_names:
            self.results[player_name][new_key] = self.results[player_name].pop(cur_round)

    def save_results(self, player_name, phase, phase_data):
        cur_round = self.round
        if player_name not in self.results:
            self.results[player_name] = {}
            self.results[player_name]['role'] = self.name_to_char[player_name]

        if cur_round not in self.results[player_name]:
            self.results[player_name][cur_round] = {}
        if phase not in self.results[player_name][cur_round]:
            self.results[player_name][cur_round][phase] = []

        self.results[player_name][cur_round][phase].append(phase_data)
    
    def first_order(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['first_order'])
        # self.save_results(player_name, self.phase, {'intent_guess': action})

        if 'reasoning' in action.keys():
            del action['reasoning']
        if 'confidence' in action.keys():
            del action['confidence']
        if 'evidence' in action.keys():
            del action['evidence']

        self.save_results(player_name, self.phase, {'first_order': action})

        if 'intent' in action.keys():
            del action['intent']

        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=action,
                          msg_type='first_order', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message)

        if self.is_first_order_active:
            self.prompt_for_first_order(self.current_player, self.round)
        else:
            if USE_INTENT_CATEGORY:
                self.phase = 'intent_category'
                self.prompt_for_intent_category_selection(self.current_player, self.turn, self.round)
            else:
                self.phase = 'intent'
                self.prompt_for_intent_selection(self.current_player, self.turn, self.round)

    def select_intent(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent'])
        intents = action['Intents']
        thinking = action['Think']

        self.save_results(player_name, self.phase, {'intents': intents, 'think': thinking})

        self.current_intent[player_name] = intents

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent', visible_to=player_name, turn=self.round)
        # message3 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=answers,
        #                    msg_type='answers', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)
        # self.message_pool.append_message(message3)
        self.phase = "formulation_con"
        self._moderator_speak(
            Moderator_speech['formulation_contemplation'] + 'Remember your intents for this round is to ' +
            ', '.join(self.current_intent['Player' + str(self.current_player)]), round=self.round,
            visible_to='Player' + str(self.current_player), msg_type='intent')
        # self._moderator_speak(
        #     Moderator_speech['formulation_contemplation'] + 'Remember your intents for this round while thinking and speaking.', round=self.round,
        #     visible_to='Player' + str(self.current_player), msg_type='intent')
        self._moderator_speak(format_control['contemplation'], round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='format')

    def select_intent_category(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_category'])
        selected_intent_categories = action['Intents']
        thinking = action['Think']

        self.save_results(player_name, self.phase, {'intent_category': selected_intent_categories})

        self.current_intent[player_name] = selected_intent_categories

        message1 = Message(agent_name=player_name, content=selected_intent_categories, msg_type='intent_category', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent_category', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        if USE_INTENT_GENERATION:
            self.phase = "intent_generation"
            self.prompt_for_intent_generation(self.current_player, self.round)
        else:
            self.phase = "formulation_con"
            self._moderator_speak(
                Moderator_speech['formulation_contemplation'] + 'Remember your intent categories for this round are ' +
                ', '.join(self.current_intent['Player' + str(self.current_player)]), round=self.round,
                visible_to='Player' + str(self.current_player), msg_type='intent_category')
            self._moderator_speak(format_control['contemplation'], round=self.round,
                                  visible_to='Player' + str(self.current_player), msg_type='format')

    def intent_generation(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_generation'])
        generated_intents = action['Intents']
        thinking = action['Think']
        answers = action['Answers']

        self.save_results(player_name, self.phase, {'intents': generated_intents})

        self.current_intent[player_name] = generated_intents

        message1 = Message(agent_name=player_name, content=generated_intents, msg_type='intent', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent', visible_to=player_name, turn=self.round)
        message3 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=answers,
                           msg_type='answers', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)
        self.message_pool.append_message(message3)
        self.phase = "formulation_con"
        # self._moderator_speak(
        #     Moderator_speech['formulation_contemplation'] + 'Remember your intent for this round is to ' +
        #     ', '.join(self.current_intent['Player' + str(self.current_player)]), round=self.round,
        #     visible_to='Player' + str(self.current_player), msg_type='intent')
        self._moderator_speak(
            Moderator_speech['formulation_contemplation'] + 'Remember your intents for this round while thinking and speaking.', round=self.round,
            visible_to='Player' + str(self.current_player), msg_type='intent')
        self._moderator_speak(format_control['contemplation'], round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='format')

    def formulation_con(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['contemplation'])


        thinking = action['Think']
        speak = action['Speak']
        self.save_results(player_name, self.phase, {'think': thinking, 'speech': speak})

        message1 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content="Think:" + thinking,
                           msg_type="formulation_con", visible_to=player_name, turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content="Speech:" + speak,
                           msg_type="formulation_con", visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.phase = "second_order"
        self._moderator_speak(Moderator_speech['second_order'], round=self.round, visible_to=player_name, msg_type='second_order')
        self._moderator_speak(format_control['second_order'], round=self.round, visible_to=player_name,
                              msg_type='format')

    def get_remember_speech(self, player_name):
        if self.name_to_char[player_name] in ('Morgana', 'Assassin'):
            remember_speech = Moderator_remember_speech['team']['evil']
        else:
            remember_speech = Moderator_remember_speech['team']['good']
        return remember_speech

    def second_order(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['second_order'])
        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=action,
                          msg_type="second_order", visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message)

        if USE_INTENT_CATEGORY and not USE_INTENT_GENERATION:
            self.phase = 'intent_category_modification'
            self.prompt_for_intent_category_modification(self.current_player, self.round)
        else:
            self.phase = 'intent_modification'
            self.prompt_for_intent_modification(self.current_player, self.round)

    def intent_modification(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent'])
        new_intents = action['Intents']
        thinking = action['Think']

        if len(new_intents) > 0:
            self.save_results(player_name, self.phase, {'new_intents': new_intents, 'think': thinking})
            self.current_intent[player_name] = new_intents

        message1 = Message(agent_name=player_name, content=new_intents, msg_type='intent', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.if_finish_contemplation = True
        self._moderator_speak(self.role_tips[self.name_to_char['Player' + str(self.current_player)]],
                              round=self.round, visible_to='Player' + str(self.current_player), msg_type='role_tips')
        self._moderator_speak(Moderator_speech['refinement_contemplation'] + 'Remember your intents for this round is to ' +
                              ', '.join(self.current_intent['Player' + str(self.current_player)]) + f"\n\nRemember: You need to pick {str(self.every_round_team_no[self.round])} team members.", round=self.round, visible_to=player_name, msg_type='intent')

        self.phase = 'discussion'
        if self.if_propose:
            # if self.round > 1:
            # remember_speech = self.get_remember_speech(player_name)
            # moderator_speech = Moderator_speech['discussion']['first'].replace('[remember]', remember_speech)
            # self._moderator_speak(
            #      moderator_speech + str(self.every_round_team_no[self.round]) + f". Remember to pick {str(self.every_round_team_no[self.round])} team members.",
            #     round=self.round, visible_to=player_name)
            # self._moderator_speak(str(self.every_round_team_no[
            #                                self.round]) + f". Remember to pick {str(self.every_round_team_no[self.round])} team members.",
            #     round=self.round, visible_to=player_name)
            self._moderator_speak(format_control['proposal'], round=self.round, visible_to=player_name, msg_type='format')
        else:
            # moderator_speech = Moderator_speech['discussion']['rest'].replace('[proposed team players]', ', '.join(
            #     self.every_round_team_member[self.round]))
            # moderator_speech = moderator_speech.replace("[leader]", 'Player' + str(self.current_leader))
            # moderator_speech = moderator_speech.replace("[remember]", self.get_remember_speech('Player' + str(self.current_player)))
            # self._moderator_speak("Player" + str(self.current_player) + moderator_speech,
            #                       visible_to='Player' + str(self.current_player), round=self.round)
            self._moderator_speak(format_control['contemplation'], round=self.round, visible_to=player_name,
                                  msg_type='format')
        self.if_finish_contemplation = True

    def intent_category_modification(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_category'])
        new_intent_categories = action['Intents']
        thinking = action['Think']

        if len(new_intent_categories) > 0:
            self.save_results(player_name, self.phase, {'new_intent_categories': new_intent_categories})
            self.current_intent[player_name] = new_intent_categories

        message1 = Message(agent_name=player_name, content=new_intent_categories, msg_type='intent_category', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent_category', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.if_finish_contemplation = True
        self._moderator_speak(Moderator_speech['refinement_contemplation'] + 'Remember your new intent for this round is to ' +
                              ', '.join(self.current_intent['Player' + str(self.current_player)]), round=self.round, visible_to=player_name, msg_type='intent')
        self.phase = 'discussion'
        if self.if_propose:
            # if self.round > 1:
            remember_speech = self.get_remember_speech(player_name)
            moderator_speech = Moderator_speech['discussion']['first'].replace('[remember]', remember_speech)
            self._moderator_speak(
                moderator_speech + str(self.every_round_team_no[self.round]) + f".\n\nRemember: You need to pick {str(self.every_round_team_no[self.round])} team members.",
                round=self.round, visible_to=player_name)
            self._moderator_speak(format_control['proposal'], round=self.round, visible_to=player_name, msg_type='format')
        else:
            # moderator_speech = Moderator_speech['discussion']['rest'].replace('[proposed team players]', ', '.join(
            #     self.every_round_team_member[self.round]))
            # moderator_speech = moderator_speech.replace("[leader]", 'Player' + str(self.current_leader))
            # moderator_speech = moderator_speech.replace("[remember]",
            #                                             self.get_remember_speech('Player' + str(self.current_player)))
            # self._moderator_speak("Player" + str(self.current_player) + moderator_speech,
            #                       visible_to='Player' + str(self.current_player), round=self.round)
            self._moderator_speak(format_control['contemplation'], round=self.round, visible_to=player_name, msg_type='format')

    def discussion(self, player_name, action):
        if player_name == 'Player' + str(self.current_leader):
            action = utils.parse_json_response(response=action, schema=format_control_schemas['proposal'])
            thinking = action['Think']
            speech = action['Speak']

            self.save_results(player_name, self.phase, {'think': thinking, 'speech': speech})

            message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                              msg_type='thinking', visible_to=player_name, turn=self.round)
            self.message_pool.append_message(message)

            proposed_players = [player.strip() for player in action['team'].split(',')]
            self.every_round_team_member[self.round] = proposed_players
            if len(proposed_players) != self.every_round_team_no[self.current_quest]:
                print("Proposed number of team members don't match the required the team members.", proposed_players)
                sys.exit()

            message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")",
                               content="The proposed team is - " + action['team'] + ".\n" + speech, msg_type='discussion', visible_to='all',
                               turn=self.round)
            self.if_propose = False

        else:
            action = utils.parse_json_response(response=action, schema=format_control_schemas['contemplation'])
            thinking = action['Think']
            speech = action['Speak']

            self.save_results(player_name, self.phase, {'think': thinking, 'speech': speech})

            message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                              msg_type='thinking', visible_to=player_name, turn=self.round)
            self.message_pool.append_message(message)

            message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=speech, 
                               msg_type='discussion', visible_to='all', turn=self.round)

        self.message_pool.append_message(message2)
        self.turn += 1
        if self.turn < 5:
            self.if_finish_contemplation = False
            self.phase = "first_order"
            self._moderator_speak("Player" + str(self.current_player) + Moderator_speech['discussion']['general'].replace('[proposed team players]', ', '.join(self.every_round_team_member[self.round])),
                                  round=self.round)
            self._moderator_speak(self.role_tips[self.name_to_char['Player' + str(self.current_player)]],
                                  round=self.round, visible_to='Player' + str(self.current_player), msg_type='role_tips')
            moderator_speech = Moderator_speech['discussion']['rest'].replace('[proposed team players]', ', '.join(self.every_round_team_member[self.round]))
            moderator_speech = moderator_speech.replace("[leader]", 'Player' + str(self.current_leader))
            moderator_speech = moderator_speech.replace("[remember]", self.get_remember_speech('Player' + str(self.current_player)))
            self._moderator_speak("Player" + str(self.current_player) + moderator_speech,
                                  visible_to='Player' + str(self.current_player), round=self.round)
            self.prompt_for_first_order(self.current_player, self.round)

        else:
            # self.phase = 'vote'
            # self._moderator_speak(Moderator_speech['vote'], round=self.round)
            # self.prompt_for_voting(self.current_player, self.round)
            # self.turn = 0
            self.current_player = self.current_leader
            self.turn = 0
            self.phase = 'reconsider_team'
            leader_player_name = 'Player' + str(self.current_leader)
            remember_speech = self.get_remember_speech(leader_player_name)
            moderator_speech = Moderator_speech['discussion']['reconsider'].replace('[remember]', remember_speech)
            moderator_speech = moderator_speech.replace('[original team]', ', '.join(self.every_round_team_member[self.round]))
            self._moderator_speak(
                moderator_speech + str(self.every_round_team_no[self.round]) + f".\n\nRemember: You need to pick {str(self.every_round_team_no[self.round])} team members.",
                round=self.round, visible_to=leader_player_name)
            self._moderator_speak(format_control['reconsider_proposal'], round=self.round, visible_to=leader_player_name, msg_type='format')

    def reconsider_team(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['reconsider_proposal'])
        thinking = action['Think']
        speech = action['Speak']
        answer = action['Answer']

        self.save_results(player_name, self.phase, {'think': thinking, 'speech': speech})

        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                            msg_type='thinking', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message)

        message1 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=answer,
                            msg_type='answer', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)

        proposed_players = action['team'].split(',')
        if len(proposed_players) > 0:
            self.every_round_team_member[self.round] = proposed_players
            if len(proposed_players) != self.every_round_team_no[self.current_quest]:
                print("Proposed number of team members don't match the required the team members.", proposed_players)
                sys.exit()

        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")",
                            content="The proposed team is - " + action['team'] + ".\n" + speech, msg_type='discussion', visible_to='all',
                            turn=self.round)
        
        self.message_pool.append_message(message2)

        self.phase = 'vote'
        self.turn = 0
        self._moderator_speak(Moderator_speech['vote'], round=self.round)
        self.prompt_for_voting(self.current_player, self.round)
        

    def vote(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['vote'])

        vote_result = action['vote']
        explanation = action['explanation']

        self.vote_result[player_name] = vote_result

        self.save_results(player_name, self.phase, {'vote_result': vote_result, 'think': explanation})

        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=explanation,
                           msg_type='explanation', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message2)

        if vote_result == 'agree':
            self.vote_count += 1
        self.turn += 1
        if self.turn != 5:
            self.prompt_for_voting(self.current_player, self.round)

        if self.turn == 5:
            if self.vote_count >= 3 or self.consecutive_vote_failure_count == 1:
                # on agreement on team or 2 consecutive disagreement, this should execute
                self.consecutive_vote_failure_count = 0
                self.vote_count = 0
                self._moderator_speak(
                    Moderator_speech['vote_result']['agree'] + ','.join(self.every_round_team_member[self.round]),
                    round=self.round)  # add player name
                self._moderator_speak("The vote result for this round is: " + str(self.vote_result), round=self.round)
                self.phase = 'action'
                self.prompt_for_action(self.round)
            else:
                # on the first disagreement on team, this should execute
                self.consecutive_vote_failure_count += 1
                self.current_player = 1

                if USE_INTENT_EVAL:
                    self.phase = 'intent_summarization'
                    self._moderator_speak("The vote result for this round is: " + str(self.vote_result),
                                          round=self.round)
                    self._moderator_speak(Moderator_speech['vote_result']['disagree'], round=self.round)
                    self.prompt_for_intent_summarization(self.current_player, self.turn, self.round)
                else:
                    self.phase = "summary"
                    self._moderator_speak("The vote result for this round is: " + str(self.vote_result),
                                          round=self.round)
                    self._moderator_speak(Moderator_speech['vote_result']['disagree'], round=self.round)
                    self.prompt_for_summary(self.current_player, self.round)

            self.turn = 0

    def action(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['action'])

        result = action['result']
        explanation = action['explanation']
        answers = action['answers']

        self.every_round_team_result[self.round][player_name] = result

        self.save_results(player_name, self.phase, {'action_result': result, 'think': explanation, 'context_answers': answers})

        message1 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=result,
                           msg_type='action', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=explanation,
                           msg_type='explanation', visible_to=player_name, turn=self.round)
        message3 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=answers,
                           msg_type='answers', visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message2)
        self.message_pool.append_message(message3)

        self.turn += 1
        if self.turn == len(self.every_round_team_member[self.round]):
            fail_no = list(self.every_round_team_result[self.round].values()).count('failure')
            if fail_no > 0:
                self.quest_result[self.round] = 0
                self._moderator_speak("The quest is failed, there are " + str(fail_no) + ' fail choice',
                                      round=self.round)
            else:
                self.quest_result[self.round] = 1
                self._moderator_speak("Nice, the quest is successful!", round=self.round)

            self.turn = 0
            self.check_game_state()
            if self.phase == 'assassin':
                self._moderator_speak(self.role_tips['Assassin'], round=self.round,
                                      visible_to=self.char_to_name['Assassin'], msg_type='role_tips')
                self._moderator_speak(text=Moderator_speech['assassin'], visible_to=self.char_to_name['Assassin'],
                                      round=self.round)
                self.current_player = int(self.char_to_name['Assassin'][-1])
                self._moderator_speak(text=format_control['assassin'], round=self.round,
                                      visible_to=self.char_to_name['Assassin'], msg_type='format')
            else:
                self.current_player = 1
                if USE_INTENT_EVAL:
                    self.phase = 'intent_summarization'
                    self.prompt_for_intent_summarization(self.current_player, self.turn, self.round)
                else:
                    self.phase = "summary"
                    self.prompt_for_summary(self.current_player, self.round)

            if self._terminal:
                return TimeStep(observation=self.get_observation(player_name), reward=self.get_zero_rewards(),
                                terminal=self._terminal)
        else:
            self.prompt_for_action(self.round)

    def intent_summarization(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_summarization'])

        intents = action['Intents']
        thinking = action['Think']

        self.save_results(player_name, self.phase, {'intents': intents})

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent_summarization', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent_summarization', visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.turn += 1
        if self.turn == 5:
            self.current_player = 1
            self.turn = 0
            self.phase = 'intent_summarization_min'
            self.prompt_for_intent_summarization_min(self.current_player, self.turn, self.round)
        else:
            self.prompt_for_intent_summarization(self.current_player, self.turn, self.round)

    def intent_summarization_min(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_summarization_min'])

        intents = action['Intents']
        thinking = action['Think']

        self.save_results(player_name, self.phase, {'intents': intents})

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent_summarization_min', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent_summarization_min', visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.turn += 1
        if self.turn == 5:
            # self.phase = 'intent_evaluation'
            self.phase = 'selected_intent_evaluation'
            self.turn = 0
            self.current_player = 1
            # self.prompt_for_intent_evaluation(self.current_player, self.turn, self.round)
            self.prompt_for_selected_intent_evaluation(self.current_player, self.turn, self.round)
        else:
            self.prompt_for_intent_summarization_min(self.current_player, self.turn, self.round)

    def intent_evaluation(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_evaluation'])

        result = action['Result']
        thinking = action['Think']

        message1 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=result,
                           msg_type='intent_evaluation', visible_to=player_name, turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                          msg_type='intent_evaluation', visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        if player_name not in self.intent_eval_results:
            self.intent_eval_results[player_name] = {}
        if self.round not in self.intent_eval_results[player_name]:
            self.intent_eval_results[player_name][self.round] = {}

        self.intent_eval_results[player_name][self.round][self.cur_intent_eval_idx[1]] = result

        if self.cur_intent_eval_idx[0] == len(self.player_intent_options["Player" + str(self.current_player)]) - 1:
            self.save_results(player_name, self.phase, {'intent_eval': self.intent_eval_results[player_name][self.round]})

            self.turn += 1
            if self.turn == 5:
                self.phase = "summary"
                self.current_player = 1
                self.turn = 0
                self.prompt_for_summary(self.current_player, self.round)
                return
            elif self.current_player == 5:
                self.current_player = 1
            else:
                self.current_player += 1
            intent_option = self.player_intent_options["Player" + str(self.current_player)][0]
            self.cur_intent_eval_idx = (0, intent_option)
        else:
            cur_idx = self.cur_intent_eval_idx[0] + 1
            intent_option = self.player_intent_options["Player" + str(self.current_player)][cur_idx]
            self.cur_intent_eval_idx = (cur_idx, intent_option)

        self._moderator_speak(Moderator_speech['intent_evaluation'].format(intent_option), round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='intent_evaluation')
        self._moderator_speak(format_control['intent_evaluation'], round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='format')

    def selected_intent_evaluation(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['selected_intent_evaluation'])

        result = action['Result']
        thinking = action['Think']

        message1 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=result,
                           msg_type='selected_intent_evaluation', visible_to=player_name, turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                          msg_type='selected_intent_evaluation', visible_to=player_name, turn=self.round)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        if player_name not in self.intent_eval_results:
            self.intent_eval_results[player_name] = {}
        if self.round not in self.intent_eval_results[player_name]:
            self.intent_eval_results[player_name][self.round] = {}

        self.intent_eval_results[player_name][self.round][self.cur_intent_eval_idx[1]] = result

        if self.cur_intent_eval_idx[0] == len(self.current_intent["Player" + str(self.current_player)]) - 1:
            self.save_results(player_name, self.phase, {'selected_intent_evaluation': self.intent_eval_results[player_name][self.round]})

            self.turn += 1
            if self.turn == 5:
                self.phase = "summary"
                self.current_player = 1
                self.turn = 0
                self.prompt_for_summary(self.current_player, self.round)
                return
            elif self.current_player == 5:
                self.current_player = 1
            else:
                self.current_player += 1
            intent_option = self.current_intent["Player" + str(self.current_player)][0]
            self.cur_intent_eval_idx = (0, intent_option)
        else:
            cur_idx = self.cur_intent_eval_idx[0] + 1
            intent_option = self.current_intent["Player" + str(self.current_player)][cur_idx]
            self.cur_intent_eval_idx = (cur_idx, intent_option)

        self._moderator_speak(Moderator_speech['selected_intent_evaluation'].format(intent_option), round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='selected_intent_evaluation')
        self._moderator_speak(format_control['selected_intent_evaluation'], round=self.round,
                              visible_to='Player' + str(self.current_player), msg_type='format')

    def summary(self, player_name, action):
        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=action,
                          msg_type='summary', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message)
        self.save_results(player_name, self.phase,
                          {'summary': action})

        self.turn += 1
        if self.turn == 5:
            if self.vote_count < 3 and self.consecutive_vote_failure_count == 1:
                # on disagreement this should execute
                self.update_results_key_for_team_disagreement(self.round)
                self.every_round_leader[str(self.round + 10)] = 'Player' + str(self.current_leader)
                if self.current_leader != 5:
                    self.current_leader += 1
                else:
                    self.current_leader = 1

                self.every_round_leader[str(self.round)] = 'Player' + str(self.current_leader)

                self.current_player = self.current_leader
                self._moderator_speak(Moderator_speech['vote_result']['announce_leader'] + str(self.current_leader),
                                      round=self.round)
                remember_speech = self.get_remember_speech(player_name)
                moderator_speech = Moderator_speech['discussion']['first'].replace('[remember]', '')
                self._moderator_speak(moderator_speech + str(
                    self.every_round_team_no[self.current_quest]) + '. Remember to select different players this time.',
                                      round=self.round)
                self._moderator_speak(remember_speech, round=self.round,
                                      visible_to='Player' + str(self.current_player), msg_type='role_tips')

                self.if_finish_contemplation = False
                self.if_propose = True
                self.phase = "first_order"
                self.prompt_for_first_order(self.current_player, self.round)

                self.vote_count = 0
                self.every_round_team_member[self.round] = []
            else:
                # on agreement on team and quest completion this should execute
                self.phase = 'discussion'
                self.if_propose = True
                self.round += 1

                if self.current_leader != 5:
                    self.current_leader += 1
                else:
                    self.current_leader = 1

                self.every_round_leader[str(self.round)] = 'Player' + str(self.current_leader)

                self.current_player = self.current_leader
                self.current_quest += 1

                print(f'\n\nNow entering round - {self.round}\n\n')

                self._moderator_speak(
                    'This is round ' + str(self.round) + '. For this round, the leader is ' + 'Player' + str(
                        self.current_leader), round=self.round)

                self.if_finish_contemplation = False
                self.phase = "first_order"
                self._moderator_speak(self.role_tips[self.name_to_char['Player' + str(self.current_player)]],
                                      round=self.round, visible_to='Player' + str(self.current_player), msg_type='role_tips')
                self.prompt_for_first_order(self.current_player, self.round)

            self.turn = 0
        else:
            self.prompt_for_summary(self.current_player, self.round)

    def assassin(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['assassin'])
        assassinated_player = action['player']

        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")",
                          content=assassinated_player, turn=self.round)
        self.message_pool.append_message(message)
        if assassinated_player != self.char_to_name['Merlin']:
            self._moderator_speak('Assassin failed! The game is over. Loyal team wins!', round=self.round)
        else:
            self._moderator_speak('Assassin succeed! The game is over. Evil team wins!', round=self.round)
        self._terminal = True

    def step(self, player_name: str, action: str) -> TimeStep:
        print("===============================================================")
        print(f"Phase: {self.phase}, Player: {player_name}")
        print("===============================================================")
        # try:
        self.check_game_state()
        if self._terminal:
            return TimeStep(observation=self.get_observation(player_name), reward=self.get_zero_rewards(),
                            terminal=self._terminal)

        if self.phase == 'intent':
            self.select_intent(player_name, action)
        elif self.phase == 'intent_category':
            self.select_intent_category(player_name, action)
        elif self.phase == 'intent_generation':
            self.intent_generation(player_name, action)

        elif self.phase == "first_order":
            self.first_order(player_name, action)
        elif self.phase == "formulation_con":
            self.formulation_con(player_name, action)
        elif self.phase == "second_order":
            self.second_order(player_name, action)
        elif self.phase == "intent_modification":
            self.intent_modification(player_name, action)
        elif self.phase == 'intent_category_modification':
            self.intent_category_modification(player_name, action)

        elif self.phase == 'discussion':
            self.discussion(player_name, action)
        elif self.phase == 'reconsider_team':
            self.reconsider_team(player_name, action)
        elif self.phase == 'vote':
            self.vote(player_name, action)

        elif self.phase == 'action':
            self.action(player_name, action)

        elif self.phase == 'intent_summarization':
            self.intent_summarization(player_name, action)
        elif self.phase == 'intent_summarization_min':
            self.intent_summarization_min(player_name, action)
        elif self.phase == 'intent_evaluation':
            self.intent_evaluation(player_name, action)
        elif self.phase == 'selected_intent_evaluation':
            self.selected_intent_evaluation(player_name, action)
        elif self.phase == 'summary':
            self.summary(player_name, action)

        elif self.phase == 'assassin':
            self.assassin(player_name, action)

        with open(self.output_folder_name + "/results" + ".json", "w") as file:
            json.dump(self.results, file)

        return TimeStep(observation=self.get_observation(player_name), reward=self.get_zero_rewards(),
                 terminal=self._terminal)


if __name__ == "__main__":
    folder_name = config_utils.get_config_value("output_game_folder") + "/game_" + str(datetime.datetime.now().date()) + '-' + str(
        datetime.datetime.now().hour) + '-' + str(
        datetime.datetime.now().minute) + '-' + str(datetime.datetime.now().second)
    file_name = folder_name + '/conversation'
    is_openai_model = config_utils.get_config_value("is_openai_model")
    model_name = config_utils.get_config_value("model_name")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    players_no = [1, 2, 3, 4, 5]
    characters = ['Merlin', 'Percival', 'Servant', 'Assassin', 'Morgana']
    players = {}
    character_to_player = {}
    shuffled_players = random.sample(players_no, 5)
    for index, player_no in enumerate(shuffled_players):
        players['Player' + str(player_no)] = characters[index]
        character_to_player[characters[index]] = 'Player' + str(player_no)

    if is_openai_model:
        backend = OpenAIChat(model=model_name)
        # backend = OpenAIChat(model="gpt-4-1106-preview")
    else:
        backend = LLamaChat()

    role_tips = {}
    for player in players:
        if players[player] == 'Assassin':
            addition_info = [name for name in players if players[name] == 'Morgana'][0]

        elif players[player] == 'Morgana':
            addition_info = [name for name in players if players[name] == 'Assassin'][0]
        elif players[player] == 'Merlin':
            addition_info = [name for name in players if players[name] in ['Morgana', 'Assassin']]
            addition_info = ','.join(addition_info)
        elif players[player] == 'Percival':
            addition_info = [name for name in players if players[name] in ['Morgana', 'Merlin']]
            addition_info = ','.join(
                addition_info) + " .However, you don't know which one is Merlin and which one is Morgana, you only know one of them is Merlin and another one is Morgana."
        else:
            addition_info = ''
        
        if player[-1] == '1':
            player1 = Player(name='Player1', role_desc=Role_tips[players[player]] + addition_info,
                             global_prompt=game_description, backend=backend)

        elif player[-1] == '2':
            player2 = Player(name='Player2', role_desc=Role_tips[players[player]] + addition_info,
                             global_prompt=game_description, backend=backend)

        elif player[-1] == '3':
            player3 = Player(name='Player3', role_desc=Role_tips[players[player]] + addition_info,
                             global_prompt=game_description, backend=backend)

        elif player[-1] == '4':
            player4 = Player(name='Player4', role_desc=Role_tips[players[player]] + addition_info,
                             global_prompt=game_description, backend=backend)

        elif player[-1] == '5':
            player5 = Player(name='Player5', role_desc=Role_tips[players[player]] + addition_info,
                             global_prompt=game_description, backend=backend)

        role_tips[players[player]] = Role_tips[players[player]]

    conversation_df = pd.DataFrame(columns=['agent_name', 'visible_to', 'content', 'turn', 'timestamp', 'msg_type'])
    conversation_df.to_csv(file_name + '.csv', index=False)

    env = Avalon(character_to_player, players, folder_name, role_tips=role_tips)
    arena = Arena([player1, player2, player3, player4, player5], env)
    arena.launch_cli(interactive=False, output_file=file_name)

    with open(folder_name + "/game_play_data.json", "w") as f:
        data = {
            "character_to_player": character_to_player,
            "round_team_members": env.every_round_team_member,
            "team_quest_result": env.every_round_team_result,
            'quest_results': env.quest_result,
            'round_leaders': env.every_round_leader
        }
        json.dump(data, f)

    print("Players:")
    print(env.name_to_char)

    print("Players:")
    print(env.char_to_name)

    print("Team members:")
    print(env.every_round_team_member)

    print("Team result:")
    print(env.every_round_team_result)

    print("Quest result:")
    print(env.quest_result)
