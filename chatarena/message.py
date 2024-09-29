from typing import List, Union
from dataclasses import dataclass
import time
from uuid import uuid1
import hashlib
from collections import  defaultdict

# Preserved roles
SYSTEM_NAME = "System"
MODERATOR_NAME = "Moderator"


def _hash(input: str):
    """
    Helper function that generates a SHA256 hash of a given input string.

    Parameters:
        input (str): The input string to be hashed.

    Returns:
        str: The SHA256 hash of the input string.
    """
    hex_dig = hashlib.sha256(input.encode()).hexdigest()
    return hex_dig


@dataclass
class Message:
    """
    Represents a message in the chatArena environment.

    Attributes:
        agent_name (str): Name of the agent who sent the message.
        content (str): Content of the message.
        turn (int): The turn at which the message was sent.
        timestamp (int): Wall time at which the message was sent. Defaults to current time in nanoseconds.
        visible_to (Union[str, List[str]]): The receivers of the message. Can be a single agent, multiple agents, or 'all'. Defaults to 'all'.
        msg_type (str): Type of the message, e.g., 'text'. Defaults to 'text'.
        logged (bool): Whether the message is logged in the database. Defaults to False.
    """
    agent_name: str
    content: str
    turn: int
    timestamp: int = time.time_ns()
    visible_to: Union[str, List[str]] = 'all'
    msg_type: str = "text"
    logged: bool = False  # Whether the message is logged in the database

    @property
    def msg_hash(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(
            f"agent: {self.agent_name}\ncontent: {self.content}\ntimestamp: {str(self.timestamp)}\nturn: {self.turn}\nmsg_type: {self.msg_type}")


class MessagePool():
    """
    A pool to manage the messages in the chatArena environment.

    The pool is essentially a list of messages, and it allows a unified treatment of the visibility of the messages.
    It supports two configurations for step definition: multiple players can act in the same turn (like in rock-paper-scissors).
    Agents can only see the messages that 1) were sent before the current turn, and 2) are visible to the current role.
    """

    def __init__(self, eval_mode: bool = False):
        """
        Initialize the MessagePool with a unique conversation ID.
        """
        self.conversation_id = str(uuid1())
        self._messages: List[Message] = []  # TODO: for the sake of thread safety, use a queue instead
        self._last_message_idx = 0
        self.eval_mode = eval_mode

    def reset(self):
        """
        Clear the message pool.
        """
        self._messages = []

    def append_message(self, message: Message):
        """
        Append a message to the pool.

        Parameters:
            message (Message): The message to be added to the pool.
        """
        self._messages.append(message)

    def print(self):
        """
        Print all the messages in the pool.
        """
        for message in self._messages:
            print(f"[{message.agent_name}->{message.visible_to}]: {message.content}")

    @property
    def last_turn(self):
        """
        Get the turn of the last message in the pool.

        Returns:
            int: The turn of the last message.
        """
        if len(self._messages) == 0:
            return 0
        else:
            return self._messages[-1].turn

    @property
    def last_message(self):
        """
        Get the last message in the pool.

        Returns:
            Message: The last message.
        """
        if len(self._messages) == 0:
            return None
        else:
            return self._messages[-1]

    def get_all_messages(self) -> List[Message]:
        """
        Get all the messages in the pool.

        Returns:
            List[Message]: A list of all messages.
        """
        return self._messages

    def get_visible_messages(self, agent_name, turn: int, phase: str) -> List[Message]:
        """
        Get all the messages that are visible to a given agent before a specified turn.

        Parameters:
            agent_name (str): The name of the agent.
            turn (int): The specified turn.

        Returns:
            List[Message]: A list of visible messages.
        """

        # Get the messages before the current turn
        prev_messages = [message for message in self._messages]

        if self.eval_mode:
            msgs = prev_messages[-2:]
            return msgs

        max_turn = 0
        visible_messages = defaultdict(list)
        role_tips_included = False
        for index, message in enumerate(prev_messages):
            max_turn = max(message.turn, max_turn)
            # exclusions
            if message.msg_type == 'intent_evaluation' and index != len(prev_messages) - 2:
                continue
            if phase == 'summary' and message.msg_type in ('first_order', 'second_order', 'formulation_con', 'intent_summarization', 'intent_summarization_min', 'intent_evaluation', 'selected_intent_evaluation'):
                continue
            if (phase in ['intent_summarization', 'intent_summarization_min', 'intent_evaluation', 'selected_intent_evaluation']) and message.msg_type == 'intent':
                continue
            # if (phase in ['action']) and (message.msg_type == 'intent' or message.msg_type == 'intent_category'):
            #     continue
            # if message.msg_type == 'role_tips' and role_tips_included:
            #     continue
            # if (phase != 'intent_modification') and message.msg_type == 'intent_modification':
            #     continue
            # if (phase != 'first_order') and message.msg_type == 'first_order' and message.agent_name == 'Moderator':
            #     continue
            # if phase == 'first_order' and message.msg_type == 'first_order' and message.agent_name == 'Moderator' and index != len(prev_messages) - 2:
            #     continue
            if message.msg_type == 'first_order' and message.agent_name == 'Moderator' and index != len(prev_messages) - 2:
                message.content = "Analyze roles of other players based on game dialogues and past actions."
            # if message.msg_type == 'first_order' and phase != 'first_order':
            #     continue
            if phase != 'intent_summarization' and message.msg_type == 'intent_summarization':
                continue
            if phase != 'intent_summarization_min' and message.msg_type == 'intent_summarization_min':
                continue

            if message.msg_type == 'format' and agent_name in message.visible_to:
                if index == len(prev_messages)-1:
                    visible_messages[message.turn].append(message)
                continue
            if message.turn == 0 and agent_name in message.visible_to:
                visible_messages[message.turn].append(message)
                if message.msg_type == 'role_tips':
                    role_tips_included = True
            elif message.turn != turn and message.turn != 1:
                if message.msg_type == 'summary' and agent_name in message.visible_to:
                    visible_messages[message.turn].append(message)
                    if message.msg_type == 'role_tips':
                        role_tips_included = True
                elif phase == 'assassin' and message.msg_type == 'first_order' and agent_name in message.visible_to:
                    visible_messages[message.turn].append(message)
            elif message.visible_to == "all" or agent_name in message.visible_to or agent_name == "Moderator":
                if message.msg_type == "summary":
                    visible_messages[message.turn] = []
                visible_messages[message.turn].append(message)
                if message.msg_type == 'role_tips':
                    role_tips_included = True

        visible_messages_list = []
        for turn in range(max_turn + 1):
            visible_messages_list.extend(visible_messages[turn])

        return visible_messages_list
