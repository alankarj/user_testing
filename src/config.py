# User Profile Probability keys and values:
CONV_GOAL_TYPE_STR = 'conv_goal_type'
INITIATIVE_TYPE_STR = 'initiative'
COOPERATION_TYPE_STR = 'cooperation_type'
SLOT_PREFERENCE_TYPE_STR = '_preference'

CONV_GOAL_TYPES = ['i', 'p']
INITIATIVE_TYPES = ['high', 'low']
COOPERATION_TYPES = ['cooperative', 'uncooperative']
SLOT_PREFERENCE_TYPES = ['single_preference', 'no_preference']

ACCEPTANCE_STR = 'acceptance'
NOISE_STR = 'noise'

# STATE STR's:
TASK_STATE_STR = 'task_state'
SOCIAL_STATE_STR = 'social_state'
TURN_STR = 'turn'
PREV_AGENT_DF_STR = 'prev_agent_df'
PREV_USER_DF_STR = 'prev_user_df'
AGENT_DF_STR = 'agent_df'
USER_DF_STR = 'user_df'

# COMMON STR's:
REQUEST_STR = 'request'
INFORM_STR = 'inform'
INTENT_STR = 'intent'
SLOT_STR = 'slot'
VALUE_STR = 'value'

# Affirm-negate:
AFFIRM_STR = 'affirm'
NEGATE_STR = 'negate'

TS_STR = 'ts'
CS_STR = 'cs'

MOVIE_PLACEHOLDER = '#MOVIE'
GENRE_PLACEHOLDER = '#GENRE'
ACTOR_PLACEHOLDER = '#ACTOR'
MOVIE_INFO_PLACEHOLDER = '#MOVIE_INFO'

SLOT_LISTS_FILE_SUFFIX = '-list'

AGENT_TYPE = ['rule_based', 'rl']
AGENT_SOCIAL_TYPE = ['social', 'unsocial']

# Probabilities
CONV_GOAL_TYPES_PROB = [0.5, 0.5]
INITIATIVE_TYPES_PROB = [0.5, 0.5]
COOPERATION_TYPES_PROB = [0.9, 0.1]
SLOT_PREFERENCE_TYPES_PROB = [0.5, 0.5]
REQUEST_SLOTS_PROB = [0.34, 0.33, 0.33]
INFORM_SLOTS_PROB = [0.34, 0.33, 0.33]

# Conversational strategies
ALL_CONV_STRATEGIES = ['SD', 'PR', 'HE', 'QESD', 'VSN', 'NONE']
BLANK_DF = {TS_STR: {INTENT_STR: '', SLOT_STR: '', VALUE_STR: ''}, CS_STR: ''}

INFORMABLE_SLOTS = ['genre', 'actor', 'director']
REQUESTABLE_SLOTS = ['genre', 'actor']

INFORMABLE_SLOTS_PSEUDO = ['last_movie_like', 'reason_like', 'reason_not_like', 'feedback', 'another_one']
REQUESTABLE_SLOTS_PSEUDO = ['movie_info']

MAX_RECOS = 2
MAX_TURNS = 20

NON_REQINF_USER_TS = ['greeting', 'affirm', 'negate', 'bye']

PROB_USER_BEHAVIOUR = {}
pass
# The following determines the preference probabilities for requestable_slots.
# Request the requestable slots with this probability.
PROB_USER_BEHAVIOUR[REQUEST_STR + '_' + SLOT_STR] = dict(zip(REQUESTABLE_SLOTS + REQUESTABLE_SLOTS_PSEUDO, REQUEST_SLOTS_PROB))
# Request the informable slots with this probability.
PROB_USER_BEHAVIOUR[INFORM_STR + '_' + SLOT_STR] = dict(zip(INFORMABLE_SLOTS, INFORM_SLOTS_PROB))
# Reco acceptance is a geometric random variable with the following parameter.
PROB_USER_BEHAVIOUR[ACCEPTANCE_STR] = 0.5
PROB_USER_BEHAVIOUR[NOISE_STR] = 0.0


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


# def get_all_user_ts():
#     inf_user_ts = ['inform(' + inf_slot + ')' for inf_slot in informable_slots]
#     inf_user_ts.extend(['inform(' + inf_slot + ')' for inf_slot in informable_slots_pseudo])
#     req_user_ts = ['request(' + req_slot + ')' for req_slot in requestable_slots]
#     req_user_ts.extend(['request(' + req_slot + ')' for req_slot in requestable_slots_pseudo])
#     return non_reqinf_user_ts + inf_user_ts + req_user_ts


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
    if intent == '':
        return intent, None
    slot = ts[SLOT_STR]
    value = ts[VALUE_STR]
    return intent + '(' + slot + ')', value


def parse_ts(ts_string):
    split_string = ts_string.split('(')
    intent = split_string[0]
    if len(split_string) > 1:
        slot = split_string[1].rstrip(')')
    else:
        slot = None
    return construct_ts(intent, slot)


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
    return MOVIE_PLACEHOLDER
