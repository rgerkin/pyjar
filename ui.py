from datetime import datetime
from itertools import product
import numpy as np
import uuid

from . import io, config, vuetify_utils as vu

W = {}  # Created widgets
vu.W = W

def update(widget, event, data):
    question_type = get_question_type()
    vu.hide_widgets([W[x] for x in ['rank_select', 'rate_slider']])
    if question_type == 'done':
        W['instructions'].value = "You've completed all the trials!"
        return
    elif question_type == 'rank':
        update_rank_question()
    elif question_type == 'rate':
        update_rate_question()
        
    experimenter = curr_experimenter()
    n = sum([config.n_trials[x] for x in ('rate', 'rank')])
    k = sum([config.n_trials_completed[x][experimenter] for x in ('rate', 'rank')])
    W['progress_bar'].label = '%d/%d' % (k, n)
    W['progress_bar'].v_model = 100*(k/n)
    vu.show_widgets([W[x] for x in ['progress_bar', 'submit_button', 'confidence_checkbox']])
    config.q_start_time = datetime.now()
    
def submit_answer(widget, event, data):
    q_end_time = datetime.now()
    experimenter = W['experimenter_select'].v_model
    question_type = get_question_type()
    slots = W['submit_button'].slots
    jars = [jar for jar, slot in config.slot_map.items() if slot in slots]
    responder = 'rate_slider' if question_type=='rate' else 'rank_select'
    answer = str(W[responder].v_model)
    result = {'Experimenter': experimenter,
              't_start': str(config.q_start_time),
              't_end': str(q_end_time),
              'Slots': slots,
              'Jars': jars,
              'Question': question_type,
              'Answer': answer,}
    key = uuid.uuid4().hex
    io.write_result([key, result])
    config.n_trials_completed[question_type][experimenter] += 1
    update(widget, event, data)
    
"""
DEPRECATED
def start_stop(widget, event, data):
    if widget.status == 'Cold':
        widget.children = ['Stop']
        widget.status = 'Hot'
        vu.show_widgets(W.values())
    elif widget.status == 'Hot':
        widget.children = ['Start']
        widget.status = 'Cold'
        vu.hide_widgets(not_widgets=widget)
"""
        
def curr_experimenter():
    return W['experimenter_select'].v_model
    
def get_question_type():
    experimenter = curr_experimenter()
    frac = {x: config.n_trials_completed[x][experimenter] / config.n_trials[x] for x in ('rate', 'rank')}
    if frac['rate'] == 1 and frac['rank'] == 1:
        return 'done'
    elif frac['rate'] < frac['rank']:
        return 'rate'
    else:
        return 'rank'
    
def update_rate_question():
    experimenter = curr_experimenter()
    trial_num = config.n_trials_completed['rate'][experimenter]
    slot, rep = config.trials['rate'][trial_num]
    vu.show_widgets(W['rate_slider'])
    W['submit_button'].kind = 'rate'
    W['submit_button'].slots = [slot]
    W['rate_slider'].label = 'How intense is odorant %s' % slot
    W['rate_slider'].v_model = 50
    
def update_rank_question():
    experimenter = curr_experimenter()
    trial_num = config.n_trials_completed['rank'][experimenter]
    slot1, slot2, rep = config.trials['rank'][trial_num]
    signs = ['>>', '>', '=', '<', '<<']
    vu.show_widgets(W['rank_select'])
    W['submit_button'].kind = 'rank'
    W['submit_button'].slots = [slot1, slot2]
    W['rank_select'].label = 'Which odorant is more intense, %s or %s?' % (slot1, slot2)
    W['rank_select'].items = ['%s %s %s' % x for x in product([slot1], signs, [slot2])]
    n_rank_options = len(W['rank_select'].items)
    median = int((n_rank_options-1)/2)
    W['rank_select'].value = W['rank_select'].items[median]

def show_slot(widget, event, data):
    barcode = widget.v_model
    jar_id = io.barcode_to_jar_id(config.inventory, barcode)
    slot = config.slot_map.get(jar_id, 'Not Found')
    W['slot_field'].v_model = slot
    
def submit_randomize(widget, event, data):
    vu.show_widgets(W['prog_bar'])
    seed = W['seed_slider'].v_model
    np.random.seed(seed)
    randomized_slots = np.random.permutation(config.slots)
    config.slot_map = dict(zip(config.jar_ids, randomized_slots))
    key = "%s; seed: %d" % (io.now_str(), seed)
    io.write_slotmap(config.slot_map, key=key)
    W['instructions'].value = "Now use the barcode reader to determine the new locations for each jar."
    vu.hide_widgets(W['prog_bar'])
    
def check_seed(widget, event, data):
    seed = widget.v_model
    used_seeds = io.get_slotmap_seeds()
    disabled = seed in used_seeds
    vu.style_widgets('disabled', disabled, W['randomize_button'])
