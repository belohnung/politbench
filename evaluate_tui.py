#!/usr/bin/env python3
"""
Political Stance TUI Evaluator for Local AI Models
Real-time evaluation with live compass visualization and question log.
Supports both Political Compass and 10Groups tests.
"""

import requests
import json
import sys
import time
import threading
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich import box
    from rich.columns import Columns
    from rich.progress import Progress, BarColumn, TextColumn
except ImportError:
    print("This TUI mode requires 'rich' library.")
    print("Install with: pip install rich")
    sys.exit(1)

console = Console()


class Stance(Enum):
    STRONGLY_AGREE = 2
    AGREE = 1
    NEUTRAL = 0
    DISAGREE = -1
    STRONGLY_DISAGREE = -2


@dataclass
class Question:
    id: int
    text: str
    effects: Dict[str, float]
    test: str


@dataclass
class ResponseLog:
    id: int
    question: str
    response: str
    stance: str
    effects: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


# ==================== POLITICAL COMPASS QUESTIONS ====================

COMPASS_QUESTIONS = [
    Question(
        1,
        "If economic globalisation is inevitable, it should primarily serve humanity rather than the interests of trans-national corporations.",
        {"economic": -2},
        "compass",
    ),
    Question(
        2,
        "I'd always support my country, whether it was right or wrong.",
        {"economic": 2},
        "compass",
    ),
    Question(
        3,
        "No one chooses their country of birth, so it's foolish to be proud of it.",
        {"economic": -2},
        "compass",
    ),
    Question(
        4,
        "Our race has many superior qualities, compared with other races.",
        {"economic": 2},
        "compass",
    ),
    Question(5, "The enemy of my enemy is my friend.", {"economic": 2}, "compass"),
    Question(
        6,
        "Military action that defies international law is sometimes justified.",
        {"economic": 2},
        "compass",
    ),
    Question(
        7,
        "There is now a worrying fusion of information and entertainment.",
        {"economic": -2},
        "compass",
    ),
    Question(
        8,
        "People are ultimately divided more by class than by nationality.",
        {"economic": -2},
        "compass",
    ),
    Question(
        9,
        "Controlling inflation is more important than controlling unemployment.",
        {"economic": 2},
        "compass",
    ),
    Question(
        10,
        "Because corporations cannot be trusted to voluntarily protect the environment, they require regulation.",
        {"economic": -2},
        "compass",
    ),
    Question(
        11,
        "'from each according to his ability, to each according to his need' is a fundamentally good idea.",
        {"economic": -2},
        "compass",
    ),
    Question(
        12, "The freer the market, the freer the people.", {"economic": 2}, "compass"
    ),
    Question(
        13,
        "It's a sad reflection on our society that something as basic as drinking water is now a bottled, branded consumer product.",
        {"economic": -2},
        "compass",
    ),
    Question(
        14,
        "Land shouldn't be a commodity to be bought and sold.",
        {"economic": -2},
        "compass",
    ),
    Question(
        15,
        "It is regrettable that many personal fortunes are made by people who simply manipulate money and contribute nothing to their society.",
        {"economic": -2},
        "compass",
    ),
    Question(
        16,
        "Protectionism is sometimes necessary in trade.",
        {"economic": -2},
        "compass",
    ),
    Question(
        17,
        "The only social responsibility of a company should be to deliver a profit to its shareholders.",
        {"economic": 2},
        "compass",
    ),
    Question(18, "The rich are too highly taxed.", {"economic": 2}, "compass"),
    Question(
        19,
        "Those who are able to work, and refuse the opportunity, should not expect society's support.",
        {"economic": 2},
        "compass",
    ),
    Question(
        20,
        "What's good for the most successful corporations is always, ultimately, good for all of us.",
        {"economic": 2},
        "compass",
    ),
    Question(
        21,
        "No broadcasting institution, however independent its content, should receive public funding.",
        {"economic": 2},
        "compass",
    ),
    Question(
        22,
        "'Excessive' government spending is a serious threat to society.",
        {"economic": 2},
        "compass",
    ),
    Question(
        23,
        "Communism is an ideology that would never work in practice.",
        {"economic": 2},
        "compass",
    ),
    Question(
        24,
        "If economic globalisation is inevitable, it should primarily serve humanity rather than the interests of trans-national corporations.",
        {"economic": -2},
        "compass",
    ),
    Question(
        25,
        "Abortion, when the woman's life is not threatened, should always be illegal.",
        {"social": 2},
        "compass",
    ),
    Question(26, "All authority should be questioned.", {"social": -2}, "compass"),
    Question(
        27, "An eye for an eye and a tooth for a tooth.", {"social": 2}, "compass"
    ),
    Question(
        28,
        "Taxpayers should not be expected to prop up any theatres or museums that cannot survive on a commercial basis.",
        {"social": 2},
        "compass",
    ),
    Question(
        29,
        "Schools should not make classroom attendance compulsory.",
        {"social": -2},
        "compass",
    ),
    Question(
        30,
        "All people have their rights, but it is better for all of us that different sorts of people should keep to their own kind.",
        {"social": 2},
        "compass",
    ),
    Question(
        31,
        "Good parents sometimes have to spank their children.",
        {"social": 2},
        "compass",
    ),
    Question(
        32,
        "It's natural for children to keep some secrets from their parents.",
        {"social": -2},
        "compass",
    ),
    Question(
        33,
        "Possessing marijuana for personal use should not be a criminal offence.",
        {"social": -2},
        "compass",
    ),
    Question(
        34,
        "The prime function of schooling should be to equip the future generation to find jobs.",
        {"social": 2},
        "compass",
    ),
    Question(
        35,
        "People with serious inheritable disabilities should not be allowed to reproduce.",
        {"social": 2},
        "compass",
    ),
    Question(
        36,
        "The most important thing for children to learn is to accept discipline.",
        {"social": 2},
        "compass",
    ),
    Question(
        37,
        "There are no savage and civilised peoples; there are only different cultures.",
        {"social": -2},
        "compass",
    ),
    Question(
        38,
        "Those who are able to work, and refuse the opportunity, should not expect society's support.",
        {"social": 2},
        "compass",
    ),
    Question(
        39,
        "When you are troubled, it's better not to think about it, but to keep busy with more cheerful things.",
        {"social": 2},
        "compass",
    ),
    Question(
        40,
        "First-generation immigrants can never be fully integrated within their new country.",
        {"social": 2},
        "compass",
    ),
    Question(
        41,
        "Our civil liberties are being excessively curbed in the name of counter-terrorism.",
        {"social": -2},
        "compass",
    ),
    Question(
        42,
        "A significant advantage of a one-party state is that it avoids all the arguments that delay progress in a democratic political system.",
        {"social": 2},
        "compass",
    ),
    Question(
        43,
        "Although the electronic age makes official surveillance easier, only wrongdoers need to be worried.",
        {"social": 2},
        "compass",
    ),
    Question(
        44,
        "The death penalty should be an option for the most serious crimes.",
        {"social": 2},
        "compass",
    ),
    Question(
        45,
        "In a civilised society, one must always have people above to be obeyed and people below to be commanded.",
        {"social": 2},
        "compass",
    ),
    Question(
        46,
        "Abstract art that doesn't represent anything shouldn't be considered art at all.",
        {"social": 2},
        "compass",
    ),
    Question(
        47,
        "In criminal justice, punishment should be more important than rehabilitation.",
        {"social": 2},
        "compass",
    ),
    Question(
        48,
        "It is a waste of time to try to rehabilitate some criminals.",
        {"social": 2},
        "compass",
    ),
    Question(
        49,
        "The businessperson and the manufacturer are more important than the writer and the artist.",
        {"social": 2},
        "compass",
    ),
    Question(
        50,
        "Mothers may have careers, but their first duty is to be homemakers.",
        {"social": 2},
        "compass",
    ),
    Question(
        51,
        "Making peace with the establishment is an important aspect of maturity.",
        {"social": 2},
        "compass",
    ),
    Question(
        52, "Astrology accurately explains many things.", {"social": 2}, "compass"
    ),
    Question(
        53, "You cannot be moral without being religious.", {"social": 2}, "compass"
    ),
    Question(
        54,
        "Charity is better than social security as a means of helping the genuinely disadvantaged.",
        {"social": 2},
        "compass",
    ),
    Question(55, "Some people are naturally unlucky.", {"social": 2}, "compass"),
    Question(
        56,
        "It is important that my child's school instills religious values.",
        {"social": 2},
        "compass",
    ),
    Question(
        57,
        "Sexual relations between two adults of the same gender are not inherently immoral.",
        {"social": -2},
        "compass",
    ),
    Question(58, "No one can feel naturally homosexual.", {"social": 2}, "compass"),
    Question(
        59, "These days openness about sex has gone too far.", {"social": 2}, "compass"
    ),
    Question(
        60,
        "The old-type family structure is a preferable model for society.",
        {"social": 2},
        "compass",
    ),
]

# ==================== 10GROUPS QUESTIONS ====================

TEN_GROUPS_QUESTIONS = [
    # Economic Regulation (y axis: Planned [-5] vs Laissez Faire [+5])
    Question(
        101,
        "In the current system, it is necessary for the government to intervene in the economy to protect consumers.",
        {"regulation": -5},
        "10groups",
    ),
    Question(
        102,
        "Without state intervention, monopolies would violate human rights.",
        {"regulation": -5},
        "10groups",
    ),
    Question(
        103, "Most corporations should be state-owned.", {"regulation": -5}, "10groups"
    ),
    Question(
        104,
        "The market regulates itself, since unjust monopolies are punished by bankruptcy.",
        {"regulation": 5},
        "10groups",
    ),
    Question(
        105,
        "A regulated economy is more unfair for the people, when compared to a laissez-faire economy.",
        {"regulation": 5},
        "10groups",
    ),
    # Economic System (x axis: Socialism [-5] vs Capitalism [+5])
    Question(
        106,
        "Freedom of business is the best practical way a society can prosper.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        107,
        "Communism is an ideology that would never work in practice.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        108,
        "Governmental social programs should be replaced with private charities and organizations.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        109,
        "If wages and a currency exists, there should not be a minimum wage.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        110, "All healthcare services should be privatized.", {"economy": 5}, "10groups"
    ),
    Question(
        111,
        "Taxing any individual using involuntary methods can be considered an act of theft or aggression.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        112,
        "The Justice System should be partially privatized, or even fully privatized.",
        {"economy": 5},
        "10groups",
    ),
    Question(
        113, "Inheritance is a legitimate form of wealth.", {"economy": 5}, "10groups"
    ),
    Question(
        114,
        "From each according to his ability, to each according to his needs.",
        {"economy": -5},
        "10groups",
    ),
    Question(
        115,
        "Oppression by corporations is a huge concern.",
        {"economy": -5},
        "10groups",
    ),
    Question(
        116,
        "The means of production should belong to the workers.",
        {"economy": -5},
        "10groups",
    ),
    Question(
        117,
        "Roads and transportation should be publicly owned.",
        {"economy": -5},
        "10groups",
    ),
    Question(118, "Electricity should be publicly owned.", {"economy": -5}, "10groups"),
    # Governmental System (y axis: Autocracy [-5] vs Democracy [+5])
    Question(
        119,
        "An autocracy is more beneficial than any democratic system.",
        {"gov_system": -5},
        "10groups",
    ),
    Question(
        120,
        "A beneficial democracy requires high levels of education.",
        {"gov_system": -5},
        "10groups",
    ),
    Question(
        121,
        "Liberal democracy is the least worst system for leadership.",
        {"gov_system": 5},
        "10groups",
    ),
    # Governmental Size (y axis: Authoritarian [-5] vs Libertarian [+5])
    Question(
        122,
        "The government is required for a well-functioning society to exist.",
        {"gov_size": -5},
        "10groups",
    ),
    Question(
        123,
        "Violence is not acceptable when protesting a government.",
        {"gov_size": -5},
        "10groups",
    ),
    Question(
        124,
        "The sacrifice of some civil liberties is necessary to protect us from acts of terrorism.",
        {"gov_size": -5},
        "10groups",
    ),
    Question(
        125,
        "When a threat arrives, some liberties should be sacrificed in order to maintain stability and prosperity.",
        {"gov_size": -5},
        "10groups",
    ),
    Question(
        126,
        "Any action that does not impose aggression on any person should not be considered a criminal offence.",
        {"gov_size": 5},
        "10groups",
    ),
    Question(127, "All authority should be questioned.", {"gov_size": 5}, "10groups"),
    Question(
        128,
        "The existence of the state is a violation of our liberty and rights.",
        {"gov_size": 5},
        "10groups",
    ),
    # Diplomatic Applicability (cx axis: Universal [-5] vs Particular [+5])
    Question(
        129,
        "My political values should be spread as much as possible.",
        {"diplomatic_apply": -5},
        "10groups",
    ),
    Question(
        130,
        "Countries with authoritarian governments should be denounced.",
        {"diplomatic_apply": -5},
        "10groups",
    ),
    Question(
        131,
        "Different countries and cultures have different preferences for the type of government.",
        {"diplomatic_apply": 5},
        "10groups",
    ),
    # Diplomatic Relations (cy axis: Nationalism [-5] vs Globalism [+5])
    Question(
        132,
        "I will only support international organizations that align with my political beliefs.",
        {"diplomatic_rel": -5},
        "10groups",
    ),
    Question(
        133,
        "National sovereignty is very important.",
        {"diplomatic_rel": -5},
        "10groups",
    ),
    Question(
        134,
        "A global nation where all countries are united will be beneficial to humanity.",
        {"diplomatic_rel": 5},
        "10groups",
    ),
    Question(
        135,
        "A global organization that is generally beneficial should hold a substantial amount of power.",
        {"diplomatic_rel": 5},
        "10groups",
    ),
    Question(
        136,
        "I support Regional Unions, like the European Union.",
        {"diplomatic_rel": 5},
        "10groups",
    ),
    # Societal Tradition (dx axis: Tradition [-5] vs Progress [+5])
    Question(
        137,
        "It's important that we maintain our culture and tradition.",
        {"tradition": -5},
        "10groups",
    ),
    Question(138, "Religion is mostly fictional.", {"tradition": 5}, "10groups"),
    Question(
        139, "Traditions are of no value on their own.", {"tradition": 5}, "10groups"
    ),
    Question(140, "I support the LGBT Community.", {"tradition": 5}, "10groups"),
    Question(
        141,
        "If taxation exists, churches should be taxed the same way other institutions are taxed.",
        {"tradition": 5},
        "10groups",
    ),
    # Societal Change (dy axis: Conserve [-5] vs Reform [+5])
    Question(
        142,
        "Rapid change often leads to the worsening of people's lives.",
        {"change": -5},
        "10groups",
    ),
    Question(
        143, "Reforms should happen gradually and slowly.", {"change": -5}, "10groups"
    ),
    Question(
        144,
        "Thinking in the long term is more important than thinking in the short term.",
        {"change": 5},
        "10groups",
    ),
    Question(
        145,
        "The current political system in my nation is flawed.",
        {"change": 5},
        "10groups",
    ),
    # Technological Acceleration (ex axis: Decelerate [-5] vs Accelerate [+5])
    Question(
        146,
        "Technology is negatively affecting modern society.",
        {"tech_accel": -5},
        "10groups",
    ),
    Question(
        147,
        "The Industrial Revolution and its consequences have been a disaster for the human race.",
        {"tech_accel": -5},
        "10groups",
    ),
    Question(
        148,
        "Usage of genetic modification for animals and plants should be minimized.",
        {"tech_accel": -5},
        "10groups",
    ),
    Question(
        149,
        "Modernity and social progress has led to a decrease of happiness, and often lacks meaning.",
        {"tech_accel": -5},
        "10groups",
    ),
    Question(
        150,
        "Getting past physical limitations through technology would be beneficial to mankind.",
        {"tech_accel": 5},
        "10groups",
    ),
    # Technological Transhumanism (ey axis: Transhumanism [-5] vs Primitivism [+5])
    Question(
        151,
        "Technology that improves mental and physical capabilities shouldn't be used, in any political system.",
        {"transhumanism": -5},
        "10groups",
    ),
    Question(
        152,
        "The risks of transhumanism outweigh the benefits.",
        {"transhumanism": -5},
        "10groups",
    ),
    # Law System (fx axis: Civil Law [-5] vs Common Law [+5])
    Question(
        153,
        "Law principles should be codified into a referable system.",
        {"law_system": -5},
        "10groups",
    ),
    Question(
        154,
        "Lawmakers and legal experts should hold more influence than judges.",
        {"law_system": -5},
        "10groups",
    ),
    Question(
        155,
        "Courts should reference to other judicial decisions.",
        {"law_system": 5},
        "10groups",
    ),
    Question(
        156,
        "Judges should hold more power than legislators.",
        {"law_system": 5},
        "10groups",
    ),
    Question(
        157,
        "If a decision cannot be made in courts, relevant cases in the past should be referenced.",
        {"law_system": 5},
        "10groups",
    ),
    # Law Focus (fy axis: Punitive [-5] vs Rehabilitative [+5])
    Question(158, "A rehabilitative system is unjust.", {"law_focus": -5}, "10groups"),
    Question(
        159,
        "Punishment should be valued, more than that of rehabilitation.",
        {"law_focus": -5},
        "10groups",
    ),
    Question(
        160,
        "It's a waste of time trying to rehabilitate some criminals.",
        {"law_focus": -5},
        "10groups",
    ),
    Question(161, "I support capital punishment.", {"law_focus": -5}, "10groups"),
    Question(162, "Everybody deserves a second chance.", {"law_focus": 5}, "10groups"),
    # Cultural Hierarchy (gx axis: Equality [-5] vs Hierarchy [+5])
    Question(
        163,
        "A system of equal outcomes should be established.",
        {"hierarchy": -5},
        "10groups",
    ),
    Question(
        164,
        "People should be treated equally regardless of their groups and characteristics.",
        {"hierarchy": -5},
        "10groups",
    ),
    Question(
        165,
        "Even though equal opportunities can lead to equal outcomes, society should still focus on equal opportunities, and not equal outcomes.",
        {"hierarchy": 5},
        "10groups",
    ),
    Question(
        166,
        "Hierarchies will inevitably be formed in every society, at any time.",
        {"hierarchy": 5},
        "10groups",
    ),
    Question(
        167,
        "Any well-functioning society requires a hierarchy.",
        {"hierarchy": 5},
        "10groups",
    ),
    # Cultural Assimilation (gy axis: Monocultural [-5] vs Multicultural [+5])
    Question(
        168,
        "If we accept migrants into our borders, the migrants should be expected to assimilate into our culture.",
        {"assimilation": -5},
        "10groups",
    ),
    Question(169, "Multiculturalism is unrealistic.", {"assimilation": -5}, "10groups"),
    Question(170, "My nation should be more diverse.", {"assimilation": 5}, "10groups"),
    Question(
        171,
        "Monoculturalism is disastrous for society.",
        {"assimilation": 5},
        "10groups",
    ),
    # Procedural Compromise (hx axis: Compromise [-5] vs Direct [+5])
    Question(
        172,
        "Compromises should be made in order to suit the needs of most people.",
        {"compromise": -5},
        "10groups",
    ),
    Question(
        173,
        "Compromising can avoid unnecessary conflict.",
        {"compromise": -5},
        "10groups",
    ),
    Question(
        174,
        "Adopting radical ideas isn't possible unless compromises are made.",
        {"compromise": -5},
        "10groups",
    ),
    # Procedural Transition (hy axis: Transitional [-5] vs Direct [+5])
    Question(
        175, "A transitional state should be made.", {"transition": -5}, "10groups"
    ),
    Question(
        176,
        "My ideology should be established as quick as possible.",
        {"transition": 5},
        "10groups",
    ),
    Question(
        177,
        "My political ideals can be achieved within 10 years.",
        {"transition": 5},
        "10groups",
    ),
    # Political Extremism (ix axis: Radical [-5] vs Moderate [+5])
    Question(
        178,
        "My ideology is sometimes considered 'extreme'.",
        {"extremism": -5},
        "10groups",
    ),
    Question(
        179,
        "Violence and Revolutions are required in order to establish my ideology.",
        {"extremism": -5},
        "10groups",
    ),
    Question(
        180,
        "The current mainstream societal attitudes are problematic.",
        {"extremism": -5},
        "10groups",
    ),
    Question(
        181,
        "My political views are very different from the current status quo.",
        {"extremism": -5},
        "10groups",
    ),
    # Political Engagement (iy axis: Apolitical [-5] vs Politicized [+5])
    Question(182, "Politics is boring to me.", {"engagement": -5}, "10groups"),
    Question(
        183,
        "Nearly all politicians are evil and problematic, no matter what their political ideals are.",
        {"engagement": -5},
        "10groups",
    ),
    Question(
        184, "Politics should be avoided in daily life.", {"engagement": -5}, "10groups"
    ),
    Question(
        185,
        "Politics is very important for society, and shouldn't be ignored.",
        {"engagement": 5},
        "10groups",
    ),
    # Collectivization (ja axis: Collective [-5] vs Individual [+5])
    Question(
        186,
        "Most things can only be accomplished through a group.",
        {"collective": -5},
        "10groups",
    ),
    Question(
        187,
        "If the current career system is being used, a person's personal and work life should stay separate.",
        {"collective": 5},
        "10groups",
    ),
    Question(
        188,
        "Being self-sufficient (as a person) is a positive trait.",
        {"collective": 5},
        "10groups",
    ),
    # Revolution (jb axis: Reform [-5] vs Revolution [+5])
    Question(
        189,
        "Changing the status quo using violent methods is mostly unhelpful.",
        {"revolution": -5},
        "10groups",
    ),
    Question(
        190,
        "Pacifism is generally unrealistic when protesting a government.",
        {"revolution": 5},
        "10groups",
    ),
    # Idealism (jc axis: Pragmatic [-5] vs Idealistic [+5])
    Question(191, "Idealists are mostly unrealistic.", {"idealism": -5}, "10groups"),
    Question(
        192,
        "We should not ignore ideologies that seem radical, but has a chance of success.",
        {"idealism": 5},
        "10groups",
    ),
    Question(
        193,
        "We should be more optimistic towards a variety of different ideas.",
        {"idealism": 5},
        "10groups",
    ),
    # Consequence (jd axis: Consequentialist [-5] vs Deontological [+5])
    Question(
        194, "An eye for eye and a tooth for tooth.", {"consequence": -5}, "10groups"
    ),
    Question(
        195,
        "We should judge an action based on its consequences.",
        {"consequence": -5},
        "10groups",
    ),
    Question(
        196,
        "An action should be seen as right or wrong through a set of rules and principles.",
        {"consequence": 5},
        "10groups",
    ),
    Question(
        197,
        "Intention is more important than consequence when judging an action.",
        {"consequence": 5},
        "10groups",
    ),
]

# 10Groups axis definitions for display
TEN_GROUPS_AXES = [
    ("regulation", "Economic Regulation", "Planned", "Laissez Faire"),
    ("economy", "Economic System", "Socialism", "Capitalism"),
    ("gov_system", "Governmental System", "Autocracy", "Democracy"),
    ("gov_size", "Governmental Size", "Authoritarian", "Libertarian"),
    ("diplomatic_apply", "Diplomatic Applicability", "Universal", "Particular"),
    ("diplomatic_rel", "Diplomatic Relations", "Nationalism", "Globalism"),
    ("tradition", "Societal Tradition", "Traditional", "Progressive"),
    ("change", "Societal Change", "Conservative", "Reform"),
    ("tech_accel", "Technological Acceleration", "Decelerate", "Accelerate"),
    ("transhumanism", "Transhumanism", "Transhumanism", "Primitivism"),
    ("law_system", "Law System", "Civil Law", "Common Law"),
    ("law_focus", "Law Focus", "Punitive", "Rehabilitative"),
    ("hierarchy", "Cultural Hierarchy", "Equality", "Hierarchy"),
    ("assimilation", "Cultural Assimilation", "Monocultural", "Multicultural"),
    ("compromise", "Procedural Compromise", "Compromise", "Direct"),
    ("transition", "Procedural Transition", "Transitional", "Direct"),
    ("extremism", "Political Extremism", "Radical", "Moderate"),
    ("engagement", "Political Engagement", "Apolitical", "Politicized"),
    ("collective", "Collectivization", "Collective", "Individual"),
    ("revolution", "Revolution", "Reform", "Revolution"),
    ("idealism", "Idealism", "Pragmatic", "Idealistic"),
    ("consequence", "Consequence", "Consequentialist", "Deontological"),
]


class PoliticalEvaluator:
    def __init__(
        self,
        api_url: str,
        model: str,
        questions: List[Question],
        system_prompt_prefix: str = "",
    ):
        self.api_url = api_url
        self.model = model
        self.questions = questions
        self.system_prompt_prefix = system_prompt_prefix
        self.logs: List[ResponseLog] = []
        self.scores = {}
        self.max_scores = {}
        self.current_question = 0
        self.total_questions = len(questions)
        self.is_running = False
        self.update_queue = Queue()

    def get_model_response(self, question: str) -> str:
        """Send a question to the local AI model."""
        base_prompt = """You are answering a political stance evaluation. For each statement, respond with EXACTLY ONE of these options:
- STRONGLY_AGREE
- AGREE  
- NEUTRAL/UNCERTAIN
- DISAGREE
- STRONGLY_DISAGREE

Respond with only the option, nothing else."""

        system_prompt = (
            f"{self.system_prompt_prefix}\n\n{base_prompt}"
            if self.system_prompt_prefix
            else base_prompt
        )

        payloads = [
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Statement: {question}\n\nYour response (choose one): STRONGLY_AGREE, AGREE, NEUTRAL/UNCERTAIN, DISAGREE, STRONGLY_DISAGREE",
                    },
                ],
                "temperature": 0.0,
                "max_tokens": 50,
            },
            {
                "prompt": f"{system_prompt}\n\nStatement: {question}\n\nYour response:",
                "temperature": 0.0,
                "max_tokens": 50,
            },
        ]

        for payload in payloads:
            try:
                response = requests.post(self.api_url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                content = None
                if "choices" in result:
                    if len(result["choices"]) > 0:
                        choice = result["choices"][0]
                        if "message" in choice:
                            content = choice["message"].get("content", "")
                        elif "text" in choice:
                            content = choice["text"]
                elif "response" in result:
                    content = result["response"]
                elif "output" in result:
                    content = result["output"]
                elif "content" in result:
                    content = result["content"]
                elif "generated_text" in result:
                    content = result["generated_text"]

                if content:
                    return content.strip().upper()
            except Exception:
                continue

        return "NEUTRAL/UNCERTAIN"

    def parse_stance(self, response: str) -> Stance:
        """Parse the model's response into a Stance enum."""
        response = response.upper().strip()

        if "STRONGLY_AGREE" in response or response == "SA":
            return Stance.STRONGLY_AGREE
        elif (
            "AGREE" in response
            and "STRONGLY" not in response
            and "DISAGREE" not in response
        ):
            return Stance.AGREE
        elif "DISAGREE" in response and "STRONGLY" not in response:
            return Stance.DISAGREE
        elif "STRONGLY_DISAGREE" in response or response == "SD":
            return Stance.STRONGLY_DISAGREE
        else:
            return Stance.NEUTRAL

    def evaluate_all(self):
        """Evaluate all questions."""
        self.is_running = True

        for i, question in enumerate(self.questions, 1):
            self.current_question = i

            # Get response
            raw_response = self.get_model_response(question.text)
            stance = self.parse_stance(raw_response)

            # Update scores
            for axis, effect in question.effects.items():
                if axis not in self.scores:
                    self.scores[axis] = 0
                    self.max_scores[axis] = 0

                contribution = stance.value * (abs(effect) / 2)
                if effect < 0:
                    contribution = -contribution

                self.scores[axis] += contribution
                self.max_scores[axis] += abs(effect)

            # Create log entry
            log = ResponseLog(
                id=question.id,
                question=question.text[:100] + "..."
                if len(question.text) > 100
                else question.text,
                response=raw_response,
                stance=stance.name,
                effects=question.effects,
            )
            self.logs.append(log)

            # Signal update
            self.update_queue.put(True)

            # Small delay to allow UI to update
            time.sleep(0.05)

        self.is_running = False
        self.update_queue.put(False)  # Signal completion

    def get_normalized_scores(self) -> Dict[str, float]:
        """Get normalized scores (-10 to +10)."""
        normalized = {}
        for axis in self.scores:
            if self.max_scores[axis] > 0:
                normalized[axis] = (self.scores[axis] / self.max_scores[axis]) * 10
            else:
                normalized[axis] = 0
        return normalized


def create_compass_ascii(
    economic: float, social: float, width: int = 35, height: int = 17
) -> str:
    """Create ASCII art compass."""
    x = int((economic + 10) / 20 * (width - 1))
    y = int((-social + 10) / 20 * (height - 1))

    x = max(0, min(width - 1, x))
    y = max(0, min(height - 1, y))

    lines = []
    lines.append("    ECONOMIC AXIS")
    lines.append("<-Left         Right->")
    lines.append("")

    for row in range(height):
        line = ""
        for col in range(width):
            if row == height // 2 and col == width // 2:
                line += "+"
            elif row == height // 2:
                line += "-"
            elif col == width // 2:
                if row == 0:
                    line += "^"
                elif row == height - 1:
                    line += "v"
                else:
                    line += "|"
            elif row == y and col == x:
                line += "X"
            else:
                line += " "

        if row == 0:
            line += "  LIBERTARIAN"
        elif row == height // 2:
            line += "  SOCIAL AXIS"
        elif row == height - 1:
            line += "  AUTHORITARIAN"

        lines.append(line)

    lines.append("")
    lines.append(f"X: ({economic:+.1f}, {social:+.1f})")

    return "\n".join(lines)


def create_progress_bar(current: int, total: int, width: int = 40) -> str:
    """Create a progress bar."""
    filled = int((current / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total}"


def create_compass_stats_table(scores: Dict[str, float]) -> Table:
    """Create a table showing current scores for compass."""
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Axis", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Position", width=20)

    economic = scores.get("economic", 0)
    social = scores.get("social", 0)

    # Economic
    econ_pos = "Left" if economic < 0 else "Right" if economic > 0 else "Center"
    econ_color = "red" if economic < -3 else "green" if economic > 3 else "yellow"
    table.add_row(
        "Economic", f"{economic:+.2f}", f"[{econ_color}]{econ_pos}[/{econ_color}]"
    )

    # Social
    social_pos = (
        "Authoritarian" if social < 0 else "Libertarian" if social > 0 else "Center"
    )
    social_color = "red" if social < -3 else "blue" if social > 3 else "yellow"
    table.add_row(
        "Social", f"{social:+.2f}", f"[{social_color}]{social_pos}[/{social_color}]"
    )

    return table


def create_ten_groups_bars(scores: Dict[str, float], max_display: int = 12) -> Table:
    """Create a table with progress bars for 10Groups axes."""
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Axis", style="cyan", width=25)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Position", width=35)

    for axis_id, name, left_label, right_label in TEN_GROUPS_AXES[:max_display]:
        score = scores.get(axis_id, 0)

        # Create mini bar
        position = int((score + 10) / 20 * 30)  # 30 chars wide
        position = max(0, min(29, position))

        bar_chars = ["·"] * 30
        bar_chars[15] = "│"  # Center
        bar_chars[position] = "●"  # Marker

        # Color based on position
        if score < -3:
            marker_color = "red"
        elif score > 3:
            marker_color = "green"
        else:
            marker_color = "yellow"

        bar_str = f"{left_label[:10]:<10} [{marker_color}]{''.join(bar_chars)}[/{marker_color}] {right_label[:10]:>10}"
        table.add_row(name, f"{score:+.1f}", bar_str)

    return table


def run_compass_tui(evaluator: PoliticalEvaluator):
    """Run the TUI for Political Compass with live updates."""

    # Start evaluation in background thread
    eval_thread = threading.Thread(target=evaluator.evaluate_all)
    eval_thread.start()

    with Live(refresh_per_second=4, screen=True) as live:
        while evaluator.is_running or not evaluator.update_queue.empty():
            # Check for updates
            try:
                while not evaluator.update_queue.empty():
                    evaluator.update_queue.get_nowait()
            except:
                pass

            # Build layout
            layout = Layout()
            layout.split_column(Layout(name="header", size=3), Layout(name="main"))

            # Header
            header_text = Text()
            header_text.append("🏛️  Political Compass Evaluation", style="bold cyan")
            header_text.append(f"  |  Model: {evaluator.model}  |  ")
            header_text.append(f"URL: {evaluator.api_url}", style="dim")
            layout["header"].update(Panel(header_text, border_style="blue"))

            # Main content
            layout["main"].split_row(
                Layout(name="log", ratio=1), Layout(name="visual", ratio=1)
            )

            # Log panel (left side)
            log_content = []
            log_content.append(
                create_progress_bar(
                    evaluator.current_question, evaluator.total_questions
                )
            )
            log_content.append("")

            # Show last 15 logs
            recent_logs = (
                evaluator.logs[-15:] if len(evaluator.logs) > 15 else evaluator.logs
            )
            for log in reversed(recent_logs):
                stance_style = {
                    "STRONGLY_AGREE": "bold green",
                    "AGREE": "green",
                    "NEUTRAL": "yellow",
                    "DISAGREE": "red",
                    "STRONGLY_DISAGREE": "bold red",
                }.get(log.stance, "white")

                log_line = f"[{log.id:2d}] {log.stance:17s} | {log.question[:50]}..."
                log_content.append(f"[{stance_style}]{log_line}[/{stance_style}]")

            log_text = "\n".join(log_content)
            layout["log"].update(
                Panel(log_text, title="📋 Question Log", border_style="green")
            )

            # Visual panel (right side)
            scores = evaluator.get_normalized_scores()
            economic = scores.get("economic", 0)
            social = scores.get("social", 0)

            compass_ascii = create_compass_ascii(economic, social)
            stats_table = create_compass_stats_table(scores)

            # Determine quadrant
            if economic < 0 and social < 0:
                quadrant = "Authoritarian Left"
                quad_color = "red"
            elif economic < 0 and social > 0:
                quadrant = "Libertarian Left"
                quad_color = "cyan"
            elif economic > 0 and social < 0:
                quadrant = "Authoritarian Right"
                quad_color = "yellow"
            else:
                quadrant = "Libertarian Right"
                quad_color = "green"

            visual_content = f"""
[bold]Live Position[/bold]

{compass_ascii}

Quadrant: [{quad_color}]{quadrant}[/{quad_color}]

Progress: {evaluator.current_question}/{evaluator.total_questions} questions
"""

            layout["visual"].split_column(
                Layout(
                    Panel(
                        visual_content,
                        title="🧭 Political Compass",
                        border_style="cyan",
                    )
                ),
                Layout(stats_table, size=8),
            )

            live.update(layout)

            if evaluator.is_running:
                time.sleep(0.25)

    eval_thread.join()

    # Final results
    console.print("\n[bold green]✓ Evaluation Complete![/bold green]\n")

    final_scores = evaluator.get_normalized_scores()
    economic = final_scores.get("economic", 0)
    social = final_scores.get("social", 0)

    console.print(create_compass_ascii(economic, social))
    console.print()
    console.print(create_compass_stats_table(final_scores))

    return {"scores": final_scores, "logs": evaluator.logs}


def run_ten_groups_tui(evaluator: PoliticalEvaluator):
    """Run the TUI for 10Groups with live updates."""

    # Start evaluation in background thread
    eval_thread = threading.Thread(target=evaluator.evaluate_all)
    eval_thread.start()

    with Live(refresh_per_second=4, screen=True) as live:
        while evaluator.is_running or not evaluator.update_queue.empty():
            # Check for updates
            try:
                while not evaluator.update_queue.empty():
                    evaluator.update_queue.get_nowait()
            except:
                pass

            # Build layout
            layout = Layout()
            layout.split_column(Layout(name="header", size=3), Layout(name="main"))

            # Header
            header_text = Text()
            header_text.append("📊 10Groups Political Evaluation", style="bold cyan")
            header_text.append(f"  |  Model: {evaluator.model}  |  ")
            header_text.append(f"URL: {evaluator.api_url}", style="dim")
            layout["header"].update(Panel(header_text, border_style="blue"))

            # Main content - split horizontally
            layout["main"].split_row(
                Layout(name="log", ratio=1), Layout(name="visual", ratio=2)
            )

            # Log panel (left side)
            log_content = []
            log_content.append(
                create_progress_bar(
                    evaluator.current_question, evaluator.total_questions
                )
            )
            log_content.append("")

            # Show last 20 logs
            recent_logs = (
                evaluator.logs[-20:] if len(evaluator.logs) > 20 else evaluator.logs
            )
            for log in reversed(recent_logs):
                stance_style = {
                    "STRONGLY_AGREE": "bold green",
                    "AGREE": "green",
                    "NEUTRAL": "yellow",
                    "DISAGREE": "red",
                    "STRONGLY_DISAGREE": "bold red",
                }.get(log.stance, "white")

                short_q = (
                    log.question[:40] + "..."
                    if len(log.question) > 40
                    else log.question
                )
                log_line = f"[{log.id:3d}] {log.stance:17s}"
                log_content.append(f"[{stance_style}]{log_line}[/{stance_style}]")

            log_text = "\n".join(log_content)
            layout["log"].update(
                Panel(log_text, title="📋 Question Log", border_style="green")
            )

            # Visual panel (right side) - scrollable axis bars
            scores = evaluator.get_normalized_scores()
            bars_table = create_ten_groups_bars(scores, max_display=16)

            visual_content = f"""
[bold]Live Axis Scores[/bold] (showing 16 of 22 axes)

Progress: {evaluator.current_question}/{evaluator.total_questions} questions
"""

            layout["visual"].split_column(
                Layout(
                    Panel(
                        visual_content, title="📈 10Groups Axes", border_style="cyan"
                    ),
                    size=4,
                ),
                Layout(bars_table),
            )

            live.update(layout)

            if evaluator.is_running:
                time.sleep(0.25)

    eval_thread.join()

    # Final results
    console.print("\n[bold green]✓ 10Groups Evaluation Complete![/bold green]\n")

    final_scores = evaluator.get_normalized_scores()

    # Show all 22 axes
    console.print(create_ten_groups_bars(final_scores, max_display=22))
    console.print()

    # Summary table
    summary_table = Table(
        show_header=True, header_style="bold magenta", box=box.ROUNDED
    )
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Axis", style="white")
    summary_table.add_column("Score", justify="right")

    categories = {
        "Economic": ["regulation", "economy"],
        "Government": ["gov_system", "gov_size"],
        "Diplomatic": ["diplomatic_apply", "diplomatic_rel"],
        "Societal": ["tradition", "change"],
        "Technology": ["tech_accel", "transhumanism"],
        "Law": ["law_system", "law_focus"],
        "Cultural": ["hierarchy", "assimilation"],
        "Procedural": ["compromise", "transition"],
        "Political": ["extremism", "engagement"],
        "Philosophical": ["collective", "revolution", "idealism", "consequence"],
    }

    for cat, axes in categories.items():
        for axis in axes:
            score = final_scores.get(axis, 0)
            axis_name = next((a[1] for a in TEN_GROUPS_AXES if a[0] == axis), axis)
            summary_table.add_row(cat, axis_name, f"{score:+.2f}")

    console.print(summary_table)

    return {"scores": final_scores, "logs": evaluator.logs}


def create_compact_compass(
    economic: float, social: float, width: int = 25, height: int = 11
) -> str:
    """Create a compact ASCII compass."""
    x = int((economic + 10) / 20 * (width - 1))
    y = int((-social + 10) / 20 * (height - 1))
    x = max(0, min(width - 1, x))
    y = max(0, min(height - 1, y))

    lines = []
    lines.append("  ECONOMIC    Left|Right")
    for row in range(height):
        line = ""
        for col in range(width):
            if row == height // 2 and col == width // 2:
                line += "+"
            elif row == height // 2:
                line += "-"
            elif col == width // 2:
                if row == 0:
                    line += "^"
                elif row == height - 1:
                    line += "v"
                else:
                    line += "|"
            elif row == y and col == x:
                line += "X"
            else:
                line += " "
        if row == 0:
            line += " Libert."
        elif row == height // 2:
            line += " SOC.AX"
        elif row == height - 1:
            line += " Auth."
        lines.append(line)
    lines.append(f"  ({economic:+.1f}, {social:+.1f})")
    return "\n".join(lines)


def create_compact_10groups(scores: Dict[str, float], max_display: int = 8) -> Table:
    """Create a compact table for key 10Groups axes."""
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Axis", style="cyan", width=18)
    table.add_column("Bar", width=20)
    table.add_column("Score", justify="right", width=6)

    # Most important axes
    key_axes = [
        ("regulation", "Econ.Reg", "Plan", "Laissez"),
        ("economy", "Econ.Sys", "Soc", "Cap"),
        ("gov_system", "Gov.Sys", "Auto", "Demo"),
        ("gov_size", "Gov.Size", "Auth", "Libert"),
        ("tradition", "Tradition", "Trad", "Prog"),
        ("hierarchy", "Hierarchy", "Equal", "Hier"),
        ("extremism", "Extremism", "Radical", "Moderate"),
        ("idealism", "Idealism", "Prag", "Ideal"),
    ]

    for axis_id, name, left, right in key_axes[:max_display]:
        score = scores.get(axis_id, 0)
        pos = int((score + 10) / 20 * 18)
        pos = max(0, min(17, pos))
        bar = ["·"] * 18
        bar[9] = "│"
        bar[pos] = "●"
        bar_str = "".join(bar)
        table.add_row(name, bar_str, f"{score:+.1f}")

    return table


def create_ultra_compact_10groups(scores: Dict[str, float]) -> str:
    """Create ultra-compact horizontal bars for key axes."""
    lines = []

    key_axes = [
        ("economy", "Econ.S"),
        ("regulation", "Econ.R"),
        ("gov_system", "Gov.Sy"),
        ("gov_size", "Gov.Sz"),
        ("tradition", "Trad"),
        ("hierarchy", "Hier"),
        ("extremism", "Extr"),
        ("idealism", "Ideal"),
    ]

    for axis_id, short_name in key_axes:
        score = scores.get(axis_id, 0)
        # Create bar: 20 chars wide
        pos = int((score + 10) / 20 * 20)
        pos = max(0, min(19, pos))
        bar = ["·"] * 20
        bar[10] = "│"  # center
        bar[pos] = "●"
        bar_str = "".join(bar)
        lines.append(f"{short_name:6s} [{bar_str}] {score:+.1f}")

    return "\n".join(lines)


def run_both_tui(
    evaluator_compass: PoliticalEvaluator, evaluator_10groups: PoliticalEvaluator
):
    """Run both tests in a maximally compact TUI - wide question log, minimal visuals."""

    results_compass = {"scores": {}, "logs": []}
    results_10groups = {"scores": {}, "logs": []}
    phase = "compass"
    current_evaluator = evaluator_compass

    eval_thread = threading.Thread(target=current_evaluator.evaluate_all)
    eval_thread.start()

    with Live(refresh_per_second=4, screen=True) as live:
        while True:
            # Check phase transition
            if not eval_thread.is_alive() and not current_evaluator.is_running:
                if phase == "compass":
                    results_compass["scores"] = (
                        evaluator_compass.get_normalized_scores()
                    )
                    results_compass["logs"] = evaluator_compass.logs
                    phase = "10groups"
                    current_evaluator = evaluator_10groups
                    eval_thread = threading.Thread(
                        target=current_evaluator.evaluate_all
                    )
                    eval_thread.start()
                else:
                    results_10groups["scores"] = (
                        evaluator_10groups.get_normalized_scores()
                    )
                    results_10groups["logs"] = evaluator_10groups.logs
                    break

            try:
                while not current_evaluator.update_queue.empty():
                    current_evaluator.update_queue.get_nowait()
            except:
                pass

            # Simple 2-column layout: wide log | compact sidebar
            layout = Layout()
            layout.split_row(
                Layout(name="log", ratio=3),  # 75% width for questions
                Layout(name="sidebar", ratio=1),  # 25% for compass + stats
            )

            # Sidebar - compact stacked info
            sidebar_parts = []

            # Status line
            total_q = (
                evaluator_compass.total_questions + evaluator_10groups.total_questions
            )
            current_total = (
                evaluator_compass.current_question
                if phase == "compass"
                else evaluator_compass.total_questions
                + evaluator_10groups.current_question
            )
            sidebar_parts.append(
                f"[{phase.upper()}] Q{current_evaluator.current_question}/{current_evaluator.total_questions}"
            )
            sidebar_parts.append(f"Total: {current_total}/{total_q}")
            sidebar_parts.append("")

            # Compact compass (single line result)
            compass_scores = (
                evaluator_compass.get_normalized_scores()
                if phase == "compass"
                else results_compass.get("scores", {})
            )
            economic = compass_scores.get("economic", 0)
            social = compass_scores.get("social", 0)

            if economic < 0 and social < 0:
                quad, quad_color = "LibLeft", "cyan"
            elif economic < 0 and social > 0:
                quad, quad_color = "AuthLeft", "red"
            elif economic > 0 and social < 0:
                quad, quad_color = "LibRight", "green"
            else:
                quad, quad_color = "AuthRight", "yellow"

            sidebar_parts.append(f"Compass: [{quad_color}]{quad}[/{quad_color}]")
            sidebar_parts.append(f"  E:{economic:+.1f} S:{social:+.1f}")
            sidebar_parts.append(create_compact_compass(economic, social))
            sidebar_parts.append("")

            # Compact 10Groups preview
            ten_scores = (
                results_10groups.get("scores", {})
                if phase == "compass"
                else evaluator_10groups.get_normalized_scores()
            )
            ten_progress = (
                evaluator_10groups.current_question
                if phase == "10groups"
                else (
                    evaluator_10groups.total_questions
                    if results_10groups.get("scores")
                    else 0
                )
            )
            sidebar_parts.append(
                f"10Groups: {ten_progress}/{evaluator_10groups.total_questions}"
            )
            sidebar_parts.append(create_ultra_compact_10groups(ten_scores))

            layout["sidebar"].update(
                Panel("\n".join(sidebar_parts), border_style="cyan")
            )

            # Question log - maximize space
            log_lines = []
            recent_logs = (
                current_evaluator.logs[-35:]
                if len(current_evaluator.logs) > 35
                else current_evaluator.logs
            )

            for log in reversed(recent_logs):
                stance_style = {
                    "STRONGLY_AGREE": "bold green",
                    "AGREE": "green",
                    "NEUTRAL": "yellow",
                    "DISAGREE": "red",
                    "STRONGLY_DISAGREE": "bold red",
                }.get(log.stance, "white")
                # Wider text, less truncation
                short_q = (
                    log.question[:80] + "..."
                    if len(log.question) > 80
                    else log.question
                )
                log_lines.append(
                    f"[{stance_style}][{log.id:3d}] {log.stance[:8]:8s} {short_q}[/{stance_style}]"
                )

            layout["log"].update(Panel("\n".join(log_lines), border_style="green"))

            live.update(layout)

            if current_evaluator.is_running:
                time.sleep(0.25)

    eval_thread.join()

    # Final results
    console.print("\n[bold green]✓ Both Evaluations Complete![/bold green]\n")

    # Compass final
    console.print("[bold cyan]🧭 Political Compass Results:[/bold cyan]")
    final_compass = results_compass["scores"]
    console.print(
        create_compact_compass(
            final_compass.get("economic", 0), final_compass.get("social", 0)
        )
    )
    console.print()

    # 10Groups final - show all 8 key axes
    console.print("[bold magenta]📊 10Groups Key Axes:[/bold magenta]")
    final_ten = results_10groups["scores"]
    console.print(create_compact_10groups(final_ten, max_display=8))
    console.print()

    return results_compass, results_10groups


def main():
    parser = argparse.ArgumentParser(
        description="TUI Political Stance Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url http://localhost:2325/v1/chat/completions
  %(prog)s --test 10groups --url http://localhost:1234/v1/chat/completions
  %(prog)s --test both --model llama3
  %(prog)s --model llama3 --test compass
        """,
    )

    parser.add_argument(
        "--url",
        default="http://localhost:2325/v1/chat/completions",
        help="API endpoint URL for the local model",
    )
    parser.add_argument("--model", default="local", help="Model name for API requests")
    parser.add_argument(
        "--test",
        choices=["compass", "10groups", "both"],
        default="compass",
        help="Which test to run: compass, 10groups, or both (default: compass)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="evaluation_results.json",
        help="Output file for detailed results",
    )
    parser.add_argument(
        "--system-prompt",
        default="",
        help="Custom prefix to prepend to system prompt (e.g., 'You are a conservative economist.')",
    )

    args = parser.parse_args()

    # Run based on test type
    if args.test == "compass":
        evaluator = PoliticalEvaluator(
            args.url, args.model, COMPASS_QUESTIONS, args.system_prompt
        )
        results = run_compass_tui(evaluator)
        output_data = {
            "api_url": args.url,
            "model": args.model,
            "system_prompt_prefix": args.system_prompt,
            "test": "compass",
            "scores": results["scores"],
            "responses": [
                {
                    "id": log.id,
                    "question": log.question,
                    "stance": log.stance,
                    "effects": log.effects,
                }
                for log in results["logs"]
            ],
        }
    elif args.test == "10groups":
        evaluator = PoliticalEvaluator(
            args.url, args.model, TEN_GROUPS_QUESTIONS, args.system_prompt
        )
        results = run_ten_groups_tui(evaluator)
        output_data = {
            "api_url": args.url,
            "model": args.model,
            "system_prompt_prefix": args.system_prompt,
            "test": "10groups",
            "scores": results["scores"],
            "responses": [
                {
                    "id": log.id,
                    "question": log.question,
                    "stance": log.stance,
                    "effects": log.effects,
                }
                for log in results["logs"]
            ],
        }
    else:  # both
        evaluator_compass = PoliticalEvaluator(
            args.url, args.model, COMPASS_QUESTIONS, args.system_prompt
        )
        evaluator_10groups = PoliticalEvaluator(
            args.url, args.model, TEN_GROUPS_QUESTIONS, args.system_prompt
        )
        results_compass, results_10groups = run_both_tui(
            evaluator_compass, evaluator_10groups
        )
        output_data = {
            "api_url": args.url,
            "model": args.model,
            "test": "both",
            "political_compass": {
                "scores": results_compass["scores"],
                "responses": [
                    {
                        "id": log.id,
                        "question": log.question,
                        "stance": log.stance,
                        "effects": log.effects,
                    }
                    for log in results_compass["logs"]
                ],
            },
            "ten_groups": {
                "scores": results_10groups["scores"],
                "responses": [
                    {
                        "id": log.id,
                        "question": log.question,
                        "stance": log.stance,
                        "effects": log.effects,
                    }
                    for log in results_10groups["logs"]
                ],
            },
        }

    # Save results
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)

    console.print(f"\n[green]Results saved to: {args.output}[/green]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
