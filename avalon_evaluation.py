from scripts import config_utils, utils
import json
import random
import string
from typing import List, Union
import os

from chatarena.agent import Player
from chatarena.arena import Arena
from chatarena.backends import OpenAIChat, LLamaChat
from chatarena.environments.base import TimeStep, Environment
from chatarena.message import Message, MessagePool
from prompts import game_description, Moderator_speech, format_control, \
    format_control_schemas, intents_total

characters = string.ascii_letters + string.digits

USE_LLAMA = False
USE_INTENT_CATEGORY = False
USE_INTENT_GENERATION = False
USE_INTENT_EVAL = False


# f=open('output/'+filename+'.txt','w+')


class Avalon(Environment):
    type_name = 'Avalon'
    intent_summarization_ctx_tmplt = """\
Current Game Details and State: 

{}

Your thinking: 
{}

Your speech:
{}

"""

    intent_guessing_ctx_tmplt = """\
Current Game Details and State: 

{}
"""

    intent_guessing_speech_tmplt = """\
Now, here is your speech:
{}

Select 2-3 intents without modifications that {} might think you have based on your speech and above given game context.

Let's think step by step before making your decisions.

"""

    intent_guessing_ext_tmplt = """\
Given below are your intentions and following for this round. 
Please use this as a reflection of your own thinking and speaking experiment for better understanding others’ intentions.

Intents:
{}

Your thinking:
{}

Your speech:
{}

Player's dialogue in this round: 
{}
"""

    intent_selection_ctx_tmplt = """\
Current Game Details and State: 

{}

"""

    hallucination_detection_ctx_tmplt = """\
Current Game Details and State: 

{}
"""

    hallucination_detection_ext_tmplt = """\
Player's dialogue in this round: 
{}
"""

    def __init__(
            self,
            phase: str = "first_order",
            char_to_name: dict = {},
            name_to_char: dict = {},
            hallucination_detection_data: dict = {},
            ref_con_data: dict = {},
            reas_intnt_data: dict = {},
            intent_sum_data: dict = {},
            save_path: str = ""
    ):
        super().__init__(player_names=["Agent1"])

        self.roles = ['Assassin', "Morgana", "Merlin", "Servant", "Percival"]

        self.results = {}

        self.phase = phase

        self.eval_results = {}

        self.hallucination_detection_data = hallucination_detection_data
        self.ref_con_data = ref_con_data
        self.reas_intent_data = reas_intnt_data
        self.intent_sum_data = intent_sum_data

        self.ids = list(self.intent_sum_data.keys())
        if self.phase == "first_order":
            self.ids = list(self.ref_con_data.keys())
        elif self.phase == "hallucination_detection":
            self.ids = list(self.hallucination_detection_data.keys())

        self.cur_idx = 0

        self.char_to_name = char_to_name
        self.turn = 0
        self.round = 1
        self.message_pool = MessagePool(eval_mode=True)
        self._terminal = False
        self.name_to_char = name_to_char

        self.intent_eval_results = {}
        self.cur_intent_eval_idx = (0, "")
        self.player_intent_options = {}
        self.first_order_player_options = []
        self.first_order_player_option_idx = 0

        self.save_path = save_path

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

    def get_inent_options(self, role):
        options = intents_total['general'].copy()
        if role != '':
            options.extend(intents_total[role])
        else:
            print("Empty role. Shouldn't happen.")
        return '\n'.join(options)

    def extract_role(self, context):
        lines = context.split('\n')
        for line in lines:
            if line.startswith('**Role**: '):
                return line.replace('**Role**: ', '')

        return ''

    def min_context_for_intent_guessing(self, context):
        lines = context.split('\n')

        rs = []
        incl = False
        speaker_name = None
        for line in lines:
            # if not incl and line.startswith('**Current Leader**:'):
            #     incl = True
            # if incl:
            rs.append(line)
            if line.startswith('**Player Name**:'):
                speaker_name = line.split(': ')[-1].strip()
        return '\n'.join(rs), speaker_name

    def min_context_for_intent_summarization(self, context, inc_discussion=False):
        lines = context.split('\n')

        rs = []
        for line in lines:
            if line.startswith('**Other Players**:'):
                continue
            if not inc_discussion and line.startswith('**Previous Discussions'):
                break
            rs.append(line)
        return '\n'.join(rs)

    def prompt_for_intent_summarization(self):
        cur_key = self.ids[self.cur_idx]
        context = self.intent_sum_data[cur_key]['context']
        think = self.intent_sum_data[cur_key]['think']
        speak = self.intent_sum_data[cur_key]['speak']

        prompt = self.intent_summarization_ctx_tmplt.format(
            self.min_context_for_intent_summarization(context, inc_discussion=True),
            think,
            speak
        )

        intent_options = self.get_inent_options(self.extract_role(context))
        self._moderator_speak(prompt + "\n\n" + Moderator_speech['intent_summarization'] + intent_options, round=0,
                              visible_to='Agent1', msg_type="intent_summarization")
        self._moderator_speak(format_control['intent_summarization'], round=0,
                              visible_to='Agent1', msg_type='format')

    def prompt_for_intent_guessing(self):
        is_reflective = False
        cur_key = self.ids[self.cur_idx]
        context, speaker_name = self.min_context_for_intent_guessing(self.ref_con_data[cur_key]['context'])

        prompt = self.intent_guessing_ctx_tmplt.format(
            context
        )

        speech = self.intent_guessing_speech_tmplt.format(
            self.ref_con_data[cur_key]['speak'], speaker_name
        )

        role = context.split('\n')[2].split(': ')[-1].strip()
        role_options = filter(lambda x: x != role, self.roles)
        moderator_speech = Moderator_speech['intent_guessing_second_order'].replace('[role options]',
                                                                                    ', '.join(role_options))
        moderator_speech = moderator_speech.replace('[role options list]', ', '.join(role_options))

        if is_reflective:
            persp_player_name = self.ref_con_data[cur_key]['persp_player'].capitalize()

            persp_player_intents = '\n'.join(self.ref_con_data[cur_key]['persp_player_intents'])
            persp_player_think = self.ref_con_data[cur_key]['persp_player_think']
            persp_player_speak = self.ref_con_data[cur_key]['persp_player_speak']

            extn_prompt = self.intent_guessing_ext_tmplt.format(
                persp_player_intents,
                persp_player_think,
                persp_player_speak,
                self.ref_con_data[cur_key]['speak']
            )
            self._moderator_speak(prompt + "\n" + extn_prompt + "\n\n" + moderator_speech, round=0, visible_to='Agent1',
                                  msg_type='first_order')
        else:
            self._moderator_speak(prompt + "\n\n" + moderator_speech + "\n" + speech, round=0, visible_to='Agent1',
                                  msg_type='first_order')

        self._moderator_speak(format_control['intent_guessing'], round=self.round,
                              visible_to='Agent1', msg_type='format')

    def prompt_for_intent_selection(self):
        cur_key = self.ids[self.cur_idx]
        context = self.reas_intent_data[cur_key]['context']

        prompt = self.intent_selection_ctx_tmplt.format(
            context,
        )

        intent_options = self.get_inent_options(self.extract_role(context))

        self._moderator_speak(prompt + "\n\n" + Moderator_speech['intent'] + intent_options, round=0,
                              visible_to='Agent1', msg_type='intent')
        self._moderator_speak(format_control['intent'], round=0,
                              visible_to='Agent1', msg_type='format')

    def prompt_for_hallucination_detection(self):
        cur_key = self.ids[self.cur_idx]
        context, speaker_name = self.min_context_for_intent_guessing(self.ref_con_data[cur_key]['context'])

        prompt = self.hallucination_detection_ctx_tmplt.format(
            context
        )

        speech = self.hallucination_detection_ext_tmplt.format(
            self.ref_con_data[cur_key]['speak'], speaker_name
        )

        # question = self.ref_con_data[cur_key]['question']

        role = context.split('\n')[2].split(': ')[-1].strip()
        role_options = filter(lambda x: x != role, self.roles)
        moderator_speech = Moderator_speech['hallucination_detection'].replace('[role options]',
                                                                               ', '.join(role_options))
        moderator_speech = moderator_speech.replace('[role options list]', ', '.join(role_options))

        self._moderator_speak(prompt + "\n\n" + speech + "\n" + moderator_speech, round=0, visible_to='Agent1',
                              msg_type='first_order')

        self._moderator_speak(format_control['hallucination_detection'], round=self.round,
                              visible_to='Agent1', msg_type='format')

    def reset(self):
        self.turn = 0
        self.message_pool.reset()
        self._terminal = False

        if self.phase == 'intent_summarization':
            self.prompt_for_intent_summarization()
        elif self.phase == 'intent':
            self.prompt_for_intent_selection()
        elif self.phase == 'first_order':
            self.prompt_for_intent_guessing()
        elif self.phase == 'hallucination_detection':
            self.prompt_for_hallucination_detection()

        observation = self.get_observation('Agent1')

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
        return 'Agent1'

    def check_game_state(self):
        if self.cur_idx == len(self.ids):
            self._terminal = True

    def prompt_for_intent_summarization_min(self, cur_player, cur_turn, cur_round):
        intent_options = self.build_min_intent_selection_prompt("Player" + str(cur_player), cur_turn, cur_round)
        self._moderator_speak(Moderator_speech['intent_summarization_min'] + intent_options, round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type="intent_summarization_min")
        self._moderator_speak(format_control['intent_summarization_min'], round=cur_round,
                              visible_to='Player' + str(cur_player), msg_type='format')

    def save_results(self, player_name, phase, phase_data):
        ...

    def select_intent(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent'])
        intents = action['Intents']
        thinking = action['Think']
        # answers = action['Answers']

        if self.cur_idx == len(self.ids):
            return
        cur_key = self.ids[self.cur_idx]
        self.reas_intent_data[cur_key]['selected_intents'] = intents
        self.reas_intent_data[cur_key]['thinking'] = thinking

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent', visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent', visible_to=player_name, turn=self.round)
        # message3 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=answers,
        #                    msg_type='answers', visible_to=player_name, turn=self.round)
        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)
        # self.message_pool.append_message(message3)

        self.cur_idx += 1
        self.prompt_for_intent_selection()

    def intent_summarization(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_summarization'])

        intents = action['Intents']
        thinking = action['Think']

        print(intents)

        if self.cur_idx == len(self.ids):
            return
        cur_key = self.ids[self.cur_idx]
        self.intent_sum_data[cur_key]['summarized_intents'] = intents

        # self.save_results(player_name, self.phase, {'intents': intents})

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent_summarization',
                           visible_to=player_name,
                           turn=self.round)
        message2 = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=thinking,
                           msg_type='intent_summarization', visible_to=player_name, turn=0)

        self.message_pool.append_message(message1)
        self.message_pool.append_message(message2)

        self.cur_idx += 1
        if self.cur_idx < len(self.ids):
            self.prompt_for_intent_summarization()

    def first_order(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_guessing'])
        # self.save_results(player_name, self.phase, {'intent_guess': action})

        if 'reasoning' in action.keys():
            del action['reasoning']
        if 'confidence' in action.keys():
            del action['confidence']
        if 'evidence' in action.keys():
            del action['evidence']

        intents = action['intent']

        if self.cur_idx == len(self.ids):
            return
        cur_key = self.ids[self.cur_idx]
        self.ref_con_data[cur_key]['guessed_intents'] = intents

        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=action,
                          msg_type='first_order', visible_to=player_name, turn=0)
        self.message_pool.append_message(message)

        self.cur_idx += 1
        self.prompt_for_intent_guessing()

    def hallucination_detection(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['hallucination_detection'])
        # self.save_results(player_name, self.phase, {'intent_guess': action})

        if 'reasoning' in action.keys():
            del action['reasoning']
        if 'confidence' in action.keys():
            del action['confidence']
        if 'evidence' in action.keys():
            del action['evidence']

        # answer = action['Failed_Quest']
        answer = action['Answer']
        thinking = action['Think']

        if self.cur_idx == len(self.ids):
            return
        cur_key = self.ids[self.cur_idx]
        self.ref_con_data[cur_key]['gpt4o_answer'] = answer
        self.ref_con_data[cur_key]['thinking'] = thinking

        message = Message(agent_name=player_name + "(" + self.name_to_char[player_name] + ")", content=action,
                          msg_type='first_order', visible_to=player_name, turn=0)
        self.message_pool.append_message(message)

        self.cur_idx += 1
        self.prompt_for_hallucination_detection()

    def intent_summarization_min(self, player_name, action):
        action = utils.parse_json_response(response=action, schema=format_control_schemas['intent_summarization_min'])

        intents = action['Intents']
        thinking = action['Think']

        self.save_results(player_name, self.phase, {'intents': intents})

        message1 = Message(agent_name=player_name, content=intents, msg_type='intent_summarization_min',
                           visible_to=player_name,
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

    def step(self, player_name: str, action: str) -> TimeStep:
        print("===============================================================")
        print(f"Phase: {self.phase}, Player: {player_name}")
        print("===============================================================")
        # try:
        self.check_game_state()

        filename = f"{save_path}/summarization_model_results/intent_summarization_results.json"
        if self.phase == "first_order":
            filename = f"{save_path}/guessing_model_results/intent_guessing_results.json"
        if self.phase == "hallucination_detection":
            filename = f"{save_path}/hallucination_detection_model_results/hallucination_detection_results.json"

        if self.phase == 'intent':
            self.select_intent(player_name, action)

        elif self.phase == "first_order":
            self.first_order(player_name, action)
        elif self.phase == 'intent_summarization':
            self.intent_summarization(player_name, action)
        elif self.phase == 'intent_summarization_min':
            self.intent_summarization_min(player_name, action)
        elif self.phase == "hallucination_detection":
            self.hallucination_detection(player_name, action)

        with open(filename, "w") as file:
            if self.phase == "intent_summarization":
                json.dump(self.intent_sum_data, file)
            else:
                json.dump(self.ref_con_data, file)

        return TimeStep(observation=self.get_observation(player_name), reward=self.get_zero_rewards(),
                        terminal=self._terminal)


def read_data(file):
    with open(file) as f:
        data = json.load(f)
    return data


def convert_list_to_dict(list_of_dicts):
    dict_from_list = {item['id']: item for item in list_of_dicts}
    return dict_from_list


if __name__ == "__main__":

    intent_guessing_data_path = f"{config_utils.get_config_value('structured_context_save_path')}/guessing_data/intent_guessing_all.json"
    hallucination_detection_data_path = f"{config_utils.get_config_value('hallucination_detection_save_path')}/hallucination_detection.json"
    intent_sum_data_path = f"{config_utils.get_config_value('structured_context_save_path')}/summarization_data/intent_summarization_all.json"
    is_openai_model = config_utils.get_config_value("is_openai_model")
    model_name = config_utils.get_config_value("model_name")
    phase = config_utils.get_config_value("evaluation_phase")
    save_path = config_utils.get_config_value("model_evaluation_save_path")

    if not os.path.exists(f"{save_path}/summarization_model_results"):
        os.makedirs(f"{save_path}/summarization_model_results")
    if not os.path.exists(f"{save_path}/guessing_model_results"):
        os.makedirs(f"{save_path}/guessing_model_results")
    if not os.path.exists(f"{save_path}/hallucination_detection_model_results"):
        os.makedirs(f"{save_path}/hallucination_detection_model_results")

    ref_con_data = convert_list_to_dict(read_data(intent_guessing_data_path))
    hallucination_detection_data = convert_list_to_dict(read_data(hallucination_detection_data_path))
    intent_sum_data = convert_list_to_dict(read_data(intent_sum_data_path))

    players_no = [1]
    characters = ['Evaluator']
    players = {}
    character_to_player = {}
    shuffled_players = random.sample(players_no, 1)
    for index, player_no in enumerate(shuffled_players):
        players['Agent' + str(player_no)] = characters[index]
        character_to_player['Evaluator'] = 'Agent' + str(player_no)

    if is_openai_model:
        if model_name == "o1-preview-2024-09-12":
            backend = OpenAIChat(model=model_name, supports_system_prompt=False, eval_mode=True)
        else:
            backend = OpenAIChat(model=model_name)
    else:
        backend = LLamaChat()

    agent1 = Player(name='Agent1',
                    role_desc='You are a player in the Avalon game and your goal is to win the game according to game rules.',
                    global_prompt=game_description, backend=backend)

    env = Avalon(
        phase,
        character_to_player,
        players,
        hallucination_detection_data,
        ref_con_data,
        {},
        intent_sum_data,
        save_path
    )
    arena = Arena([agent1], env)
    arena.launch_cli(interactive=False, output_file="output/evaluation_run")
