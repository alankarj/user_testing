# Main file constants
CONTEXT_KEY = 0  # Key to uniquely determine context for affirm/negate
AGENT_KEY = 1  # Column ID of the key for programmed agent reasoner (prev_user_ts)
USER_KEY = 3  # Column ID of the key for user simulator reasoner (agent_ts)
NUM_FIELDS_KEYS = 2  # Number of fields for agent/user simulator reasoner keys (ts, cs)

FILE_DELIMITER = '\t'  # TSV files
OPTIONS_DELIMITER = ','  # Delimiter used for different ts/cs options

NUM_FIELDS_NLG_AGENT = 5
NUM_FIELDS_NLG_USER = 3

# String constants
# User Profile Probability keys and values:
CONV_GOAL_TYPE_STR = 'conv_goal_type'
INITIATIVE_TYPE_STR = 'initiative'
COOPERATION_TYPE_STR = 'cooperation_type'
SLOT_PREFERENCE_TYPE_STR = '_preference'
INFORM_REQUEST_MOVIE_STR = 'inform_request'

ACCEPTANCE_STR = 'acceptance'
NOISE_STR = 'noise'

# STATE STR's:
TASK_STATE_STR = 'task_state'
SOCIAL_STATE_STR = 'social_state'
TURN_STR = 'turn'
RECOS_STR = 'recos'
PREV_AGENT_DF_STR = 'prev_agent_df'
PREV_USER_DF_STR = 'prev_user_df'
AGENT_DF_STR = 'agent_df'
USER_DF_STR = 'user_df'
AGENT_ACK_DF_STR = 'ack_df'

# COMMON STR's:
REQUEST_STR = 'request'
INFORM_STR = 'inform'
INTENT_STR = 'intent'
SLOT_STR = 'slot'
VALUE_STR = 'value'
MOVIE_STR = 'movie'

# Affirm-negate:
AFFIRM_STR = 'affirm'
NEGATE_STR = 'negate'

TS_STR = 'ts'
CS_STR = 'cs'

MOVIE_PLACEHOLDER = '#MOVIE'
GENRE_PLACEHOLDER = '#GENRE'
ACTOR_PLACEHOLDER = '#ACTOR'
MOVIE_INFO_PLACEHOLDER = '#MOVIE_INFO'
REQUEST_PLACEHOLDER = '#REQUESTED'

SLOT_LISTS_FILE_SUFFIX = '-list'

ACK_STR = 'ack'
OTHER_STR = 'other'

USER_STR = 'USER'
AGENT_STR = 'SARA'


# List constants
CONV_GOAL_TYPES = ['i', 'p']
INITIATIVE_TYPES = ['high', 'low']
COOPERATION_TYPES = ['cooperative', 'uncooperative']
SLOT_PREFERENCE_TYPES = ['single_preference', 'no_preference']
INFORM_REQUEST_MOVIE_TYPES = ['request', 'inform']

AGENT_TYPE = ['rule_based', 'rl']
AGENT_SOCIAL_TYPE = ['unsocial', 'part-social', 'full-social']

NON_REQINF_USER_TS = ['greeting', 'affirm', 'negate', 'bye']

ALL_CONV_STRATEGIES = ['SD', 'PR', 'HE', 'QESD', 'VSN', 'NONE']
INFORM_MOVIES_CS_LIST = ['QESD', 'SD', 'PR', 'VSN']

INFORMABLE_SLOTS = ['genre', 'director', 'actor']
REQUESTABLE_SLOTS = ['genre', 'actor']

INFORMABLE_SLOTS_PSEUDO = ['last_movie', 'reason_like', 'reason_not_like', 'feedback', 'another_one']
REQUESTABLE_SLOTS_PSEUDO = ['movie_info']

AGENT_TS_STRINGS = ['introduce', 'request(last_movie)', 'request', 'inform(movie)', 'request(another_one)', 'inform']
INFORMABLE_SLOTS_PSEUDO_PLACEHOLDERS = ['#LAST_MOVIE', '#REASON_LIKE', '#REASON_NOT_LIKE', '#FEEDBACK', '#ANOTHER_ONE']

# Integer constants
# Order of next() function output:
TS_STR_INDEX_AGENT = 2
CS_STR_INDEX_AGENT = 3
SLOT_VALUE_INDEX_AGENT = 4

TS_STR_INDEX_USER = 0
CS_STR_INDEX_USER = 1
SLOT_VALUE_INDEX_USER = 2

REQ_MOVIE_INDEX = 2
INF_MOVIE_INDEX = 5

MAX_RECOS = 2
MAX_TURNS = 20

AGENT_ACTION_DIM = 5
USER_ACTION_DIM = 3

# Probabilities
CONV_GOAL_TYPES_PROB = [0.5, 0.5]
INITIATIVE_TYPES_PROB = [0.5, 0.5]
COOPERATION_TYPES_PROB = [0.9, 0.1]
SLOT_PREFERENCE_TYPES_PROB = [0.5, 0.5]
REQUEST_SLOTS_PROB = [0.34, 0.33, 0.33]
INFORM_SLOTS_PROB = [0.25, 0.25, 0.25, 0.25]
INFORM_REQUEST_MOVIE_PROB = [0.5, 0.5]
PROB_INFORM_REQUEST_MOVIE = 0.5  # With this probability, either request more information or inform actor/genre/director

# Derived constants
BLANK_DF = {TS_STR: {INTENT_STR: '', SLOT_STR: '', VALUE_STR: ''}, CS_STR: ''}
AGENT_INFORM_SLOTS_PLACEHOLDERS = dict(zip(REQUESTABLE_SLOTS + REQUESTABLE_SLOTS_PSEUDO,
                                           [GENRE_PLACEHOLDER, ACTOR_PLACEHOLDER, MOVIE_INFO_PLACEHOLDER]))

PROB_USER_BEHAVIOUR = {}
pass
# The following determines the preference probabilities for requestable_slots.
# Request the requestable slots with this probability.
PROB_USER_BEHAVIOUR[REQUEST_STR + '_' + SLOT_STR] = dict(zip(REQUESTABLE_SLOTS + REQUESTABLE_SLOTS_PSEUDO, REQUEST_SLOTS_PROB))
# Request the informable slots with this probability.
PROB_USER_BEHAVIOUR[INFORM_STR + '_' + SLOT_STR] = dict(zip(INFORMABLE_SLOTS + [INFORMABLE_SLOTS_PSEUDO[-1]], INFORM_SLOTS_PROB))
# Reco acceptance is a geometric random variable with the following parameter.
PROB_USER_BEHAVIOUR[ACCEPTANCE_STR] = 0.5
PROB_USER_BEHAVIOUR[NOISE_STR] = 0.0
PROB_USER_BEHAVIOUR[INFORM_REQUEST_MOVIE_STR] = dict(zip(INFORM_REQUEST_MOVIE_TYPES, INFORM_REQUEST_MOVIE_PROB))

BASE_LOOP_KEYS = [INFORM_STR + '(' + MOVIE_STR + ')', REQUEST_STR + '(' + INFORMABLE_SLOTS_PSEUDO[-1] + ')']


# Functions


def get_prob_user_profile():
    prob_user_profile = {}
    pass
    prob_user_profile[CONV_GOAL_TYPE_STR] = dict(zip(CONV_GOAL_TYPES, CONV_GOAL_TYPES_PROB))
    prob_user_profile[INITIATIVE_TYPE_STR] = dict(zip(INITIATIVE_TYPES, INITIATIVE_TYPES_PROB))
    prob_user_profile[COOPERATION_TYPE_STR] = dict(zip(COOPERATION_TYPES, COOPERATION_TYPES_PROB))

    # The following determines the preference probabilities for informable_slots
    for inf_slot in INFORMABLE_SLOTS:
        prob_user_profile[inf_slot + SLOT_PREFERENCE_TYPE_STR] = dict(zip(SLOT_PREFERENCE_TYPES, SLOT_PREFERENCE_TYPES_PROB))

    return prob_user_profile


def construct_ts(intent, slot=None, value=None):
    if intent == REQUEST_STR:
        ts = {INTENT_STR: intent, SLOT_STR: slot, VALUE_STR: ''}
    elif intent == INFORM_STR:
        ts = {INTENT_STR: intent, SLOT_STR: slot, VALUE_STR: value}
    else:
        ts = {INTENT_STR: intent, SLOT_STR: '', VALUE_STR: ''}
    return ts


def deconstruct_ts(ts):
    intent = ts[INTENT_STR]
    slot = ts[SLOT_STR]
    value = ts[VALUE_STR]
    if intent == '' or slot == '':
        return intent, value
    ts_string = intent + '(' + slot + ')'
    return ts_string, value


def parse_ts_string(ts_string):
    if ts_string == '':
        return '', ''
    split_string = ts_string.split('(')
    intent = split_string[0]
    if len(split_string) > 1:
        slot = split_string[1].rstrip(')')
    else:
        slot = ''
    return intent, slot


def interface_with_recommendation_system(slot_values):
    """
    Gets movie recommendation from recommendation system.
    Input: slot_values: dict with keys as slots, values as their corresponding values.
    For example: {genre: '', actor: 'Tom Cruise', director: 'Christopher Nolan'}
    Output: movie: string with movie name (only a placeholder in simulation).
    """
    return MOVIE_PLACEHOLDER


def interface_with_omdb(slot):
    """
    Gets movie information (movie_info / genre / actor) from recommendation system.
    Input: slot: either one of requestable_slots or requestable_slots_pseudo strings
    Output: movie: string with movie information desired (only a placeholder in simulation).
    """
    if slot not in REQUESTABLE_SLOTS + REQUESTABLE_SLOTS_PSEUDO:
        raise ValueError()
    return AGENT_INFORM_SLOTS_PLACEHOLDERS[slot]


def get_agent_loop_keys():
    loop_keys = []
    for s in INFORMABLE_SLOTS + [INFORMABLE_SLOTS_PSEUDO[-1]]:
        key = (BASE_LOOP_KEYS[0], INFORM_STR + '(' + s + ')', '')
        loop_keys.append(key)
    for s in REQUESTABLE_SLOTS + REQUESTABLE_SLOTS_PSEUDO:
        key = (INFORM_STR + '(' + s + ')', AFFIRM_STR, '')
        loop_keys.append(key)
    loop_keys.append((BASE_LOOP_KEYS[1], AFFIRM_STR, ''))
    return loop_keys
