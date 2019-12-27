import sys, os, csv, hashlib, shutil
from ast import literal_eval

class db:

	def __init__(self):
		self.logged_in = False
		self.logged_DB = None
		if sys.platform.lower().startswith("linux") or sys.platform.lower().startswith("darwin"):
			os.chdir("/usr/local/")
			if os.path.exists("NHX"):
				os.chdir("NHX")
			else:
				os.mkdir("NHX")
				os.chdir("NHX")
		elif sys.platform.lower().startswith("win32"): 
			os.chdir("C:\\ProgramData")
			if os.path.exists("NHX"):
				os.chdir("NHX")
			else:
				os.mkdir("NHX")
				os.chdir("NHX")
		self.cwd = os.getcwd()


	def returner(self, code):
		os.chdir(self.cwd)
		return code


	def validator(self, db_properties, no_cred=False, others=[]):
		self.db_properties = db_properties
		if type(db_properties) != dict:
			# Returns status code 300 = Invalid Entry
			return self.returner(300)
		if others != []:
			incomplete = False
			for item in others:
				if item not in db_properties:
					incomplete = True
			if incomplete:
				return self.returner(302)
		if "name" in db_properties and "username" in db_properties and "password" in db_properties and no_cred == False:
			self.database_name = self.db_properties["name"].lower()
			self.database_usr = self.db_properties["username"]
			self.database_pass = self.db_properties["password"]
		elif no_cred == True and "name" in db_properties:
			self.database_name = self.db_properties["name"]
		else:
			# Returns status code 302 = Incomplete
			return self.returner(302)
		return self.returner(200)


	def valitable(self, table_fields):
		primaryy = False
		field_names = []
		for field in table_fields:
			if type(field) == str:
				field = literal_eval(field)
			if "name" not in field or "type" not in field: 
				return self.returner(302)
			if "ai" in field and field["ai"] == True and field["type"].lower() != "int":
				# Returns status code 501 = Cannot increment other type than int
				return self.returner(501)
			if "attribute" in field and field["attribute"] != None and field["attribute"].lower() == "primary" and primaryy == False:
				primaryy = True
			elif "attribute" in field and field["attribute"] != None and field["attribute"].lower() == "primary" and primaryy == True:
				# Returns status code 502 = Cannot have more than 1 Primary
				return self.returner(502)
			if "null" in field and field["null"] == True and "attribute" in field and (field["attribute"].lower() == "primary" or field["attribute"].lower() == "index"):
				# Returns status code 503 = Primary or Index field cannot be Null
				return self.returner(503)
			if "default" in field and field["default"] == "null" and "null" in field and (field["null"] == False or field["null"] == ""):
				# Returns status code 504 = Default cannot be Null if the field cannot be null
				return self.returner(504)
			if "length" in field and type(field["length"]) == int and (((field["type"].lower() == "int" and field["length"] > 255) or (field["type"].lower() == "str" and field["length"] > 16384))):
				# Returns status code 507 = Cannot have length more than 255 for int and more than 16384 for str
				return self.returner(507)
			if "attribute" in field and field["type"].lower() == "bool":
				# Returns status code 508 = Cannot have bool type in an attributed field
				return self.returner(508)
			if "attribute" in field and field["attribute"] != None and field["attribute"].lower() != "primary" and field["attribute"].lower() != "index" and field["attribute"].lower() != "unique":
				# Returns status code 505 = Attribute cannot be other than Primary, Index or Unique
				return self.returner(505)
			if field["name"].lower() in field_names:
				# Returns status code 506 = Cannot create two fields with same name
				return self.returner(506)
			else:
				field_names.append(field["name"].lower())
		return self.returner(200)


	def create(self, db_properties):
		status_code = self.validator(db_properties)
		dir_exists = os.path.exists("./NHX_DB_Dat/")
		if dir_exists:
			os.chdir("./NHX_DB_Dat")
		else:
			os.mkdir("./NHX_DB_Dat")
			os.chdir("./NHX_DB_Dat")
		if status_code != 200:
			return self.returner(status_code)
		if os.path.exists(self.database_name) and os.path.isfile(self.database_name + "/config.NHX"):
			# Returns status code 301 = Already Exists
			return self.returner(301)
		else:
			os.mkdir(self.database_name)
			os.chdir(self.database_name)
			with open("config.NHX", "w") as handler:
				encoded = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
				pass_encoded = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
				handler.write(self.database_name + "|" + str(encoded) + "|" + str(pass_encoded))
				# Returns status code 200 = Success
				return self.returner(200)


	def login(self, db_properties):
		self.status_code = self.validator(db_properties)
		if self.status_code != 200:
			return self.returner(self.status_code)
		# Verification Starts
		if os.path.isfile("./NHX_DB_Dat/" + self.database_name + "/config.NHX") == False and os.path.exists("./NHX_DB_Dat/" + self.database_name + "/tables/") == False:
			# Returns status code 404 = Not found
			self.status_code = 404
			return self.returner(404)
		with open("./NHX_DB_Dat/" + self.database_name + "/config.NHX") as readf:
			self.database_usr = self.database_usr
			self.database_pass = self.database_pass
			content = readf.read()
			content = content.split("|")
			verification = content[1]
			post_verification = content[2]
			verified = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
			post_verified = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
			if verification == verified and post_verification == post_verified:
				self.logged_in = True
				self.logged_DB = self.database_name
				self.status_code = 200
				return self.returner(200)
			else:
				# Returns status code 303 = Credentials error
				self.status_code = 303
				return self.returner(303)


	def drop(self):
		if self.logged_in != True:
			return self.returner(304)
		os.chdir("./NHX_DB_Dat/")
		shutil.rmtree(self.database_name)
		return self.returner(200)


	def backup(self, path):
		if self.logged_in != True:
			return self.returner(304)
		shutil.make_archive("./NHX_DB_Dat/cache" + self.database_name, "zip", "./NHX_DB_Dat/"+ self.database_name)
		file = open("./NHX_DB_Dat/cache" + self.database_name + ".zip", "r+b")
		data = file.read()
		file.close()
		to_write = data[2:] + 64*b"\x4e\x48\x58"
		file = open(path + self.database_name + ".NHX", "w+b")
		file.write(to_write)
		file.close()
		os.remove("./NHX_DB_Dat/cache" + self.database_name + ".zip")
		return self.returner(200)


	def restore(self, db_properties):
		status_code = self.validator(db_properties, others=["file"])
		if status_code != 200:
			return self.returner(status_code)
		dir_exists = os.path.exists("./NHX_DB_Dat/")
		if dir_exists:
			os.chdir("./NHX_DB_Dat")
		else:
			os.mkdir("./NHX_DB_Dat")
			os.chdir("./NHX_DB_Dat")
		if os.path.isfile(db_properties["file"]) != True:
			return self.returner(404)
		file = open(db_properties["file"], "r+b")
		data = file.read()
		file.close()
		to_restore = b"PK" + data[:-192]
		file = open("./cache.NHX", "w+b")
		file.write(to_restore)
		file.close()
		os.mkdir("./cache.?.?.?NHX")
		shutil.unpack_archive("cache.NHX", "./cache.?.?.?NHX/", "zip")
		file = open("./cache.?.?.?NHX/config.NHX", "r")
		content = file.read()
		file.close()
		content = content.split("|")
		name = content[0]
		os.remove("cache.NHX")
		verification = content[1]
		post_verification = content[2]
		verified = hashlib.sha256(self.database_usr.encode("utf-8") + self.database_pass.encode("utf-8")).hexdigest()
		post_verified = hashlib.sha256(self.database_pass.encode("utf-8")).hexdigest()
		if verification == verified and post_verification == post_verified:
			os.rename("./cache.?.?.?NHX", name)
			self.status_code = 200
			return self.returner(200)
		else:
			shutil.rmtree("./cache.?.?.?NHX")
			self.status_code = 303
			return self.returner(303)


	def create_table(self, structure, override=False):
		if self.logged_in != True:
			return self.returner(304)
		if type(structure) != dict and type(structure["fields"]) != list:
			return self.returner(300)
		no_field = len(structure["fields"])
		table_name = structure["name"].lower()
		os.chdir("./NHX_DB_Dat")
		if os.path.exists("./" + self.database_name + "/tables/") == False:
			os.mkdir("./" + self.database_name + "/tables/")
		os.chdir("./" + self.database_name + "/tables/")
		if os.path.exists("./" + table_name) and os.path.isfile("./" + table_name + "/config.NHX"):
			return self.returner(301)
		if os.path.exists("./" + table_name) == False:
			os.mkdir(table_name)
		os.chdir(table_name)
		status_code = self.valitable(structure["fields"])
		if status_code != 200:
			return self.returner(status_code)
		os.chdir("./NHX_DB_Dat/" + self.database_name + "/tables/" + table_name)
		to_write = []
		to_write_index = []
		to_write_data = []
		for field in structure["fields"]:
			buff = {"name": field["name"].lower(), "type": field["type"]}
			if "length" in field and type(field["length"]) == int and ((field["type"].lower() == "int" and field["length"] < 256) or field["type"].lower() == "str" and field["length"] < 16385):
				buff.update({"length": field["length"]})
			elif field["type"].lower() == "int":
				buff.update({"length": 255})
			elif field["type"].lower() == "float":
				buff.update({"length": 255})
			elif field["type"].lower() == "bool":
				buff.update({"length": 5})
			else:
				buff.update({"length": 16384})
			if "ai" in field and field["ai"] == True:
				buff.update({"ai": True})
			else:
				buff.update({"ai": False})
			if "null" in field and field["null"] == True:
				buff.update({"null": True})
			else:
				buff.update({"null": False})
			if "default" in field and ("ai" not in field or field["ai"] != True) and (type(field["default"]) != bool):
				buff.update({"default": field["default"]})
			else:
				buff.update({"default": None})
			if "attribute" in field and field["attribute"] != None and (field["attribute"].lower() == "unique" or field["attribute"].lower() == "index" or field["attribute"].lower() == "primary"):
				buff.update({"attribute": field["attribute"].lower()})
			else:
				buff.update({"attribute": None})
			if "attribute" in field and field["attribute"] != None and (field["attribute"].lower() == "unique" or field["attribute"].lower() == "index" or field["attribute"].lower() == "primary"):
				to_write_index.append(buff["name"].lower())
			else:
				to_write_data.append(buff["name"].lower())
			to_write.append(buff)
		with open("config.NHX", "w+", newline='') as file:
			writer = csv.writer(file, delimiter="|")
			writer.writerow(to_write)
		if (os.path.isfile("nindex.NHX") == True or os.path.isfile("index.NHX")) and override == False:
			# Returns status code 500 = Data file for the current table exists
			return self.returner(500)
		with open("index.NHX", "w+", newline='') as file:
			pass
		if os.path.isfile("nindex.NHX") == True and override == False:
			# Returns status code 500 = Data file for the current table exists
			return self.returner(500)
		with open("nindex.NHX", "w+", newline='') as file:
			pass
		return self.returner(200)


	def drop_table(self, table_name):
		if self.logged_in != True:
			return self.returner(304)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/")
		if os.path.exists(table_name) != True:
			return self.returner(404)
		shutil.rmtree(table_name)
		return self.returner(200)


	def truncate_table(self, table_name):
		if self.logged_in != True:
			return self.returner(304)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/")
		if os.path.exists(table_name) != True:
			return self.returner(404)
		os.chdir(table_name)
		head = []
		with open("nindex.NHX", "w") as file:
			pass
		with open("index.NHX", "w") as file:
			pass
		return self.returner(200)
	

	def alter_table(self, values):
		if self.logged_in != True:
			return self.returner(304)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/")
		if os.path.exists(values["table_name"]) != True:
			return self.returner(404)
		os.chdir(values["table_name"])
		if values["operation"].lower() == "add":
			cfields = []
			with open("config.NHX", "r+") as file:
				reader = csv.reader(file, delimiter="|")
				for index, row in enumerate(reader):
					if index == 0:
						cfields = row
						break
			table_fields = cfields + values["fields"]
			status_code = self.valitable(table_fields)
			if status_code != 200:
				return self.returner(status_code)
			os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + values["table_name"])
			to_write = []
			for field in table_fields:
				if type(field) == str:
					field = literal_eval(field)
				buff = {"name": field["name"].lower(), "type": field["type"]}
				if "length" in field and type(field["length"]) == int and ((field["type"] == int and field["length"] < 256) or field["type"] == str and field["length"] < 16385):
					buff.update({"length": field["length"]})
				elif field["type"].lower() == "int":
					buff.update({"length": 255})
				elif field["type"].lower() == "float":
					buff.update({"length": 255})
				elif field["type"].lower() == "bool":
					buff.update({"length": 5})
				else:
					buff.update({"length": 16384})
				if "ai" in field and field["ai"] == True:
					buff.update({"ai": True})
				else:
					buff.update({"ai": False})
				if "null" in field and field["null"] == True:
					buff.update({"null": True})
				else:
					buff.update({"null": False})
				if "default" in field and (type(field["default"]) != bool):
					buff.update({"default": field["default"]})
				else:
					buff.update({"default": None})
				if "attribute" in field:
					buff.update({"attribute": field["attribute"]})
				else:
					buff.update({"attribute": None})
				to_write.append(buff)
			with open("config.NHX", "w+", newline='') as file:
				writer = csv.writer(file, delimiter="|")
				writer.writerow(to_write)
		if values["operation"].lower() == "drop":
			to_drop = values["fields"]
			fields = []
			to_update = []
			with open("config.NHX", "r+", newline="") as file:
				reader = csv.reader(file, delimiter="|")
				for index, row in enumerate(reader):
					if index == 0:
						fields = row
			for field in fields:
				field = literal_eval(field)
				if field["name"] in to_drop:
					pass
				else:
					to_update.append(field)
			with open("config.NHX", "w+", newline='') as file:
				writer = csv.writer(file, delimiter='|')
				writer.writerow(to_update)
		return self.returner(200)


	def insert_data(self, table_name, values):
		if self.logged_in != True:
			return self.returner(304)
		field_names_nindex = []
		field_names_index = []
		fields = []
		if os.path.exists("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name) == False:
			return self.returner(404)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name)
		with open("config.NHX", "r+", newline='') as file:
			reader = csv.reader(file, delimiter="|")
			for index, row in enumerate(reader):
				if index == 0:
					fields = row
					break
		nindexread = []
		indexread = []
		for field in fields:
			field = literal_eval(field)
			if field["attribute"] != None:
				indexread.append(field["name"])
			else:
				nindexread.append(field["name"])
		indexvalues = {}
		nindexvalues = {}
		for field in fields:
			field = literal_eval(field)
			if field["ai"] != True:
				if (field["name"] not in values and field["null"] != True) or (values[field["name"]] == "" or values[field["name"]] == None):
					# Returns status code 600 = Values for a non Null field is not specified
					return self.returner(600)
				if (field["type"].lower() == "int" and type(values[field["name"]]) != int) or (field["type"] == "float" and type(values[field["name"]]) != float) or (field["type"] == "str" and type(values[field["name"]]) != str) or ((field["type"] == "bool" and type(values[field["name"]]) != bool)):
					# Returns status code 601 = Values provided do not match their types
					return self.returner(601)
				if len(str(values[field["name"]])) > field["length"]:
					# Returns status code 602 = Values provided are longer than the size allocated
					return self.returner(602)
			else:
				pass
			if field["name"] in values:
				if field["attribute"] != None:
					indexvalues.update({field["name"]: values[field["name"]]})
					if field["attribute"].lower() == "unique" or field["attribute"].lower() == "primary":
						file = open("index.NHX", "r+", newline='')
						reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
						flagged = False
						for row in reader:
							if str(values[field["name"]]) == str(row[field["name"]]):
								flagged = True
								break
						if flagged:
							# Returns status code 603 = Unique and Primary values can not have previous values
							return self.returner(603)
				else:
					nindexvalues.update({field["name"]: values[field["name"]]})
			else:
				if field["attribute"] != None and field["ai"] != True:
					indexvalues.update({field["name"]: ""})
				if field["attribute"] == None and field["ai"] != True:
					nindexvalues.update({field["name"]: ""})
				if field["attribute"] != None and field["ai"] == True:
					if os.path.getsize("index.NHX") != 0:
						with open("index.NHX", "r+") as file:
							data = file.read().splitlines()[-1]
						data = data.split("|")
						index_no = indexread.index(field["name"])
						required = int(data[index_no]) + 1
						indexvalues.update({field["name"]: required})
					else:
						indexvalues.update({field["name"]: 0})
				if field["attribute"] == None and field["ai"] == True:
					if os.path.getsize("nindex.NHX") != 0:
						with open("nindex.NHX", "r+") as file:
							data = file.read().splitlines()[-1]
						data = data.split("|")
						index_no = nindexread.index(field["name"])
						required = int(data[index_no]) + 1
						nindexvalues.update({field["name"]: required})
					else:
						nindexvalues.update({field["name"]: 0})
				if field["attribute"] == "primary" or field["attribute"] == "index":
					# Returns status code 604 = Primary and Index fields cannot contain be empty
					return self.returner(604)
		indexed = open("index.NHX", "a+", newline="")
		nindexed = open("nindex.NHX", "a+", newline="")
		indexwrite = csv.DictWriter(indexed, delimiter="|", fieldnames=indexread)
		nindexwrite = csv.DictWriter(nindexed, delimiter="|", fieldnames=nindexread)
		nindexwrite.writerow(nindexvalues)
		indexwrite.writerow(indexvalues)
		nindexed.close()
		indexed.close()
		return self.returner(200)


	def update_data(self, table_name, values):
		if self.logged_in != True:
			return self.returner(304)
		if os.path.exists("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name) == False:
			return self.returner(404)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name)
		fields = []
		with open("config.NHX", "r+", newline='') as file:
			reader = csv.reader(file, delimiter="|")
			for index, row in enumerate(reader):
				if index == 0:
					fields = row
					break
		nindexread = []
		indexread = []
		to_alter = []
		for field_name in values["fields"]:
			to_alter.append(field_name)
		for field in fields:
			field = literal_eval(field)
			if field["attribute"] != None:
				indexread.append(field["name"])
			else:
				nindexread.append(field["name"])
		for field in fields:
			field = literal_eval(field)
			if field["name"] in to_alter:
				if "criteria" not in values or values["criteria"] == "*":
					to_up = []
					if field["attribute"] != None:
						with open("index.NHX", "r+", newline='') as file:
							reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
							for index, row in enumerate(reader):
								row.update({field["name"] : values["fields"][field["name"]]})
								to_up.append(row)
						with open("index.NHX", "w+", newline='') as file:
							writer = csv.DictWriter(file, fieldnames=indexread, delimiter="|")
							for index, row in enumerate(to_up):
								writer.writerow(row)
					else:
						with open("nindex.NHX", "r+", newline='') as file:
							reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
							for index, row in enumerate(reader):
								row.update({field["name"] : values["fields"][field["name"]]})
								to_up.append(row)
						with open("nindex.NHX", "w+", newline='') as file:
							writer = csv.DictWriter(file, fieldnames=nindexread, delimiter="|")
							for index, row in enumerate(to_up):
								writer.writerow(row)
		if "criteria" in values and values["criteria"] != "*":
			splitted = []
			typ = 0
			operand = 1
			left = 2
			right = 3
			operands = []
			if "==" in values["criteria"]:
				splitted = ["all", "=="] + values["criteria"].split("==")
			elif "!=" in values["criteria"]:
				splitted = ["all", "!="] + values["criteria"].split("!=")
			elif ">=" in values["criteria"]:
				splitted = ["if", ">="] + values["criteria"].split(">=")
			elif "<=" in values["criteria"]:
				splitted = ["if", "<="] + values["criteria"].split("<=")
			elif "<" in values["criteria"]:
				splitted = ["if", "<"] + values["criteria"].split("<")
			elif ">" in values["criteria"]:
				splitted = ["if", ">"] + values["criteria"].split(">")
			else:
				# Returns status code 605 = Cannot find a valid criteria
				return self.returner(605)
			for operanda in splitted:
				operands.append(operanda.strip())
			flagged = False
			try:
				int(operands[right])
			except ValueError:
				flagged = True
			if operands[right] == "" or operands[left] == "":
				# Returns status code 609 = Cannot find essential Operands
				return self.returner(609)
			if operands[typ] == "if" and flagged:
				# Returns status code 607 = Cannot have the right operand as non int on int comparisons
				return self.returner(607)
			results = False
			crit = {}
			for fieldaa in fields:
				fieldaa = literal_eval(fieldaa)
				if fieldaa["name"] == operands[left]:
					results = True
					if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
						# Returns status code 606 = Cannot compare with int operands on non int fields
						return self.returner(606)
					else:
						if fieldaa["attribute"] != None:
							crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": True})
						else:
							crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": False})
			if results != True:
				# Returns status code 608 = Expected Left operand as A field Name, none found
				return self.returner(608)
			line_no = []
			if field["attribute"] != None:
				if crit["is_index"]:
					with open("index.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				else:
					with open("nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					# Returns status code 700 = Unknown Internal Error
					return self.returner(700)
			else:
				if crit["is_index"]:
					with open("index.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				else:
					with open("nindex.NHX", "r+", newline='') as file:
						reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
						for index, row in enumerate(reader):
							if crit["type"] == "==":
								if row[crit["name"]] == crit["value"]:
									line_no.append(index)
							elif crit["type"] == "!=":
								if row[crit["name"]] != crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">=":
								if row[crit["name"]] >= crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<=":
								if row[crit["name"]] <= crit["value"]:
									line_no.append(index)
							elif crit["type"] == ">":
								if row[crit["name"]] > crit["value"]:
									line_no.append(index)
							elif crit["type"] == "<":
								if row[crit["name"]] < crit["value"]:
									line_no.append(index)
							else:
								line_no = False
				if line_no == False:
					return self.returner(700)
			for field in values["fields"]:
				nindexlines = []
				indexlines = []
				for fieldx in fields:
					fieldx = literal_eval(fieldx)
					if field == fieldx["name"]:
						if (fieldx["attribute"]!= None and(fieldx["attribute"] == "primary" or fieldx["attribute"] == "index")) and (values["fields"][field] == "" or values["fields"][field] == None):
							return self.returner(604)
						if (fieldx["null"] == False) and (values["fields"][field] == "" or values["fields"][field] == None):
							return self.returner(600)
						if len(str(values["fields"][field])) > fieldx["length"]:
							return self.returner(602)
						if (fieldx["type"].lower() == "int" and type(values["fields"][field]) != int) or (fieldx["type"] == "float" and type(values["fields"][field]) != float) or (fieldx["type"] == "str" and type(values["fields"][field]) != str) or ((fieldx["type"] == "bool" and type(values["fields"][field]) != bool)):
							return self.returner(601)
						break
				if field in indexread:
					with open("index.NHX", "r+", newline="") as file:
						reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
						for row in reader:
							indexlines.append(row)
					for line in line_no:
						indexlines[line].update({field: values["fields"][field]})
					with open("index.NHX", "w+", newline='') as file:
						writer = csv.DictWriter(file, delimiter="|", fieldnames=indexread)
						for line in indexlines:
							writer.writerow(line)
				if field in nindexread:
					with open("nindex.NHX", "r+", newline="") as file:
						reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
						for row in reader:
							nindexlines.append(row)
					for line in line_no:
						nindexlines[line].update({field: values["fields"][field]})
					with open("nindex.NHX", "w+", newline='') as file:
						writer = csv.DictWriter(file, delimiter="|", fieldnames=nindexread)
						for line in nindexlines:
							writer.writerow(line)
		return self.returner(200)


	def delete_data(self, table_name, criteria):
		if self.logged_in != True:
			return self.returner(304)
		if os.path.exists("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name) == False:
			return self.returner(404)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name)
		fields = []
		nindexread = []
		indexread = []
		with open("config.NHX", "r+", newline='') as file:
			reader = csv.reader(file, delimiter="|")
			for index, row in enumerate(reader):
				if index == 0:
					fields = row
					break
		for field in fields:
			field = literal_eval(field)
			if field["attribute"] != None:
				indexread.append(field["name"])
			else:
				nindexread.append(field["name"])
		splitted = []
		typ = 0
		operand = 1
		left = 2
		right = 3
		operands = []
		if "==" in criteria:
			splitted = ["all", "=="] + criteria.split("==")
		elif "!=" in criteria:
			splitted = ["all", "!="] + criteria.split("!=")
		elif ">=" in criteria:
			splitted = ["if", ">="] + criteria.split(">=")
		elif "<=" in criteria:
			splitted = ["if", "<="] + criteria.split("<=")
		elif "<" in criteria:
			splitted = ["if", "<"] + criteria.split("<")
		elif ">" in criteria:
			splitted = ["if", ">"] + criteria.split(">")
		else:
			return self.returner(605)
		for operanda in splitted:
			operands.append(operanda.strip())
		flagged = False
		try:
			int(operands[right])
		except ValueError:
			flagged = True
		if operands[right] == "" or operands[left] == "":
			return self.returner(609)
		if operands[typ] == "if" and flagged:
			return self.returner(607)
		crit = {}
		results = False
		for fieldaa in fields:
			fieldaa = literal_eval(fieldaa)
			if fieldaa["name"] == operands[left]:
				results = True
				if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
					return self.returner(606)
				else:
					if fieldaa["attribute"] != None:
						crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": True})
					else:
						crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": False})
		if results != True:
			return self.returner(608)
		line_no = []
		if field["attribute"] != None:
			if crit["is_index"]:
				with open("index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open("nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				# Returns status code 700 = Unknown Internal Error
				return self.returner(700)
		else:
			if crit["is_index"]:
				with open("index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open("nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				return self.returner(700)
		nindexlines = []
		indexlines = []
		with open("index.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
			for row in reader:
				indexlines.append(row)
		with open("nindex.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
			for row in reader:
				nindexlines.append(row)
		count = 0
		for line in line_no:
			nindexlines.pop(line - count)
			indexlines.pop(line - count)
			count = count + 1
		with open("index.NHX", "w+", newline="") as file:
			writer = csv.DictWriter(file, delimiter="|", fieldnames=indexread)
			for row in indexlines:
				writer.writerow(row)
		with open("nindex.NHX", "w+", newline="") as file:
			writer = csv.DictWriter(file, delimiter="|", fieldnames=nindexread)
			for row in nindexlines:
				writer.writerow(row)
		return self.returner(200)


	def select_data(self, table_name, criteria):
		if self.logged_in != True:
			return self.returner(304)
		if os.path.exists("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name) == False:
			return self.returner(404)
		os.chdir("./NHX_DB_Dat/" + self.logged_DB + "/tables/" + table_name)
		fields = []
		nindexread = []
		indexread = []
		with open("config.NHX", "r+", newline='') as file:
			reader = csv.reader(file, delimiter="|")
			for index, row in enumerate(reader):
				if index == 0:
					fields = row
					break
		for field in fields:
			field = literal_eval(field)
			if field["attribute"] != None:
				indexread.append(field["name"])
			else:
				nindexread.append(field["name"])
		splitted = []
		typ = 0
		operand = 1
		left = 2
		right = 3
		operands = []
		if "==" in criteria:
			splitted = ["all", "=="] + criteria.split("==")
		elif "!=" in criteria:
			splitted = ["all", "!="] + criteria.split("!=")
		elif ">=" in criteria:
			splitted = ["if", ">="] + criteria.split(">=")
		elif "<=" in criteria:
			splitted = ["if", "<="] + criteria.split("<=")
		elif "<" in criteria:
			splitted = ["if", "<"] + criteria.split("<")
		elif ">" in criteria:
			splitted = ["if", ">"] + criteria.split(">")
		else:
			return self.returner(605)
		for operanda in splitted:
			operands.append(operanda.strip())
		flagged = False
		try:
			int(operands[right])
		except ValueError:
			flagged = True
		if operands[right] == "" or operands[left] == "":
			return self.returner(609)
		if operands[typ] == "if" and flagged:
			return self.returner(607)
		crit = {}
		results = False
		for fieldaa in fields:
			fieldaa = literal_eval(fieldaa)
			if fieldaa["name"] == operands[left]:
				results = True
				if (fieldaa["type"] == "str" or fieldaa["type"] == "bool") and operands[typ] == "if":
					return self.returner(606)
				else:
					if fieldaa["attribute"] != None:
						crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": True})
					else:
						crit.update({"name": operands[left], "value": operands[right], "type": operands[operand], "is_index": False})
		if results != True:
			return self.returner(608)
		line_no = []
		if field["attribute"] != None:
			if crit["is_index"]:
				with open("index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open("nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				# Returns status code 700 = Unknown Internal Error
				return self.returner(700)
		else:
			if crit["is_index"]:
				with open("index.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=indexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			else:
				with open("nindex.NHX", "r+", newline='') as file:
					reader = csv.DictReader(file, fieldnames=nindexread, delimiter="|")
					for index, row in enumerate(reader):
						if crit["type"] == "==":
							if row[crit["name"]] == crit["value"]:
								line_no.append(index)
						elif crit["type"] == "!=":
							if row[crit["name"]] != crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">=":
							if row[crit["name"]] >= crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<=":
							if row[crit["name"]] <= crit["value"]:
								line_no.append(index)
						elif crit["type"] == ">":
							if row[crit["name"]] > crit["value"]:
								line_no.append(index)
						elif crit["type"] == "<":
							if row[crit["name"]] < crit["value"]:
								line_no.append(index)
						else:
							line_no = False
			if line_no == False:
				return self.returner(700)
		nindexlines = []
		indexlines = []
		with open("index.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=indexread)
			for row in reader:
				indexlines.append(row)
		with open("nindex.NHX", "r+", newline="") as file:
			reader = csv.DictReader(file, delimiter="|", fieldnames=nindexread)
			for row in reader:
				nindexlines.append(row)
		tout = []
		for line in line_no:
			to_append = {}
			to_append.update(nindexlines[line])
			to_append.update(indexlines[line])
			tout.append(to_append)
		return self.returner(tout)


if __name__ == "__main__":
	print("\n\n                     +++++++++++++++++++++++++++++++++++++++++++")
	print("                             Welcome to the NHXDB Module\n")
	print("                                     By NHXTech")
	print("                           Written by Ch. Muhammad Sohaib")
	print("        Since this is a module, it is designed to be used from another Python Script")
	print("             For more details visit our Github page and get started with NHXDB       ")
	print("                     +++++++++++++++++++++++++++++++++++++++++++\n\n")