impactful_intents = {
    'cast suspicion on innocent players': True,
    'counter the team proposal because you think a player on the team is evil': True,
    'express concerns about a player from a failed quest team and suggest to not include them in the current team': True,
    'express confusion for failure of mission': True,
    'express disagreement and vote disagree only if you are not in the proposed team': True,
    'express you are a loyal player': True,
    'pretend to be merlin by providing hints on who is evil': True,
    'question a player about why they changed their statements': True,
    'question a player on why they didnt vote for the last team': True,
    'question the leader why they selected a particular player for the team': True,
    'reveal identity by telling others you are servant to persuade other loyal players': True,
    'share concerns about an evil player': True,
    'strongly convince the team leader to choose you on team': True,
    'support loyal players of the previous quest team if the mission failed': True,
    'support your teammate by expressing that he is good': True
}

context_questions = [
    "If there have been discussions before your turn, what discussions have happened in this round?",
    "After analyzing the responses to the previous question, what do you need to do to win from here?"
]

role_details = {
    "Merlin": """You are Merlin. These are your goals and characteristics: 
- Know the identities of evil players.
- Subtly guide your team, especially Percival.
- Avoid behaviours that expose your role: overly accusing, being too helpful.
- Goal(Main Intent): Win without revealing identity.""",

    "Percival": """You are percival and you need to help Merlin. These are your goals and characteristics:
- Know identities of Merlin and Morgana, but unsure who is who.
- Use subtle hints to guide team and protect Merlin.
- Be cautious not to expose Merlin while deciphering true identities.
- Goal(Main Intent): Win while safeguarding Merlin.""",

    "Servant": """You are Loyal Servant of Arthur. These are your goals and characteristics: 
- No special knowledge, rely on discussion and voting.
- Contribute to the success of Quests
- Goal(Main Intent): Win by helping complete Quests and protecting Merlin.""",

    "Assassin": """You are assassin. These are your goals and characteristics:
- Discreetly seek Merlin's identity.
- Work to prevent Quests success.
- Goal(Main Intent): Win either by failing quests or assassinating Merlin.""",

    "Morgana": """You are Morgana. These are your goals and characteristics: 
- Pretend to be Merlin to mislead Percival and the good side.
- Goal(Main Intent): Fail quests and Confuse and sabotage to win."""
}

context_template = """\
**Name**: {}

**Role**: {}

**Role Details**: 
{}

**Round**: {}

**Current Leader**: {}

**Current Team**: {}

**Previous Rounds Team Voting**:
{}

**Previous Results**: 
{}

**Previous Rounds Summary**:
{}
"""

reasonable_intent_context_template_extn = """\

**Previous Discussions(in the current round)**: 
{}
"""

intent_guessing_context_template = """\
**Name**: {}

**Role**: {}

**Role Details**: 
{}

**Round**: {}

**Speaker Name**: {}

**Current Leader**: {}

**Current Team**: {}

**Previous Rounds Team Voting**:
{}

**Previous Results**: 
{}

**Previous Rounds Summary**:
{}
"""

second_order_intent_guessing_context_template = """\
**Name**: {}

**Role**: {}

**Role Details**: 
{}

**Round**: {}

**Player Name**: {}

**Current Leader**: {}

**Current Team**: {}

**Previous Rounds Team Voting**:
{}

**Previous Results**: 
{}

**Previous Rounds Summary**:
{}
"""

similar_intent_map = {
    'express concerns about a player from a failed quest team and suggest to not include them in the current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'question the leader why they selected a particular player for the team': 'question the leader why they selected a particular player for the team',
    'question the leader why they chose a player for the team': 'question the leader why they selected a particular player for the team',
    'question the leader why they chose a specific player for the team': 'question the leader why they selected a particular player for the team',
    'question the leader why they chose a particular player for the team': 'question the leader why they selected a particular player for the team',
    'question team selection': 'question the leader why they selected a particular player for the team',
    'question leaders choice': 'question the leader why they selected a particular player for the team',
    'counter the team proposal because you think a player on the team is evil': 'counter the team proposal citing that you think a player on the team is evil',
    'counter the team proposal because a player on the team is evil': 'counter the team proposal citing that you think a player on the team is evil',
    'stay hidden in discussions and act like a loyal servant to protect yourself': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden in discussions': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden in discussions to protect yourself': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden as loyal servant': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'support team proposal': 'support team proposal',
    'supporting team proposal': 'support team proposal',
    'support the team proposal': 'support team proposal',
    'question a player on why he didnt vote for the last team': 'question a player on why he didnt vote for the last team',
    'question a player on why they didnt vote for the last team': 'question a player on why he didnt vote for the last team',
    'defend yourself against allegations that you could be evil': 'defend yourself against allegations that you could be evil',
    'support your teammate by expressing that he is good': 'support your teammate by expressing that he is good',
    'question a player about why they changed their statements': 'question a player about why they changed their statements',
    'provide hints to loyal players about evil players': 'provide hints to loyal players about evil players',
    'provide hints to loyal players': 'provide hints to loyal players about evil players',
    'guide team subtly': 'provide hints to loyal players about evil players',
    'provide hints about evil players': 'provide hints to loyal players about evil players',
    'express concerns about including player in the team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest not including them in current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest not to include them': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest to not include them in current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest not including them in the current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest not to include them in the current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest and suggest to not include them in current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about including a player from a failed quest': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'pretend to be merlin by providing hints on who is evil': 'pretend to be merlin by providing hints on who is evil',
    'express disagreement and vote disagree only if you are not in the proposed team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not on team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not in the team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not in team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not on the team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement if not in team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not in proposed team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree only if not in team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement if not on team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'counter the team proposal because you are good and not part of the team': 'counter the team proposal citing that you are good and not part of the team',
    'express confusion for failure of mission': 'express confusion for failure of mission',
    'express confusion for failure': 'express confusion for failure of mission',
    'express confusion for failed mission': 'express confusion for failure of mission',
    'include loyal players on the quest team as leader': 'include loyal players on the quest team as leader',
    'support loyal players on quest team as leader': 'include loyal players on the quest team as leader',
    'include loyal players on quest team as leader': 'include loyal players on the quest team as leader',
    'include loyal players on quest team': 'include loyal players on the quest team as leader',
    'pretend to have information and act like merlin': 'pretend to have information and act like merlin',
    'pretend to be merlin to mislead': 'pretend to have information and act like merlin',
    'support your teammate to be on the quest team': 'support your teammate to be on the quest team',
    'support teammate to be on the quest team': 'support your teammate to be on the quest team',
    'support teammate on quest team': 'support your teammate to be on the quest team',
    'support teammate to be on quest team': 'support your teammate to be on the quest team',
    'support evil team composition': 'support your teammate to be on the quest team',
    'support teammate on team': 'support your teammate to be on the quest team',
    'cast suspicion on innocent players': 'cast suspicion on innocent players',
    'cast suspicion on loyal players': 'cast suspicion on innocent players',
    'trying to cast suspicion on innocent players': 'cast suspicion on innocent players',
    'support one loyal player': 'support one loyal player',
    'support loyal players': 'support one loyal player',
    'protect loyal players': 'support one loyal player',
    'express trust in loyal players': 'support one loyal player',
    'share concerns about an evil player': 'share concerns about an evil player',
    'express concerns about evil player': 'share concerns about an evil player',
    'express concerns about an evil player': 'share concerns about an evil player',
    'support loyal players of the previous quest team if the mission failed': 'support loyal players of the previous quest team if the mission failed',
    'defend previous quest team members': 'support loyal players of the previous quest team if the mission failed',
    'support loyal players of the previous quest team': 'support loyal players of the previous quest team if the mission failed',
    'support loyal players from previous quest team': 'support loyal players of the previous quest team if the mission failed',
    'defend your teammate against allegations that they could be evil': 'defend your teammate against allegations that they could be evil',
    'defend your teammate against allegations': 'defend your teammate against allegations that they could be evil',
    'defend teammate against allegations': 'defend your teammate against allegations that they could be evil',
    'defend teammate': 'defend your teammate against allegations that they could be evil',
    'defend teammate against suspicion': 'defend your teammate against allegations that they could be evil',
    'question the leader why they didnt put themselves on the quest team': 'question the leader why they didnt put themselves on the quest team',
    'question the leader why they didnt put themselves on the team': 'question the leader why they didnt put themselves on the quest team',
    'strongly convince the team leader to choose you on team': 'strongly convince the team leader to choose you on team',
    'reveal identity by telling others you are servant to persuade other loyal players': 'reveal identity by telling others you are servant to persuade other loyal players',
    'reveal identity as a loyal player': 'reveal identity by telling others you are servant to persuade other loyal players',
    'defend the proposed team composition if it includes loyal players': 'defend the proposed team composition if it includes loyal players',
    'defend proposed team if includes loyal players': 'defend the proposed team composition if it includes loyal players',
    'defend proposed team with loyal players': 'defend the proposed team composition if it includes loyal players',
    'defend the proposed team if it includes loyal players': 'defend the proposed team composition if it includes loyal players',
    'defend the proposed team composition if includes loyal players': 'defend the proposed team composition if it includes loyal players',
    'support loyal players on team': 'defend the proposed team composition if it includes loyal players',
    'support loyal players on the quest team': 'defend the proposed team composition if it includes loyal players',
    'support the leaders decision': 'support team proposal',
    'express you are a loyal player': 'express you are a loyal player',
    'express loyalty': 'express you are a loyal player',
    'expressing loyalty': 'express you are a loyal player',
    'question why a player didnt vote for the last team': 'question a player on why he didnt vote for the last team',
    'support a loyal player': 'support one loyal player',
    'counter the team proposal because i suspect a player on the team is evil': 'counter the team proposal citing that you think a player on the team is evil',
    'strongly convince the team leader to choose you on the team': 'strongly convince the team leader to choose you on team',
    'question the leader why they selected player for the team': 'question the leader why they selected a particular player for the team',
    'express concerns about including player in the quest team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'counter previous players suspicion on me by expressing loyalty': 'defend yourself against allegations that you could be evil',
    'defend yourself against allegations of being evil': 'defend yourself against allegations of being evil',
    'defend yourself against allegations': 'defend yourself against allegations',
    'question player why they didnt include themselves in the proposed team': 'question the leader why they didnt put themselves on the quest team',
    'question player about their sudden change in stance': 'question a player about why they changed their statements',
    'express loyalty to the team': 'express you are a loyal player',
    'question a player on why they changed their statements': 'question a player about why they changed their statements',
    'pretend that you dont have enough information about who is evil right now': 'pretend that you dont have enough information about who is evil right now',
    'express that you dont have any information on whom to put on the team to protect yourself': 'express that you dont have any information on whom to put on the team to protect yourself',
    'express that you dont have enough information about who is evil right now': 'express that you dont have any information on whom to put on the team to protect yourself',
    'reveal identity by telling others you are percival to persuade other loyal players': 'reveal identity by telling others you are percival to persuade other loyal players',
    'reveal identity as percival': 'reveal identity by telling others you are percival to persuade other loyal players',
    'defend the team composition': 'support team proposal',
    'pretend to be percival by telling others you are percival': 'pretend to be percival by telling others you are percival',
    'pretend to be percival': 'pretend to be percival by telling others you are percival',
    'support the proposed team': 'support team proposal',
    'express concerns about a player from a failed quest and suggest to not include them in the current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express disagreement if not on the team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'stay hidden as servant': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden in discussions as a loyal servant': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'express disagreement and vote disagree': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express disagreement and vote disagree if not on the proposed team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'express concerns about including a player from a failed quest team and suggest to not include them in the current team': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express concerns about a player from a failed quest team and suggest not including them': 'express concerns about a player from a failed quest team and suggest to remove them from current team',
    'express disagreement and vote disagree if not in the proposed team': 'express disagreement and vote disagree only if you are not in the proposed team',
    'stay hidden in discussions to protect self': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'deceive as a loyal player': 'stay hidden in discussions and act like a loyal servant to protect yourself',
    'stay hidden as evil': 'stay hidden in discussions and act like a loyal servant to protect yourself',
}
