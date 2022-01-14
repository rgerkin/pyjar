from datetime import datetime
import pandas as pd
from pathlib import Path
import pyairtable as air
import shelve

ROOT_PATH = Path('/srv/jar-experiments')

def get_airtable_key():
    with open('/srv/jar-experiments/atk.txt', 'r') as f:
        x = f.read()
        return str(x).strip('\n')

ATK = get_airtable_key()

DATA_PATH = ROOT_PATH / 'data'
DB_PATH = str(DATA_PATH / 'results.db')
SM_PATH = str(DATA_PATH / 'slotmap.db')


def now_str():
    now = datetime.now()
    return datetime.strftime(now, '%Y-%m-%d %H:%M:%S')

def get_inventory():
    table = air.Table(ATK, 'appJrRwCJcKjbmLwW', 'Jar Inventory')
    return table.all()

def read_results(source='local'):
    if source == 'local':
        with shelve.open(DB_PATH) as f:
            df = pd.DataFrame.from_dict(f, orient='index', dtype='object')
            if df.shape[1]:
                df[['t_start', 't_end']] = df[['t_start', 't_end']].astype('datetime64[ns]')
    else:
        df = None
    return df

def write_result(result, target='local+airtable'):
    assert isinstance(result, (tuple, list))
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], dict)
    key, value = result
    if 'local' in target:
        with shelve.open(DB_PATH) as f:
            f[key] = value
    if 'airtable' in target:
        table = air.Table(ATK, 'appJrRwCJcKjbmLwW', 'Jar Results')
        table.create(value)
        
def read_slotmap(source='local', key=None, reverse=False):
    if source == 'local':
        with shelve.open(SM_PATH) as f:
            if len(f):
                latest_key = max(f.keys())
                slot_map = f[latest_key]
            else:
                slot_map = {}
    if reverse:
        slot_map = {v: k for k, v in slot_map.items()}
    return slot_map

def get_slotmap_seeds():
    with shelve.open(SM_PATH) as f:
        keys = list(f.keys())
    return [int(key.split(' ')[-1]) for key in keys]

def write_slotmap(slot_map, source='local', key=None):
    if key is None:
        key = now_str()
    if source == 'local':
        with shelve.open(SM_PATH) as f:
            f[key] = slot_map
    table = air.Table(ATK, 'appJrRwCJcKjbmLwW', 'Jar Slots')
    table.batch_delete([rec['id'] for rec in table.all()])
    for jar_id, slot in slot_map.items():
        table.create({"Slot": slot,
                      "Jar": [jar_id]})
    return slot_map

def barcode_to_jar_id(inventory, barcode):
    try:
        barcode = int(barcode)
        matches = [x for x in inventory if x['fields'].get('Barcode #', 0)==barcode]
        jar_id = matches[0]['id']
    except:
        jar_id = ''
    return jar_id

def get_jar_by_record(record, inventory):
    jars = [x for x in inventory if x['id']==record]
    assert len(jars)==1
    fields = jars[0]['fields']
    try:
        cid = fields["CID (from Chemical Stock)"][0]
        concentration = fields['Concentration']
    except:
        cid = 0
        concentration = 'Solvent'
    return cid, concentration