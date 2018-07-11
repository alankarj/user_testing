informable_slots = ['genre', 'actor', 'director']
requestable_slots = ['genre', 'actor']

informable_slots_pseudo = ['last_movie_like', 'reason_like', 'reason_not_like', 'feedback']
requestable_slots_pseudo = ['another_one', 'movie_info']

max_recos = 2

non_reqinf_user_ts = ['greeting', 'affirm', 'negate', 'bye']

prob_user_behaviour = {}
# The following determines the preference probabilities for requestable_slots
prob_user_behaviour['request_slot'] = {'genre': 0.34, 'actor': 0.33, 'movie_info': 0.33}  # request the requestable slot with this probability
prob_user_behaviour['inform_slot'] = {'genre': 0.34, 'actor': 0.33, 'director': 0.33}  # request t
# Reco acceptance is a geometric random variable with the following parameter
prob_user_behaviour['acceptance'] = 0.5
prob_user_behaviour['noise'] = 0.0


def get_prob_user_profile():
    prob_user_profile = {}
    pass
    prob_user_profile['conv_goal_type'] = {'i': 0.5, 'p': 0.5}
    prob_user_profile['initiative'] = {'high': 0.5, 'low': 0.5}
    prob_user_profile['cooperation_type'] = {'cooperative': 0.9, 'uncooperative': 0.1}

    # The following determines the preference probabilities for informable_slots
    for inf_slot in informable_slots:
        prob_user_profile[inf_slot + '_preference'] = {'single_preference': 0.5, 'no_preference': 0.5}

    return prob_user_profile


# def get_all_user_ts():
#     inf_user_ts = ['inform(' + inf_slot + ')' for inf_slot in informable_slots]
#     inf_user_ts.extend(['inform(' + inf_slot + ')' for inf_slot in informable_slots_pseudo])
#     req_user_ts = ['request(' + req_slot + ')' for req_slot in requestable_slots]
#     req_user_ts.extend(['request(' + req_slot + ')' for req_slot in requestable_slots_pseudo])
#     return non_reqinf_user_ts + inf_user_ts + req_user_ts


def construct_ts(intent, slot=None, value=None):
    if intent == 'request':
        ts = {'intent': intent, 'slot': slot}
    elif intent == 'inform':
        ts = {'intent': intent, 'slot': slot, 'value': value}
    else:
        ts = {'intent': intent}
    return ts