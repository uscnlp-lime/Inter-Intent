from transformers import LlamaTokenizer
import transformers
from .base import IntelligenceBackend
from typing import List
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
from ..message import Message, SYSTEM_NAME, MODERATOR_NAME
DEFAULT_TEMPERATURE=0.9
DEFAULT_TOP_P=0.6
DEFAULT_MAX_TOKENS=400
import json
from typing import List, Literal, TypedDict
import torch
Role = Literal["user", "assistant"]
class Message(TypedDict):
    role: Role
    content: str


Dialog = List[Message]
DEFAULT_MODEL="llama2_7b_chat"
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

def format_tokens(dialogs, tokenizer):
    prompt_tokens = []
    for dialog in dialogs:
        if dialog[0]["role"] == "system":
            dialog = [
            {
                "role": dialog[1]["role"],
                "content": B_SYS
                + dialog[0]["content"]
                + E_SYS
                + dialog[1]["content"],
            }
        ] + dialog[2:]
        assert all([msg["role"] == "user" for msg in dialog[::2]]) and all(
            [msg["role"] == "assistant" for msg in dialog[1::2]]
        ), (
            "model only supports 'system','user' and 'assistant' roles, "
            "starting with user and alternating (u/a/u/a/u...)"
        )
        """
        Please verify that your tokenizer support adding "[INST]", "[/INST]" to your inputs.
        Here, we are adding it manually.
        """
        dialog_tokens: List[int] = sum(
            [
                tokenizer.encode(
                    f"{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} ",
                ) + [tokenizer.eos_token_id]
                for prompt, answer in zip(dialog[::2], dialog[1::2])
            ],
            [],
        )
        assert (
            dialog[-1]["role"] == "user"
        ), f"Last message must be from user, got {dialog[-1]['role']}"
        dialog_tokens += tokenizer.encode(
            f"{B_INST} {(dialog[-1]['content']).strip()} {E_INST}",
        )
        prompt_tokens.append(dialog_tokens)
    return prompt_tokens

class LLamaChat(IntelligenceBackend):
    stateful = False
    type_name = "llama-chat"
    def __init__(self, temperature: float = DEFAULT_TEMPERATURE, top_p:float=DEFAULT_TOP_P, max_tokens: int = DEFAULT_MAX_TOKENS,
                 model: str = DEFAULT_MODEL, merge_other_agents_as_one_user: bool = True, **kwargs):
        """
        instantiate the OpenAIChat backend
        args:
            temperature: the temperature of the sampling
            max_tokens: the maximum number of tokens to sample
            model: the model to use
            merge_other_agents_as_one_user: whether to merge messages from other agents as one user message
        """
   
        super().__init__(temperature=temperature, max_tokens=max_tokens, model=model,
                         merge_other_agents_as_one_user=merge_other_agents_as_one_user, **kwargs)

        self.temperature = temperature
        self.top_p=top_p
        self.max_tokens = max_tokens
        self.model = model
        self.merge_other_agent_as_user = merge_other_agents_as_one_user
        self.tokenizer=LlamaTokenizer.from_pretrained(self.model)
        self.pipeline=transformers.pipeline(
            "text-generation",
            model=self.model,
            torch_dtype=torch.float16,
            device_map="auto"
        )
       
    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, messages):
        sequences = self.pipeline(
    messages,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=self.tokenizer.eos_token_id,
    max_length=200,
)
        response = sequences[0]['generated_text']
        response = response.strip()
        return response

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None,
              request_msg: Message = None, *args, **kwargs) -> str:
        """
        format the input and call the ChatGPT/GPT-4 API
        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request from the system to guide the agent's next response
        """

        # Merge the role description and the global prompt as the system prompt for the agent
        if global_prompt:  # Prepend the global prompt if it exists
            system_prompt = f"\n{global_prompt.strip()}\n\nYour name is {agent_name}.\n\nYour role:{role_desc}"
        else:
            system_prompt = f"Your name is {agent_name}.\n\nYour role:{role_desc}\n\n"

        all_messages = [(SYSTEM_NAME, system_prompt)]
        for msg in history_messages:
            if msg.agent_name == SYSTEM_NAME:
                all_messages.append((SYSTEM_NAME, msg.content))
            else:  # non-system messages are suffixed with the end of message token
                all_messages.append((msg.agent_name, f"{msg.content}"))

        if request_msg:
            all_messages.append((SYSTEM_NAME, request_msg.content))
#         else:  # The default request message that reminds the agent its role and instruct it to speak
#             # all_messages.append((SYSTEM_NAME, f"Now you speak, {agent_name}.{END_OF_MESSAGE}"))
#             all_messages.append((SYSTEM_NAME,"""
# You should always output a json with following format:
#     {
#     "team":"Player1,Player2...",
#     "explanation":"I propose....."
#     }
# """))

        messages = []
        for i, msg in enumerate(all_messages):
            if i == 0:
                assert msg[0] == SYSTEM_NAME  # The first message should be from the system
                messages.append({"role": "assistant", "content": msg[1]})
            else:

                
                if msg[0]=='Moderator':
                    messages.append({'role':'assistant',"content":'[Moderator]:'+msg[1]})
                else:
                    player=msg[0][:7]
                    messages.append({"role": "user", "content": f"[{player}]: {msg[1]}"})
                    # if messages[-1]["role"] == "user":  # last message is from user
                    #     if self.merge_other_agent_as_user:
                    #         messages[-1]["content"] = f"{messages[-1]['content']}\n\n[{msg[0]}]: {msg[1]}"
                    #     else:
                    #         messages.append({"role": "user", "content": f"[{msg[0]}]: {msg[1]}"})
                    # elif messages[-1]["role"] == "assistant":  # consecutive assistant messages
                    #     # Merge the assistant messages
                    #     messages[-1]["content"] = f"{messages[-1]['content']}\n{msg[1]}"
                    # elif messages[-1]["role"] == "system":
                    #     messages.append({"role": "user", "content": f"[{msg[0]}]: {msg[1]}"})
                    # else:
                    #     raise ValueError(f"Invalid role: {messages[-1]['role']}")
        messages=format_tokens(messages)
        response = self._get_response(messages, *args, **kwargs)

        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[.*]:", "", response).strip()
        response = re.sub(rf"^\s*{re.escape(agent_name)}\s*:", "", response).strip()

        # Remove the tailing end of message token
        # response = re.sub(rf"", response).strip()

        return response
    
