import sys
import json, ast
from flask import Flask, url_for, request, render_template, jsonify
import mysql.connector
from const import *

app = Flask(__name__)

db = mysql.connector.connect(
	host=DB_HOST,
	user=DB_USER,
	password=DB_PASS,
	database=DB_NAME
)

data = None

# @app.route('/', methods=['GET', 'POST'])
# def home():
# 	return render_template("home.html")

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/', methods=['GET', 'POST'])
def inventory():
	return render_template("inventory.html")


@app.route('/process_file', methods=['GET', 'POST'])
def process_file():
	strFiledata = request.form['file_data']

	# remove trailing commas
	objEval = ast.literal_eval(strFiledata)
	strJson = json.dumps(objEval)
	objJson = json.loads(strJson)

	ldInventory, lIds = transposeData(objJson)
	ldDbItems = requestAllItems(lIds)

	full_list = []
	for dictInvItem in ldInventory:
		item_id = dictInvItem['int_id']
		bag = dictInvItem['bag']
		qty = dictInvItem['qty']

		row = next((i for i in ldDbItems if i["int_id"] == int(item_id)), False)

		if row:
			# d = {
			# 	"Char": "TBD",
			# 	"Bag": bag,
			# 	"Qty": qty,
			# 	"Id": item_id,
			# 	"Item": row['en_name'],
			# 	"Ja": row['jp_name'],
			# 	"Description": row['en_description'],
			# 	"Jal": row['jp_description'],
			# 	"Category": row['type'],
			# 	"Flags": row['flags'],
			# 	"Stack": row['stack_size'],
			# 	"Level": row['level'],
			# 	"iLvl": row['item_level'],
			# 	"SuLvl": row['superior_level'],
			# 	"Damage": row['damage'],
			# 	"Delay": row['delay'],
			# 	"Skill": row['skill'],
			# 	"Targets": row['valid-targets'],
			# 	"Type": row['type'],
			# 	"Cast Time": row['casting_time'],
			# 	"Jobs": row['jobs'],
			# 	"Races": row['races'],
			# 	"Slots": row['slots'],
			# 	"Cast Delay": row['use_delay'],
			# 	"Recast Delay": row['reuse_delay'],
			# 	"Charges": row['max_charges'],
			# 	"Shield": row['shield_size'],
			# 	"JobText": row['job_strs']
			# }
			d = [
				"TBD",
				bag,
				qty,
				item_id,
				row['en_name'],
				row['jp_name'],
				row['en_description'],
				row['jp_description'],
				row['type'],
				row['flags'],
				row['stack_size'],
				row['level'],
				row['item_level'],
				row['superior_level'],
				row['damage'],
				row['delay'],
				row['skill'],
				row['valid-targets'],
				row['type'],
				row['casting_time'],
				row['jobs'],
				row['races'],
				row['slots'],
				row['use_delay'],
				row['reuse_delay'],
				row['max_charges'],
				row['shield_size'],
				row['job_strs']
			]

			full_list.append(d)

	data_dict = dict()
	data_dict['data'] = full_list
	# data = json.dumps(fill_dict)
	# data = full_list
	return data_dict


def transposeData(userdata):
	""" Convert the dict of storages to a list of dicts of item ids.
	"""
	all_items = []
	all_ids = []
	for bag, val in userdata.items():
		if bag == 'gil':
			pass
		else:
			for id, qty in val.items():
				all_items.append({'int_id': id,'bag': bag, 'qty': qty})
				all_ids.append(id)

	return all_items, list(set(all_ids))


def requestAllItems(ids):
	all_ids = ', '.join(ids)
	cur = db.cursor(dictionary=True)
	query = "SELECT * FROM ffxiah WHERE int_id IN (%s)" % all_ids
	cur.execute(query)

	ret = cur.fetchall()
	return ret

if __name__ == "__main__":
    app.run(debug=True)
