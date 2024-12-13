from datetime import datetime as dt
from datetime import timedelta as td
import json, ast
from flask import Flask, request, render_template
import mysql.connector
from const import *
import random, string
import urllib.parse

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = b'$a24%C&$NsPzoMqCR'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024


@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template("home.html")

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/', methods=['GET', 'POST'])
def inventory():
	name = request.args.get('name')
	passkey = request.args.get('passkey')
	if name is not None and passkey is not None:
		return render_template("inventory.html", urlName=name, urlPasskey=passkey)
	else:
		return render_template("inventory.html")
[(' {"file_data": "inventory data goes here", "name":"NAME", "passkey": "None"} ', '')]

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
	app.logger.warning(request.__dict__)

	if request.method == "POST":
		app.logger.warning('Starting POST request')
		app.logger.warning(f"len(request.form) = {len(request.form)}")
		sName = None
		sPasskey = None
		sFiledata = None

		if (len(request.form) == 1):
			# app.logger.warning(request.form)
			sRequestForm = next(iter(request.form))
			evaled = json.loads(sRequestForm)

			sName = evaled['name']
			sPasskey = evaled['passkey']
			objJson = evaled['file_data']
		else:
			sFiledata = request.form['file_data']
			# If the file was manually uploaded, then we need to reformat it here.
			sFiledata = sFiledata.replace("return ", "")
			sFiledata = sFiledata.replace("[", "")
			sFiledata = sFiledata.replace("]", "")
			sFiledata = sFiledata.replace("=", ":")
			sFiledata = sFiledata.replace("key items", "keyitems")
			# remove trailing commas
			objFileData = ast.literal_eval(sFiledata)
			strJson = json.dumps(objFileData)
			
			sName = request.form['name']
			sPasskey = request.form['passkey']
			objJson = json.loads(strJson)

	if sPasskey is not None:
		if len(sPasskey) < 1:
			sPasskey = None

	app.logger.warning('Got args, moving on')

	ldInventory, lIds = transposeData(objJson)
	error, ldDbItems = selectAllItems(lIds)

	full_list = []
	for dictInvItem in ldInventory:
		item_id = dictInvItem['int_id']
		bag = dictInvItem['bag']
		qty = dictInvItem['qty']

		row = next((i for i in ldDbItems if i["int_id"] == int(item_id)), False)

		if row:
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
	data = json.dumps(data_dict)

	keyerror, unique_key = upsertInventoryTableReturnPasskey(data, sName, sPasskey)

	# app.logger.debug('unique_key :', unique_key)
	app.logger.warning(f'unique_key : {unique_key}')
	if error or keyerror:
		return {'error': 'See Error Log'}
	else:
		return unique_key


@app.route('/request_existing', methods=['POST'])
def request_existing(urlName = None, urlPasskey=None):
	if request.method == 'POST':
		name = request.form['name']
		passkey = request.form['passkey']
	else:
		name = urlName
		passkey = urlPasskey
	app.logger.debug(f'requesting [{name}, {passkey}]')
	error, ldTable = selectInventoryTableWithPasskey(name, passkey)
	if error:
		return {'error': f'No inventory found for {name} and {passkey}'}
	app.logger.warning(ldTable)
	# app.logger.warning(type(ldTable))
	if "json_data" not in ldTable[0]:
		app.logger.warning(f'No values returned for [name={name}, passkey={passkey}]')
		return {'error': f'No inventory found for {name} and {passkey}'}
	elif error:
		return {'error': 'See Error Log'}

	dTable = dict(ldTable[0])
	expiration_time = dTable['expire_time']
	inv_data = json.loads(dTable['json_data'])
	# app.logger.warning(inv_data)

	dPackage = dict()
	dPackage['name'] = name
	dPackage['passkey'] = passkey
	dPackage['data'] = inv_data['data']
	dPackage['expires'] = expiration_time

	return dPackage


@app.route('/process_file', methods=['GET', 'POST'])
def process_file():
	strFiledata = request.form['file_data']

	# remove trailing commas
	objEval = ast.literal_eval(strFiledata)
	strJson = json.dumps(objEval)
	objJson = json.loads(strJson)

	ldInventory, lIds = transposeData(objJson)
	error, ldDbItems = selectAllItems(lIds)

	full_list = []
	for dictInvItem in ldInventory:
		item_id = dictInvItem['int_id']
		bag = dictInvItem['bag']
		qty = dictInvItem['qty']

		row = next((i for i in ldDbItems if i["int_id"] == int(item_id)), False)

		if row:
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

	if error:
		return {'error': 'See Error Log'}
	else:
		return data_dict


def transposeData(bagsIds):
	""" Convert the dict of storages to a list of dicts of item ids.
	"""
	all_items = []
	all_ids = []
	for bag, val in bagsIds.items():
		# app.logger.warning(f'bag, val = {bag}, {val}')
		if bag == 'gil':
			pass
		else:
			for id, qty in val.items():
				all_items.append({'int_id': id,'bag': bag, 'qty': qty})
				all_ids.append(id)

	return all_items, list(set(all_ids))


# Database Queries
def selectAllItems(ids):
	all_ids = ', '.join(ids)
	error = False
	
	conn = mysql.connector.connect(
		host=DB_HOST,
		user=DB_USER,
		password=DB_PASS,
		database=DB_NAME
	)
	cur = conn.cursor(dictionary=True)

	ret = None
	try:
		query = "SELECT * FROM ffxiah WHERE int_id IN (%s)" % all_ids
		cur.execute(query)

		ret = cur.fetchall()
		conn.commit()
	except mysql.connector.Error as E:
		app.logger.error(f'selectAllItems: mysql.connector.Error = {E}')
		error = True

	cur.close()
	conn.close()
	return error, ret


def upsertInventoryTableReturnPasskey(json, name, passkey=None):
	error = False
	conn = mysql.connector.connect(
		host=DB_HOST,
		user=DB_USER,
		password=DB_PASS,
		database=DB_NAME
	)
	cur = conn.cursor(dictionary=True)

	created_time = dt.now()
	expire_time = created_time + td(days=1)

	if passkey is None:
		while True:
			rand = ''.join(random.choice(string.ascii_letters) for i in range(8))
			app.logger.error(f'upsertInventoryTableReturnPasskey: rand = {rand}')

			try:
				cur.execute("SELECT passkey FROM inventories")
				ret = cur.fetchall()

				if rand not in ret:
					passkey = rand
					break
			except mysql.connector.Error as E:
				app.logger.error('upsertInventoryTableReturnPasskey: mysql.connector.Error = ', E)
				error = True
				break
	app.logger.error(f'upsertInventoryTableReturnPasskey: passkey = {passkey}')
	ret = None
	try:
		add_data = ("""
			  INSERT INTO inventories (name, passkey, json_data, created_time, expire_time)
			  VALUES(%s, %s, %s, %s, %s)
			  ON DUPLICATE KEY UPDATE json_data = VALUES(json_data), expire_time = VALUES(expire_time)
			  """)
		add_values = (name, passkey, json, created_time, expire_time)
		cur.execute(add_data, add_values)

		lastrow = (cur.lastrowid)
		retrieve = "SELECT passkey, name FROM inventories WHERE id = (%s)" % lastrow
		cur.execute(retrieve)

		ret = cur.fetchall()
		ret = ret[0]
		# app.logger.debug(ret)

		conn.commit()
	except mysql.connector.Error as E:
		app.logger.error(f'upsertInventoryTableReturnPasskey: mysql.connector.Error = {E}')
		error = True

	cur.close()
	conn.close()

	return error, ret


def selectInventoryTableWithPasskey(name, passkey):
	error = False
	conn = mysql.connector.connect(
		host=DB_HOST,
		user=DB_USER,
		password=DB_PASS,
		database=DB_NAME
	)
	cur = conn.cursor(dictionary=True)

	ret = 'Error'
	try:
		query = ("SELECT * FROM inventories WHERE name = %s AND passkey = %s")
		cur.execute(query, (name, passkey))

		ret = cur.fetchall()
		# app.logger.debug(ret)
		if not cur.rowcount:
			ret = {'name':'error', 'passkey':'error'}
			error = True

		conn.commit()
	except mysql.connector.Error as E:
		app.logger.error(f'selectInventoryTableWithPasskey: mysql.connector.Error = {E}')
		error = True

	cur.close()
	conn.close()

	return error, ret


# def makeKey():
	
# 	error = False
# 	key = None
# 	while True:
# 		rand = ''.join(random.choice(string.ascii_letters) for i in range(8))

# 		conn = mysql.connector.connect(
# 			host=DB_HOST,
# 			user=DB_USER,
# 			password=DB_PASS,
# 			database=DB_NAME
# 		)
# 		cur = conn.cursor(dictionary=True)
# 		try:
# 			cur.execute("SELECT passkey FROM inventories")
# 			ret = cur.fetchall()
# 			cur.close()
# 			conn.close()

# 			if rand not in ret:
# 				key = rand
# 				break
# 		except mysql.connector.Error as E:
# 			app.logger.error('makeKey: mysql.connector.Error = ', E)
# 			error = True
# 			break

# 	return error, key



if __name__ == "__main__":
    app.run(debug=True)
