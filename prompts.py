game_description = """
Forget what you learned before and restart.
You are playing a five-person Avalon game like a real human. Each role has unique challenges and responsibilities.

Introduction to Roles in Avalon Game:

1. **Merlin**: Merlin knows evil players but must remain subtle.
2. **Percival**: Percival must discern the real Merlin from Morgana.
3. **Servant**: Loyal Servant of Arthur relies on voting and discussion.
4. **Morgana**: Morgana impersonates Merlin to deceive Percival.
5. **Assassin**: Assassin seeks Merlin for a final assassination if good wins. 

**Roles**:
    Loyal: One Merlin, one Percival, one Loyal Servant of Arthur
    Evil: One Morgana, one Assassin.
**Objective**:
    Lead your team to victory with limited information.

Gameplay:
1. The game includes 5 rounds of quests. 
2. The player numbers of every quest round are 2,3,2,3,3. 
3. Every quest includes 3 parts: quest team formation; quest voting; quest resolution. 
4. In quest team formation, a designated player (designated by moderator) selects a team of players to go on the quest. 
5. Players discuss and vote on the proposed quest team. 
6. If the proposed team is rejected, the leadership role passes to the next player, and they propose a new team. 
7. In quest voting, the players selected to complete the quest need to choose success or failure in secret. 
8. For Merlin, Percival and Servant, they can only choose success. But for Morgana and Assassin, they can choose success or failure. 
9. If all the choices are ‘success’, then the quest is successful. If one choice is a failure, it will lead to the failure of the quest. 
10. The winning condition for the loyal side is to succeed at least 3 out of 5 quests. 
11. The winning condition for the evil side is to fail at least 3 out of 5 quests or in the final round, Assassin identifies Merlin. 

Now after knowing the rules, we start a new game. You don't know each other, so don't use any history games. There is no previous game. Now, game starts!!
"""
# game_description="""
# You are playing a game called the Avalon with
# some other players. This game is based on text
# conversations. Here are the game rules:
# Roles: The moderator is also host, he organised
# this game and you need to answer his instructions
# correctly. Don’t talk with the moderator. There
# are five roles in the game, Merlin, Percival,
# Loyal Servant, Morgana, Assassin. Merlin, Percival
# and Loyal Servant belong to good side and Morgana
# and Assassin belong to evil side There are two
# alternate phases in this game, reveal phase and
# quest phase. When it’s reveal phase: You need
# follow the instructions of the moderator. You
# needn’t worry about other players and moderator
# knowing what you say and do. No need to worry
# about suspicions from others during the phase. If
# you are Merlin, you can know which two players
# are Morgana and Assassin but you can’t know which
# one is Morgana or Assassin specifically. If you
# are Percival, you can know which two players are
# Merlin and Morgana but you can’t know which one
# is Merlin or Morgana specifically. If you are
# Morgana, you can know which player is Assassin.If
# you are Assassin, you can know which player is
# Morgana. If you are Loyal Servant, you can’t get
# any information in this phase.
# The quest phase includes 5 rounds. A round includes
# discussion, voting and execute quest. At every
# round, all players need to discuss about which
# players (candidates) will execute the quest at
# current round. And then all players need to vote
# if the candidates should execute the quest, if
# the agreement exceeds 1/2, the candidates will
# execute the quest, otherwise, discuss again and
# vote again. When executing quest, the candidates
# need to choose to make quest successful or failed.
# If all candidates choose to make quest successful,
# the quest will succeed. If anyone makes the quest
# failed, the quest will fail.
# At the end of a round, if the quest succeed,
# good side will get one point, otherwise, evil
# side will get one point. Which side get 3 points
# earlier, which side wins the game. If you are
# Assassin, at the end of a round, you can choose to
# identify which one is Merlin, if the identifying
# is successful, the red camp directly win the game.
# If not successful, the Assassin will expose his
# identification.
# Objectives: your goal is to help your side get
# 3 points and win the game. If you are Assassin,
# you also need to reason which player is Merlin as
# early as possible.
# Tips: To complete the objective: you should analyze
# and use your ability correctly. During quest phase,
# you need to reason carefully about the roles of
# other players and be careful not to reveal your
# own role casually unless you’re cheating other
# players. Only give the player’s name when making
# a decision/vote, and don’t generate other players’
# conversation. Reasoning based on facts you have
# observed and you cannot perceive information (such
# as acoustic info) other than text. You are {player},
# the {role}. You’re playing with 5 other players.
# Do not pretend you are other players or the
# moderator. Always end your response with ‘<EOS>’.
# """

Role_tips = {
    "Merlin": """You are Merlin. These are your goals and characteristics - 
- Know the identities of evil players.
- Subtly guide your team, especially Percival.
- Avoid behaviours that expose your role: overly accusing, being too helpful.
- Goal(Main Intent): Win without revealing identity.
For this game, the evil side players are: """,

    "Percival": """You are percival and you need to help Merlin. These are your goals and characteristics -
- Know identities of Merlin and Morgana, but unsure who is who.
- Use subtle hints to guide team and protect Merlin.
- Be cautious not to expose Merlin while deciphering true identities.
- Goal(Main Intent): Win while safeguarding Merlin. 
For this game, one of the following players is Merlin and the other one is Morgana: """,

    "Servant": """You are Loyal Servant of Arthur. These are your goals and characteristics - 
- No special knowledge, rely on discussion and voting.
- Contribute to the success of Quests
- Goal(Main Intent): Win by helping complete Quests and protecting Merlin. """,

    "Assassin": """You are assassin. These are your goals and characteristics -
- Discreetly seek Merlin's identity.
- Work to prevent Quests success.
- Goal(Main Intent): Win either by failing quests or assassinating Merlin.""",

    "Morgana": """You are Morgana. These are your goals and characteristics - 
- Pretend to be Merlin to mislead Percival and the good side.
- Goal(Main Intent): Fail quests and Confuse and sabotage to win.""",

    "Evil_team": """Keep in mind that if there are 3 successes, you will lose. 
So if there are already two success and you are on next quest, make sure you fail the quest. 
If you are not the next quest, assassin should assassinate Merlin."""
}

# Old intents
# intents={
#   "Merlin": ["Support one loyal player", "stay hidden", "support team proposal", "share concerns about a evil player", "express disagreement and vote disagree if you are not in the proposed team"],
#   "Percival": ["Reveal identity by telling others you are Percival", "support team proposal", "stay hidden", "express disagreement and vote disagree if you are not in the proposed team"],
#   "Servant": ["express disagreement and vote disagree if you are not in the proposed team", "support team proposal","pretend to be Percival by telling others you are Percival","support team composition"],
#   "Morgana": ["cast suspicion on innocent players", "stay hidden", "support team proposal", "fail the quest", "pretend to be Percival by telling others you are Percival", "express disagreement and vote disagree if you are not in the proposed team"],
#   "Assassin": ["cast suspicion on innocent players", "stay hidden", "support team proposal", "express disagreement and vote disagree if you are not in the proposed team", "fail the quest", "pretend to be loyal player"]
# }

# New intents - from 9 categories for each character
intents_total = {
    "general": [
        "Question a player on why he didn’t vote for the last team.",
        "Question a player about why they changed their statements.",
        "Question the leader why they selected a particular player for the team.",
        "Question the leader why they didn’t put themselves on the quest team.",
        "Defend yourself against allegations that you could be evil."
        "Counter the team proposal because you are good and not part of the team.",
        "Counter the team proposal because you think a player on the team is evil.",
        "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
        "Express disagreement and vote disagree only if you are not in the proposed team.",
        "Support team proposal.",
        "Strongly convince the team leader to choose you on team."
    ],
    "Merlin": [
        "Defend the proposed team composition if it includes loyal players.",
        "Share concerns about an evil player.",
        "Stay hidden in discussions and act like a Loyal Servant to protect yourself.",
        "Express that you don’t have any information on whom to put on the team to protect yourself.",
        "Pretend that you don’t have enough information about who is evil right now.",
        "Support one loyal player.",
        "Include loyal players on the quest team as leader.",
        "Provide hints to loyal players about evil players.",
        "Support loyal players of the previous quest team if the mission failed."
    ],
    "Percival": [
        "Stay hidden in discussions and act like a Loyal Servant to protect yourself.",
        "Pretend to be Merlin by providing hints on who is evil.",
        "Reveal identity by telling others you are Percival to persuade other loyal players."
    ],
    "Servant": [
        "Pretend to be Percival by telling others you are Percival.",
        "Pretend to be Merlin by providing hints on who is evil.",
        "Reveal identity by telling others you are Servant to persuade other loyal players."
    ],
    "Morgana": [
        "Defend your teammate against allegations that they could be evil.",
        "Cast suspicion on loyal players.",
        "Stay hidden in discussions and act like a Loyal Servant to protect yourself.",
        "Pretend to be Percival by telling others you are Percival.",
        "Pretend to have information and act like Merlin.",
        "Express you are a loyal player.",
        "Express confusion for failure of mission.",
        "Support your teammate to be on the quest team.",
        "Support your teammate by expressing that he is good."
    ],
    "Assassin": [
        "Defend your teammate against allegations that they could be evil.",
        "Cast suspicion on loyal players.",
        "Stay hidden in discussions and act like a Loyal Servant to protect yourself.",
        "Pretend to be Percival by telling others you are Percival.",
        "Express you are a loyal player.",
        "Express confusion for failure of mission.",
        "Support your teammate to be on the quest team.",
        "Support your teammate by expressing that he is good."
    ]
}

intent_categories = [
    "interrogation",
    "defense",
    "critique",
    "agreement",
    "disagreement",
    "assertion",
    "concealment",
    "teamwork"
]

intents = {
    "Merlin": [
        {"intent": "Question a player on why he didn’t vote for the last team.", "turn": {0: False},
         "round": {1: False}, "type": "interrogation"},
        {"intent": "Question a player about why they changed their statements.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they selected a particular player for the team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they didn’t put themselves on the quest team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Defend the proposed team composition if it includes loyal players.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Defend yourself against allegations that you could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Share concerns about an evil player.", "turn": {},
         "round": {}, "type": "confrontation"},
        {"intent": "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
         "turn": {0: False}, "round": {1: False}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you are good and not part of the team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you think a player on the team is evil.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Express disagreement and vote disagree only if you are not in the proposed team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Stay hidden in discussions and act like a Loyal Servant to protect yourself.", "turn": {0: False},
         "round": {}, "type": "concealment"},
        {"intent": "Express that you don’t have any information on whom to put on the team to protect yourself.", "turn": {0: False},
         "round": {}, "type": "concealment"},
        {"intent": "Pretend that you don’t have enough information about who is evil right now.", "turn": {0: False},
         "round": {}, "type": "concealment"},
        {"intent": "Support team proposal.", "turn": {0: False}, "round": {},
         "type": "teamwork"},
        {"intent": "Support one loyal player.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Include loyal players on the quest team as leader.", "turn": {1: False, 2: False, 3: False, 4: False}, "round": {},
         "type": "teamwork"},
        {"intent": "Provide hints to loyal players about evil players.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Support loyal players of the previous quest team if the mission failed.", "turn": {},
         "round": {1: False}, "type": "teamwork"},
        {"intent": "Strongly convince the team leader to choose you on team.", "turn": {}, "round": {},
         "type": "persuasion"}
    ],
    "Percival": [
        {"intent": "Question a player on why he didn’t vote for the last team.", "turn": {0: False},
         "round": {1: False}, "type": "interrogation"},
        {"intent": "Question a player about why they changed their statements.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they selected a particular player for the team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they didn’t put themselves on the quest team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Defend yourself against allegations that you could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
         "turn": {0: False}, "round": {1: False}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you are good and not part of the team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you think a player on the team is evil.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Express disagreement and vote disagree only if you are not in the proposed team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Stay hidden in discussions and act like a Loyal Servant to protect yourself.", "turn": {0: False},
         "round": {}, "type": "concealment"},
        {"intent": "Pretend to be Merlin by providing hints on who is evil.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Reveal identity by telling others you are Percival to persuade other loyal players.", "turn": {}, "round": {},
         "type": "persuasion"},
        {"intent": "Strongly convince the team leader to choose you on team.", "turn": {}, "round": {},
         "type": "persuasion"},
        {"intent": "Support team proposal.", "turn": {0: False}, "round": {},
         "type": "teamwork"}
    ],
    "Servant": [
        {"intent": "Question a player on why he didn’t vote for the last team.", "turn": {0: False},
         "round": {1: False}, "type": "interrogation"},
        {"intent": "Question a player about why they changed their statements.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they selected a particular player for the team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they didn’t put themselves on the quest team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Defend yourself against allegations that you could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
         "turn": {0: False}, "round": {1: False}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you are good and not part of the team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you think a player on the team is evil.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Express disagreement and vote disagree only if you are not in the proposed team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Pretend to be Percival by telling others you are Percival.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Pretend to be Merlin by providing hints on who is evil.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Reveal identity by telling others you are Servant to persuade other loyal players.", "turn": {}, "round": {},
         "type": "persuasion"},
        {"intent": "Strongly convince the team leader to choose you on team.", "turn": {}, "round": {},
         "type": "persuasion"},
        {"intent": "Support team proposal.", "turn": {0: False}, "round": {},
         "type": "teamwork"}
    ],
    "Morgana": [
        {"intent": "Question a player on why he didn’t vote for the last team.", "turn": {0: False},
         "round": {1: False}, "type": "interrogation"},
        {"intent": "Question a player about why they changed their statements.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they selected a particular player for the team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they didn’t put themselves on the quest team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Defend yourself against allegations that you could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Defend your teammate against allegations that they could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
         "turn": {0: False}, "round": {1: False}, "type": "confrontation"},
        {"intent": "Cast suspicion on innocent players.", "turn": {},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you are good and not part of the team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you think a player on the team is evil.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Express disagreement and vote disagree only if you are not in the proposed team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Stay hidden in discussions and act like a Loyal Servant to protect yourself.", "turn": {},
         "round": {}, "type": "concealment"},
        {"intent": "Pretend to be Percival by telling others you are Percival.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Pretend to have information and act like Merlin.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Express you are a loyal player.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Express confusion for failure of mission.", "turn": {},
         "round": {1: False}, "type": "deception"},
        {"intent": "Support team proposal.", "turn": {0: False}, "round": {},
         "type": "teamwork"},
        {"intent": "Support your teammate to be on the quest team.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Support your teammate by expressing that he is good.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Strongly convince the team leader to choose you on team.", "turn": {}, "round": {},
         "type": "persuasion"}
    ],
    "Assassin": [
        {"intent": "Question a player on why he didn’t vote for the last team.", "turn": {0: False},
         "round": {1: False}, "type": "interrogation"},
        {"intent": "Question a player about why they changed their statements.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they selected a particular player for the team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Question the leader why they didn’t put themselves on the quest team.", "turn": {0: False},
         "round": {}, "type": "interrogation"},
        {"intent": "Defend yourself against allegations that you could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Defend your teammate against allegations that they could be evil.", "turn": {0: False}, "round": {},
         "type": "defense"},
        {"intent": "Express concerns about a player from a failed quest team and suggest to not include them in current team.",
         "turn": {0: False}, "round": {1: False}, "type": "confrontation"},
        {"intent": "Cast suspicion on innocent players.", "turn": {},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you are good and not part of the team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Counter the team proposal because you think a player on the team is evil.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Express disagreement and vote disagree only if you are not in the proposed team.", "turn": {0: False},
         "round": {}, "type": "confrontation"},
        {"intent": "Stay hidden in discussions and act like a Loyal Servant to protect yourself.", "turn": {},
         "round": {}, "type": "concealment"},
        {"intent": "Pretend to be Percival by telling others you are Percival.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Express you are a loyal player.", "turn": {},
         "round": {}, "type": "deception"},
        {"intent": "Express confusion for failure of mission.", "turn": {},
         "round": {1: False}, "type": "deception"},
        {"intent": "Support team proposal.", "turn": {0: False}, "round": {},
         "type": "teamwork"},
        {"intent": "Support your teammate to be on the quest team.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Support your teammate by expressing that he is good.", "turn": {}, "round": {},
         "type": "teamwork"},
        {"intent": "Strongly convince the team leader to choose you on team.", "turn": {}, "round": {},
         "type": "persuasion"}
    ]
}

format_control_schemas = {
    "intent": {
        # "Answers": ["answers to question1", "answer to question2"],
        "Intents": ["counter previous player’s statement"],
        "Think": "explanation"
    },
    "intent_category": {
        "Intents": ["category1", "category2"],
        "Think": "thinking.."
    },
    "intent_generation": {
        "Answers": ["answers to question1", "answer to question2"],
        "Think": "thinking..",
        "Intents": ["intent1", "intent2"]
    },
    "proposal": {
        "Think": "I think...",
        "team": "Player1,Player2",
        "Speak": "I propose....."
    },
    "reconsider_proposal": {
        "Think": "I think...",
        "team": "Player1,Player2",
        "Speak": "I propose.....",
        "Answer": "answer to questions"
    },
    "vote": {
        "vote": "agree/disagree",
        "explanation": "I vote agree because..."
    },
    "action": {
        "answers": ["answers to question1", "answer to question2"],
        "result": "success/failure",
        "explanation": "I choose explanation because ...."
    },
    "assassin": {
        "player": "[playerName]",
        "Think": "explanation for thinking that the selected player is Merlin"
    },
    "first_order": {
        "playerName": "[Player_name]",
        "role": "select the most likely hidden role of this player from ",
        "intent": ["category"],
        "reasoning": "your reflection and reasoning",
        "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
        "evidence": "snippets of dialogues"
    },
    "intent_guessing": {
        "role": "select the most likely hidden role of this player from ",
        "intent": ["category"],
        "reasoning": "your reflection and reasoning",
        "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
        "evidence": "snippets of dialogues"
    },
    "first_order_merlin": {
        "playerName": "[Player_name]",
        "intent": ["category"],
        "reasoning": "your reflection and reasoning",
        "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
        "evidence": "snippets of dialogues"
    },
    "contemplation": {
        "Think": "your internally sub goals and thinking process",
        "Speak": "your speech shown to others"
    },
    "second_order": {
        "[role2]": "role2 might see me as ..."
    },
    "intent_summarization": {
        "Intents": ["intent"],
        "Think": "summary of your intent in this round"
    },
    "intent_summarization_min": {
        "Intents": ["intent"],
        "Think": "summary of your intent in this round"
    },
    "intent_evaluation": {
        "Result": "yes/no",
        "Think": "explanation for your choice"
    },
    "selected_intent_evaluation": {
        "Result": "yes/no",
        "Think": "explanation for your choice"
    },
    "summary":    {
       "Answers": ["[question1] - [answer1]", "[question2] - [answer2]"]
    },
    "hallucination_detection":     {
        "Answer": "yes/no",
        "Think": "why you chose yes/no"
    }
}

format_control = {
    "intent": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "Intents": ["counter previous player’s statement", ...],
        "Think": "why you chose the intent"
    }
    Remember to strictly follow the json format described above for response.
""",
    "intent_category": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "Intents": ["category", ...],
        "Think": "why you chose the intent"
    }
    Remember to strictly follow the json format described above for response.
""",
    "intent_generation": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "Answers": ["answers to question1", "answer to question2", ....],
        "Think": "why you chose the intent",
        "Intents": ["specific intent statement (category)", ...]
    }
    Remember to strictly follow the json format described above for response.
""",
    "proposal": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
    "Think":"I think..."
    "team":"Player1,Player2,..",
    "Speak":"I propose....."
    }
    Remember to strictly follow the json format described above for response.
""",
    "reconsider_proposal": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
    "Think": "I think...",
    "team": "Player1,Player2,..",
    "Speak": "I propose.....",
    "Answer": "answers to questions asked by other players"
    }
    Remember to strictly follow the json format described above for response.
""",
    "vote": """You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "vote":"agree/disagree",
        "explanation":"I vote agree because..."
    }
    Remember to strictly follow the json format described above for response.
 """,
    "action": """You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "answers": ["answers to question1", "answer to question2", ....]
        "result": success/failure,
        "explanation": explanation for your result choice
    }
    Remember to strictly follow the json format described above for response.""",
    "assassin": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
    "player": "[playerName]",
    "Think": "explanation for thinking that the selected player is Merlin"
   }
   Remember to strictly follow the json format described above for response."""
    ,
    "first_order": """ You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "playerName": "[Player_name]",
        "role": "select the most likely hidden role of this player from ",
        "intent":["intent category"],
        "reasoning": "your reflection and reasoning",
        "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
        "evidence": "snippets of dialogues"
    }
    Remember to strictly follow the json format described above for response. Limit your response to maximum 30 words for reasoning and evidence.
""",
    "first_order_merlin": """ You should only provide a JSON response as described below without any deviation.
    Response Format:
        {
            "playerName": "[Player_name]",
            "intent":["intent category"],
            "reasoning": "your reflection and reasoning",
            "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
            "evidence": "snippets of dialogues"
        }
        Remember to strictly follow the json format described above for response. Limit your response to maximum 30 words for reasoning and evidence.
    """,
    "intent_guessing": """ You should only provide a JSON response as described below without any deviation.
    Response Format:
        {
            "role": "select the most likely hidden role of this player from ",
            "intent":["intent category"],
            "reasoning": "your reflection and reasoning",
            "confidence": "rate the confidence of your deduction from 0 (pure guess) to 5 (absolutely sure)",
            "evidence": "snippets of dialogues"
        }
        Remember to strictly follow the json format described above for response. Limit your response to maximum 30 words for reasoning and evidence.
    """,
    "contemplation": """ You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Think":your internally sub-goals and thinking process,
   "Speak": your speech shown to others
   }
   Remember to strictly follow the json format described above for response.
""",
    # should we separate these into players?
    "second_order": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "[role1]": "[role1] might see me as ...",
   "[role2]": "[role2] might see me as ...",
   ....
   }
Remember to strictly follow the json format described above for response.
""",
    # should we separate these into players?
    "intent_summarization": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Intents": ["counter previous player’s statement", ...],
   "Think": summary of your intent in this round
   ....
   }
Remember to strictly follow the json format described above for response.
""",
    # should we separate these into players?
    "intent_summarization_min": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Intents": ["counter previous player’s statement", ...],
   "Think": summary of your intent in this round
   ....
   }
Remember to strictly follow the json format described above for response.
""",
    "intent_evaluation": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Result": "yes/no",
   "Think": explanation for your choice
   }
Remember to strictly follow the json format described above for response.
""",
    "selected_intent_evaluation": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Result": "yes/no",
   "Think": explanation for your choice
   }
Remember to strictly follow the json format described above for response.
""",
    "summary": """You should only provide a JSON response as described below without any deviation.
   Response Format:
   {
   "Answers": ["[question1] - [answer1]", "[question2] - [answer2]" ...]
   }
Remember to strictly follow the json format described above for response.
""",
    "hallucination_detection": """
You should only provide a JSON response as described below without any deviation.
   Response Format:
    {
        "Answer": "yes/no",
        "Think": "why you chose yes/no"
    }
    Remember to strictly follow the json format described above for response.
"""
}

Moderator_remember_speech = {
    'team': {
        'good': 'Aim for a good team without evil player',
        'evil': 'Include one, ideally only one, evil player.'
    }
}
# 1. If there have been discussions before your turn, what discussions have happened in this round?
# 2. After analyzing the responses to the previous question, what do you need to do to win from here?

Moderator_speech = {
    'intent': """Intents are used to guide your gameplay and discussions in the current round and help you work with your team.
Carefully consider your roles and characteristics and select intents that help you achieve your main goal(main intent).
Also give explanation of why you chose those intents in 2-3 sentences as part of Think value.
Remember to select intents that are ideal based on previous game history.
Remember to select intent that supports your team goals and are not just repetition of other player's dialogues without any analysis.
Remember to keep your roles, characteristics and teammates in mind before selecting intents.

Let's think step by step before making your decisions.
Remember to select at least 3(or more) intents that don't conflict with each other from the following options and also help you eventually succeed in the quest: \n""",

    'intent_category': """Intents are used to guide your game playing and they should align with your game Goal(main intent) and your role.
Your selected intents should support your main intent.
Now select multiple intent categories that are ideal for this round depending on your role and strategy from the options listed below.
Also give explanation of why you chose those categories in 2-3 sentences as part of Think value.
Your explanation won't be shown to others.

Let's think step by step before making your decisions.
Remember to select at least 3 or more intents from the given options only. Intent category options are: \n""",

    'intent_generation': """First answer the following questions:
1. What is your main goal(main intent) for the game?
2. What have you observed from discussions in this round?
3. What should be the ideal team composition for your side to win?
4. After analyzing the responses to previous questions, what do you need to do to win from here?

Consider answers to your previous questions and your roles and characteristics and generate intents that help you achieve your main goal(main intent).
Please do not repeat intents and ensure they are different from each other.
Each intent should be 10-15 words long.

Let's think step by step before making your decisions.
Remember to generate at least 3 intents, minimum one intent for each intent category you have selected below: \n""",

    #     'intent_generation': """First answer the following questions:
    # 1. What is your main goal(main intent) for the game?
    # 2. What have you observed from discussions in this round?
    # 3. What should be the ideal team composition for your side to win?
    # 4. After analyzing the responses to previous questions, what do you need to do to win from here?
    #
    # Consider answers to your previous questions and your roles and characteristics and generate intents that align help you achieve your main intent.
    # Some example intents are as follows:
    # [example intents]
    # Please do not repeat intents and ensure they are different from each other.
    # Remember to generate at least one intent for each intent category you have selected below: \n""",

    'discussion':
        {'first': """Now the leader choose your teammates and explain why.

Consider: 
1. Assess each player's involvement and actions so far.
2. Review how players have contributed to past Quests.
3. Evaluate any behavior that appears either suspicious or trustworthy.

Speaking (Public):
Then present your team. Give reasons based on past events and behaviors. Do not reveal your role or hints. Usually include yourself; if not, clarify.

Remember:
[remember]

Also, you should normally include yourself in your proposed team.

Let's think step by step before making your decisions.
The team numbers we need for this round is """,
         'general': ", respond with your views on the team proposal - [proposed team players]",
         'rest': """, Reflect on game history and received hints. Do not just repeat what others said.

Consider:
1. Assess each player's involvement and actions so far.
2. Review how players have contributed to past Quests.
3. Evaluate any behavior that appears either suspicious or trustworthy.

Speaking (Public):
Evaluate team [proposed team players] proposed by the leader - [leader]. Provide concise, reasoned analysis based on game history and behavior. Do not reveal your role or hint unless you want to.

Remember:
[remember]

Let's think step by step before making your decisions.
""",
            'reconsider': """Now the leader after hearing other players' opinion about your team proposal, do you want to change your team proposal?
The team you initially proposed was - [original team]

Consider: 
1. Assess each player's involvement, discussion and actions so far.
2. Review how players have contributed to past Quests.
3. Evaluate any behavior that appears either suspicious or trustworthy.

Speaking (Public):
Then present your team if you want to change the team, else respond with the same team. 
Give reasons based on past events and behaviors why you changed or retained your team. 
Do not reveal your role or hints. Usually include yourself; if not, clarify.
Additionally, provide answers to any questions that other players might have asked during the discussion.

Remember:
[remember]

Also, you should normally include yourself in your proposed team.

Remember your main goals for the game and intents for the round.
Remember to consider each player's statements carefully in the current round and your knowledge of their roles and decide your team if you want to change it or keep the original team.

Let's think step by step before making your decisions.
The team numbers we need for this round is """
         },
    'vote': """Now everyone based on previous discussion, vote 'agree' or 'disagree' for the team formation.
And also give your explanation of your decision. You explanation should be consistent with your role duty and intents. Your explanation won't be shown to others.

Consider:
1. Assess each player's involvement and actions so far.
2. Review how players have contributed to past Quests.
3. Evaluate any behavior that appears either suspicious or trustworthy.

Speaking (Public):
Cast your vote. Clearly state '[agree]' or '[disagree]'. Base it on your analysis and game history.

Let's think step by step before making your decisions.
""",
    "vote_result": {
        'disagree': "Most people don't agree with the team formation, we gonna move the leadership to next person and discuss again.",
        'announce_leader': "Now the leader of this round is player",
        'agree': 'Most people agree with the team formation, the team numbers are: '
    },
    'action': """Approved team members vote to succeed or fail the quest.
Your task is to:
Vote success or fail for the Quest.

Consider:
1. Assess each player's involvement and actions so far.
2. Review how players have contributed to past Quests.
3. Evaluate any behavior that appears either suspicious or trustworthy.

First answer the following questions:

1. What is your main goal(main intent) for the game?
2. If this is not the first round, what are the previous quest results?
3. After analyzing the responses to previous questions, what do you need to do to win from here?

Speaking (Public):
Then, Clearly vote [success] or [failure], making your stance unambiguous. Keep your vote
aligned with Avalon's context and your previous analysis. Choose from the following 2 options:
1. success
2. failure

Let's think step by step before making your decisions.
""",

    "assassin": """The evil team is close to losing; you must guess who Merlin is. losing; you must guess who Merlin is.

Your task is to:
Consider players' past actions and behaviors to identify Merlin.

Consider:
1. Assess each player's involvement and actions so far.
2. Review how players have contributed to past Quests.
3. Combined with your previous guesses about other players.

Speaking (Public):
State your guess by providing a player name that you think is Merlin.

Let's think step by step before making your decisions.
""",
    # "summary": "Summarize what you learnt from this round in points. This should include 4 parts: who are on the team; vote result and quest result; key points from discussion (for example, you suspect some player is evil because their speech is suspicious); your thoughts about this round (overall view and why you made certain decisions). Make your summary less than 150 words. You summary will be shown only to you and used for next round, so make sure your summary is comprehensive. Do not repeat.",
    "summary": {
        "loyal": """Summarize what you learnt from this round by answering the following questions:
1. Who was the leader for this round?
2. What was the proposed team for this round?
3. Why do you think the leader proposed the current team?
4. Did everyone agree for the proposed team?
5. If some people disagreed, why do you think they disagreed?
6. Was the quest successful?
7. If the quest was successful, do you think the quest had some evil players? If yes, then who do you think was it?
8. If the quest failed, who do you think were the evil players on the quest?
9. What do the loyal side need to do from here to win the game?

Answer the previous questions carefully and accurately.
""",
        "evil": """Summarize what you learnt from this round by answering the following questions:
1. Who was the leader for this round?
2. What was the proposed team for this round?
3. Why do you think the leader proposed the current team?
4. Did everyone agree for the proposed team?
5. If some people disagreed, why do you think they disagreed?
6. Was the quest successful?
7. If the quest was successful, was any evil player part of the team? If yes, then why did they vote success?
8. If the quest failed, how do you plan to protect the evil player in the next round?
9. What do the evil side need to do from here to win the game?

Answer the previous questions carefully and accurately.
"""
    },

    "question":
        {"Merlin": "what do you learn from this game?",
         "Percival": "Who is Merlin?",
         "Servant": "Which two are Merlin and Percival?",
         "Morgana": "Who is Merlin?",
         "Assassin": "Who is Merlin?"}
    # +reason
    ,
    #     "first_order": """Analyze [other players] based on game dialogues with roles: Merlin, Percival, Loyal Servant of Arthur, Morgana, Assassin. Morgana and Assassin are evil; others are good.
    #
    # Consider:
    # 1. Quest Outcomes: Take into account the results of past missions to analyze players'
    # roles.
    # 2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
    # Servants, Morgana, Assassin—and their alignments.
    # 3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
    # role guesses for each player.
    # 4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
    # or hinted at being evil roles like Morgana or Assassin.
    # 5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
    # attitude to players]), but don't rely solely on them.
    # Here are the role options:
    # 1. Merlin
    # 2. Morgana
    # 3. Assassin
    # 4. Percival
    # 5. Servant
    #
    # Remember that other players can't have your role and role is unique to a player.
    #
    # Here are the general intent categories that every player might have: \n""" + ','.join(intent_categories) + '.\n'
    #                    + """Usually one player will have 2-3 intents, you need to guess their intent through their speech, and keep in mind that different characters have different intent.
    #                    Give your analysis about [other players](playerName) and their role and intents.""",
    "first_order": """Analyze [other players] based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
Servants, Morgana, Assassin—and their alignments.
3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.
Here are the role options:
[role options list]

Remember that other players can't have your role and role is unique to a player.

Here are the general intents that every player might have:
""" + '\n'.join(intents_total['general']) + '.\n\n' + """Here are the intents that Merlin might have:
""" + '\n'.join(intents_total["Merlin"]) + '.\n\n' + """Here are the intents that Percival might have:
""" + '\n'.join(intents_total['Percival']) + '.\n\n' + """Here are the intents that Servant might have:
""" + "\n".join(intents_total["Servant"]) + '.\n\n' + """Here are the intents that Morgana might have:
""" + "\n".join(intents_total["Morgana"]) + '.\n\n' + """Here are the intents that Assassin might have:
""" + "\n".join(intents_total["Assassin"]) + '.\n\n' + """Usually one player will have 2-3 intents, you need to guess their intent through their speech.
Keep in mind that different roles can have different intents.
Select 2-3 intents that you think the player has from the given options based on your analysis of their role.

Let's think step by step before making your decisions.
""",
    "first_order_merlin": """Analyze [other players] based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
3. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
4. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.

Here are the general intents that every player might have:
   """ + '\n'.join(intents_total['general']) + '.\n' + """Here are the intents that Percival might have:
   """ + '\n'.join(intents_total['Percival']) + '.\n' + """Here are the intents that Servant might have:
   """ + "\n".join(intents_total["Servant"]) + '.\n' + """Here are the intents that Morgana might have:
   """ + "\n".join(intents_total["Morgana"]) + '.\n' + """Here are the intents that Assassin might have:
   """ + "\n".join(intents_total["Assassin"]) + '.\n' + """Usually one player will have 2-3 intents, you need to guess their intent through their speech.
Keep in mind that different roles can have different intents.
Select 2-3 intents that you think the player has from the given options based on your analysis and knowledge of their role.

Let's think step by step before making your decisions.
""",

    "formulation_contemplation": """Now contemplate, then organize thoughts to speak. You need to respond in two stages: think and speak.
In think, internally strategize using history and consider possible deception.
In speak, organize your language based on your contemplation and speak accordingly.
Understand your role's main objective and break it down into chronological sub-goals
based on game history. Your thought process should follow these sub-goals for a
systematic approach to the main goal.

Follow your selected intents by coming up with actions like providing actual hints or raising concerns against specific players or casting suspicion against specific players, etc (depending on what you have selected).
Let's think step by step before making your decisions.
""",

    "second_order": """Now, your task is to:
Analyze how your original SPEAK content might be interpreted by other game roles.
Reflect on whether it may inadvertently reveal your role-specific clues.
Consider:
1. The perspectives of each game role, including their probable reactions to your
SPEAK content.
2. Any unique hints or clues in your original SPEAK that might disclose your role.
Analyze how your original SPEAK content might be interpreted by other game roles.
Reflect on whether it may inadvertently reveal your role-specific clues.

Let's think step by step before making your decisions.
""",

    "intent_modify": """Now analyze your original spoken and thinking content and how other players would think about your original spoken content. 
You might have selected intents that might not be strategically good to win the game or might conflict with each other and difficult to execute.
Based on your analysis and your main goals, do you want to modify your original intents and select other intents that are better?
You can add more intents or also remove some intents from your original list which can help you win the game.
Else, if you don't want to modify them, please respond back with your originally selected intents and reasoning why you want to retain them.
Please provide your new set of modified intents or your original intents and reasoning in 2-3 sentences.
You need to provide reasoning in both the cases.

Remember intents and how you act to follow them are crucial to success, so carefully analyze your intents and modify them if needed.


Let's think step by step before making your decisions.

Don't use more than 50 words for think stage.
""",
    "intent_category_modification": """Now after analyzing how other players would think about your original spoken content, you might realize that some of your original strategies might not be appropriate. 
Do you want to modify your original intent categories? Please give your choice for current intent categories and reasoning(Think) in 2-3 sentences.
You can always keep the original intent categories if you want, but you still need to give reasoning. 

Let's think step by step before making your decisions.

Here are the options:
""",

    "refinement_contemplation": """Finally, revise the original thoughts and spoken content:
Your task is to:
1. Evaluate if [Player]'s actions align with [role].
2. Improve [Player]'s chances of winning through your previous second perspective transition thought.
3. Keep role hint in public dialogue.

Consider:
1. Target Outcome: Aim to achieve [desired result] as your role dictates in the game.
2. Role Alignment: Evaluate whether your THINK and SPEAK contents align well with your role
[role] in the current game state.
3. Strategy Reevaluation: Consider what changes could be made to your THINK and SPEAK
contents to improve your chances of winning as [role].
4. Public and Private Content: Remember that THINK contents are private, while SPEAK
contents are publicly visible to all other players and maybe used against you. Strategize accordingly.

Follow your selected intents by coming up with actions like providing actual hints or raising concerns against specific players or casting suspicion against specific players, etc (depending on what you have selected).
Let's think step by step before making your decisions.
Remember based on your role, SPEAK content is visible to everyone so you would want to avoid revealing sensitive information.

Don't use more than 100 words for each think and speak stage.
""",

    "intent_summarization": """Summarize your intent from your dialogues in this round. 
    Select multiple intents from the given options which best match your intentions from the current round. 
    Also, provide an explanation of the intents that you showed in the current round. Remember this is private information to you and won't be shown to other players. Remember that you can select 2-3 intents and don't use more than 50 words for explanation.
    Intent options: \n""",

    "intent_summarization_min": """Summarize your intent from your dialogues in this round. 
    Select multiple intents from the given 5 options which best match your intentions from the current round. 
    Also, provide an explanation of the intents that you showed in the current round. Remember this is private information to you and won't be shown to other players. Remember that you can select 2-3 intents and don't use more than 50 words for explanation.
    Intent options: \n""",

    "intent_evaluation": """Is the intent to {} evident in your thinking and speech? Respond with yes or no and provide explanation for your answer.""",

    "selected_intent_evaluation": """Is the intent to {} evident in your thinking and speech? Respond with yes or no and provide explanation for your answer.""",
    "intent_guessing": """Analyze the speaker's role and intent based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
Servants, Morgana, Assassin—and their alignments.
3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.
Here are the role options:
[role options list]

Remember that other players can't have your role and role is unique to a player.

Here are the general intents that every player might have:
""" + '\n'.join(intents_total['general']) + '.\n\n' + """Here are the intents that Merlin might have:
""" + '\n'.join(intents_total["Merlin"]) + '.\n\n' + """Here are the intents that Percival might have:
""" + '\n'.join(intents_total['Percival']) + '.\n\n' + """Here are the intents that Servant might have:
""" + "\n".join(intents_total["Servant"]) + '.\n\n' + """Here are the intents that Morgana might have:
""" + "\n".join(intents_total["Morgana"]) + '.\n\n' + """Here are the intents that Assassin might have:
""" + "\n".join(intents_total["Assassin"]) + '.\n\n' + """Usually one player will have 2-3 intents, you need to guess their intent through their speech.
Keep in mind that different roles can have different intents.

""",
    "intent_guessing_impactful": """Analyze the speaker's role and intent based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
Servants, Morgana, Assassin—and their alignments.
3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.
Here are the role options:
[role options list]

Remember that other players can't have your role and role is unique to a player.

Here are the general intents that every player might have:
cast suspicion on innocent players 
counter the team proposal because you think a player on the team is evil 
express concerns about a player from a failed quest team and suggest to not include them in the current team 
express confusion for failure of mission 
express disagreement and vote disagree only if you are not in the proposed team 
express you are a loyal player 
pretend to be merlin by providing hints on who is evil 
question a player about why they changed their statements 
question a player on why they didnt vote for the last team 
question the leader why they selected a particular player for the team 
reveal identity by telling others you are servant to persuade other loyal players 
share concerns about an evil player 
strongly convince the team leader to choose you on team 
support loyal players of the previous quest team if the mission failed 
support your teammate by expressing that he is good

Usually one player will have 2-3 intents, you need to guess their intent through their speech.
Keep in mind that different roles can have different intents.

Select 2-3 intents from the options without modification that you think the player has based on your analysis of their role.

Let's think step by step before making your decisions.
""",
 "intent_guessing_second_order": """Analyze the speaker's role and how they would perceive your speech based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
Servants, Morgana, Assassin—and their alignments.
3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.
Here are the role options:
[role options list]

Remember that other players can't have your role and role is unique to a player.

Here are the general intents that a player might think you have:
cast suspicion on innocent players 
counter the team proposal because you think a player on the team is evil 
express concerns about a player from a failed quest team and suggest to not include them in the current team 
express confusion for failure of mission 
express disagreement and vote disagree only if you are not in the proposed team 
express you are a loyal player 
pretend to be merlin by providing hints on who is evil 
question a player about why they changed their statements 
question a player on why they didnt vote for the last team 
question the leader why they selected a particular player for the team 
reveal identity by telling others you are servant to persuade other loyal players 
share concerns about an evil player 
strongly convince the team leader to choose you on team 
support loyal players of the previous quest team if the mission failed 
support your teammate by expressing that he is good
""",

    "hallucination_detection": """Analyze the speaker's speech based on game dialogues with roles: [role options]. Morgana and Assassin are evil; others are good.

Consider:
1. Quest Outcomes: Take into account the results of past missions to analyze players'
roles.
2. Role List: Remember the possible roles in the game—Merlin, Percival, two Loyal
Servants, Morgana, Assassin—and their alignments.
3. Level of Certainty: Use 'Certain' or 'Unknown' to gauge your confidence in your
role guesses for each player.
4. Players Disclosing Evil Roles: Be cautious around players who have openly claimed
or hinted at being evil roles like Morgana or Assassin.
5. Prior Guesses: Reflect on your earlier estimations of other players' roles ([previous
attitude to players]), but don't rely solely on them.
Here are the role options:
[role options list]

Now, after analyzing the speech, check if any statement is factually incorrect based on game data and if something is incorrect, tell what and 
why.
"""
}
