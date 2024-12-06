import os
import argparse
import mysql.connector
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(description='Create and populate ffxiah table')
parser.add_argument("-f", "--file")
args = parser.parse_args()

if args.file is None:
    print("ERROR: Must supply a database file from ffxiah.")
    exit()
else:
    if os.path.exists(args.file):
        print(f"Using database file located at {args.file}")
    else:
        print(f"ERROR: Database file {args.file} does not exist in the given path.")
        exit()

# Open FFXIAH xml file
with open(args.file, 'r', encoding='utf8') as f:
    data = f.read()
bs_data = BeautifulSoup(data, 'lxml')

cols = ['int_id', 'flags', 'stack_size', 'type', 'resource_id', 'valid-targets',
        'en_name', 'jp_name', 'fr_name', 'de_name', 'en_description', 'jp_description',
        'fr_description', 'de_description',
        'level', 'slots', 'races', 'jobs', 'shield_size', 'max_charges', 'casting_time',
        'use_delay', 'reuse_delay', 'element', 'storage-slots', 'damage', 'delay', 'dps',
        'skill', 'jug_size', 'puppet_slot', 'element_charge', 'rare', 'ex', 'relic',
        'notes', 'item_level', 'superior_level']

sCols = ['en_name', 'jp_name', 'fr_name', 'de_name', 'en_description', 'jp_description',
        'fr_description', 'de_description', 'notes']
iCols = ['int_id', 'flags', 'stack_size', 'type', 'resource_id', 'valid-targets',
        'level', 'slots', 'races', 'jobs', 'shield_size', 'max_charges', 'casting_time',
        'use_delay', 'reuse_delay', 'element', 'storage-slots', 'damage', 'delay', 'dps',
        'skill', 'jug_size', 'puppet_slot', 'element_charge', 'relic', 'item_level',
        'superior_level']
bCols = ['rare', 'ex']

# Get max string lengths
sCols_lens = {}
for col in sCols:
    sCols_lens[col + "_len"] = 0

for item in bs_data.find_all('item'):
    for col in sCols:
        val = item.find(col).text
        if len(val) > sCols_lens[col + "_len"]:
            sCols_lens[col + "_len"] = len(val)

tables = f"""
CREATE TABLE ffxiah (
    int_id INT PRIMARY KEY,
    flags INT,
    stack_size INT,
    type INT,
    resource_id INT,
    `valid-targets` INT,
    en_name VARCHAR({sCols_lens['en_name_len']}),
    jp_name VARCHAR({sCols_lens['jp_name_len']}),
    fr_name VARCHAR({sCols_lens['fr_name_len']}),
    de_name VARCHAR({sCols_lens['de_name_len']}),
    en_description VARCHAR({sCols_lens['en_description_len']}),
    jp_description VARCHAR({sCols_lens['jp_description_len']}),
    fr_description VARCHAR({sCols_lens['fr_description_len']}),
    de_description VARCHAR({sCols_lens['de_description_len']}),
    level INT,
    slots INT,
    races INT,
    jobs INT,
    shield_size INT,
    max_charges INT,
    casting_time INT,
    use_delay INT,
    reuse_delay INT,
    element INT,
    `storage-slots` INT,
    damage INT,
    delay INT,
    dps INT,
    skill INT,
    jug_size INT,
    puppet_slot INT,
    element_charge INT,
    rare BOOL,
    ex BOOL,
    relic INT,
    notes VARCHAR({sCols_lens['notes_len']}),
    item_level INT,
    superior_level INT,
    job_strs VARCHAR(90)
)
"""


mydb = mysql.connector.connect(
)

cur = mydb.cursor()
cur.execute("DROP TABLE IF EXISTS ffxiah")
cur.execute(tables)

total = len(bs_data.find_all('item'))
for n, item in enumerate(bs_data.find_all('item')):
    print(f'Processing {n} of {total}.')
    names = []
    vals = []
    for col in cols:
        if '-' in col:
            names.append("`" + col + "`")
        else:
            names.append(col)

        sVal = item.find(col).text
        if sVal is None or sVal == '':
            sVal = None
        vals.append(sVal)

    name_str = ','.join(names)
    val_placeholders = ', '.join('s' * len(vals))
    val_placeholders = val_placeholders.replace('s', '%s')

    # Add a custom column for job strings
    name_str = name_str + ", job_strs"
    val_placeholders = val_placeholders + ', %s'

    ordered_set = ["RUN", "GEO", "SCH",
                    "DNC", "PUP", "COR", "BLU",
                    "SMN", "DRG", "NIN", "SAM",
                    "RNG", "BRD", "BST", "DRK",
                    "PLD", "THF", "RDM", "BLM",
                    "WHM", "MNK", "WAR", "0"]
    job_str_list = list(dict.fromkeys(ordered_set))
    job_int=int(item.find('jobs').text)

    # convert int to binary and size to 23 digits
    binary_string = f'{job_int:08b}'
    to_add = 23 - len(binary_string)
    binary_string = to_add * '0' + binary_string

    found_str_list = list()
    for a, b in zip(binary_string, job_str_list):
        if a == '1':
            found_str_list.append(b)

    if len(found_str_list) > 0:
        found_str_list.reverse()
        job_str = ','.join(found_str_list)
    else:
        job_str = '0'

    vals.append(job_str)

    tVals = tuple(vals)
    query = f"INSERT INTO ffxiah({name_str}) VALUES(%s)" % val_placeholders
    cur.execute(query, tVals)


cur.close()
mydb.commit()
mydb.close()
