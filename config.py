from . import io
from datetime import datetime
from itertools import product, combinations
import numpy as np

# Editable options
letters = 'ABCDEFG'
numbers = '123456'
experimenters = ['Tisha',
                 'Jaelyn',
                 'Rick']

# Identify all the jars that will be used
inventory = io.get_inventory()
jar_ids = []
for jar in inventory:
    date_made = jar['fields'].get('Date Made', '0')
    who = jar['fields']['Initials']
    if date_made > '2021-10-12' and date_made < '2021-10-15' and who in ['TB', 'JD']:
        jar_ids.append(jar['id'])
        
# Create all the slots and slot pairs
slots = [''.join(x) for x in product(letters, numbers)]
slot_pairs = list(combinations(slots, 2))
assert len(slots) == len(jar_ids)

# Create the trial docket
np.random.seed(0)
n_replicates = {'rank': 2,
                'rate': 5}
trials = {'rank': [],
          'rate': []}
for rep in range(1, n_replicates['rank']+1):
    trials['rank'] += [(a, b, rep) for (a, b) in np.random.permutation(slot_pairs)]
assert len(trials['rank']) == n_replicates['rank'] * len(slot_pairs)
for rep in range(1, n_replicates['rate']+1):
    trials['rate'] += [(a, rep) for a in np.random.permutation(slots)]

# Load current user progress
n_trials = {x: len(trials[x]) for x in ('rank', 'rate')}
n_trials_completed = {x: {} for x in ('rank', 'rate')}
df = io.read_results()
for experimenter in experimenters:
    for question in n_replicates:
        try:
            n = df[(df['Experimenter']==experimenter) & (df['Question']==question)].shape[0]
        except KeyError:
            n = 0
        n_trials_completed[question][experimenter] = n

# Load the current slot map
slot_map = io.read_slotmap()

# Initialize the start time
q_start_time = datetime.now()