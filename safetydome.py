#! /usr/bin/python3

import  psycopg2
conn = psycopg2.connect(dbname='safetydome', user='flask', password='flask', host='localhost')
cur = conn.cursor()

from flask import Flask, render_template

app = Flask(__name__)

class Combatant():
	def __init__(self, ids, name, species):
		self.id = ids
		self.name = name
		self.species = species

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/combatant/<identifier>')
def combatants_id(identifier=None):
	cur.execute('''select combatant.id, combatant.name, species.type, species.name, species.base_atk, species.base_dfn, species.base_hp
			from combatant, species where combatant.species_id = species.id;''')
	rows = list(cur.fetchall())
	for row in rows:
		if row[0] == int(identifier):
			return render_template('combatants_id.html', row=row)
			break

@app.route('/combatant')
def combatants():
	cur.execute('''select * from combatant order by combatant.name ASC;''')
	rows = list(cur.fetchall())
	combatant = []
	for row in rows:
		combatant.append(Combatant(row[0], row[1], row[2]))
	return render_template('combatants.html', combatants=combatant)

@app.route('/results')
def results():
	return render_template('results.html')

@app.route('/battle')
def battle():
	return render_template('battle.html')

if __name__ == '__main__':
	app.run(debug=True, port=8054)
