#! /usr/bin/python3

import  psycopg2
#connect to safetydome database as flask on the localhost
conn = psycopg2.connect(dbname='safetydome', user='flask', password='flask', host='localhost')
cur = conn.cursor()

from flask import Flask, render_template, abort
import re
import os

app = Flask(__name__)

#classes needed for the templated to work
class Combatant():
	def __init__(self, ids, name, species):
		self.id = ids
		self.name = name
		self.species = species

class Fight():
	def __init__(self, one_id, two_id, one_name, two_name, winner, ids):
		self.one_id = one_id
		self.two_id = two_id
		self.one_name = one_name
		self.two_name = two_name
		self.winner = winner
		self.id = ids
class Results():
	def __init__(self, name, ids, wins, rank):
		self.name = name
		self.id = ids
		self.wins = wins
		self.rank = rank

#setting up the route for index.html
@app.route('/')
def main():
	return render_template('index.html')

#setting up the route for combatant plus identifier on the url line
@app.route('/combatant/<identifier>')
def combatants_id(identifier=None):
	if identifier:
		#to abort if sql section attempted
		if not re.search('^-?[0-9]+$', identifier):
			abort(404)

		#sql query being made
		cur.execute('''select combatant.id, combatant.name, species.type, species.name, species.base_atk, species.base_dfn, 					species.base_hp
				from combatant, species where combatant.species_id = species.id;''')
		rows = list(cur.fetchall())
		for row in rows:
			if row[0] == int(identifier):
				return render_template('combatants_id.html', row=row)
				break
	else:
		abort(404)

#route for just combatant
@app.route('/combatant')
def combatants():
	cur.execute('''select * from combatant order by combatant.name ASC;''')
	rows = list(cur.fetchall())
	combatant = []
	#loop to set up combatant class object
	for row in rows:
		combatant.append(Combatant(row[0], row[1], row[2]))
	return render_template('combatants.html', combatants=combatant)

#route for battle by itself
@app.route('/battle')
def battle():
	#query needed to link name for each battle member
	cur.execute('''select combatant_one, combatant_two,
			(select name from combatant where combatant_one = combatant.id),
			(select name from combatant where combatant_two = combatant.id),
			winner, fight.id 
			from fight, combatant''')
	rows = list(cur.fetchall())
	fight = []
	#loop to set up the fight object
	for row in rows:
		fight.append(Fight(row[0], row[1], row[2], row[3], row[4], row[5]))
	return render_template('battle.html', fights=fight)

#route for battle id plus the 2 ids on the url line
@app.route('/battle/<id1>-<id2>')
def battle_detail(id1=None, id2=None):
	if id1 and id2:
		#the 2 checks to control sql injection and abort
		if not re.search('^-?[0-9]+$', id1):
			abort(404)

		if not re.search('^-?[0-9]+$', id2):
			abort(404)

		cur.execute('''select * from fight''')

		rows = list(cur.fetchall())

		for row in rows:
			if row[0] == int(id1) and row[1] == int(id2):
				return render_template('battle_detail.html', details=row)
				break
	else:
		abort(404)

@app.route('/results')
def results():
	#solution found with help from Samuels
	#https://github.com/ExSickness/safetydome/blob/master/app.py
	fighters = []

	cur.execute('''select count(*) from combatant;''')
	
	num_of_combatants = cur.fetchone()[0]
	
	#loop through to grab from differnt sql querys
	for i in range(1, num_of_combatants+1):
		total_wins = 0
		cur.execute("select * from fight where combatant_one = %s and winner = 'One'", (i,))
		total_wins = len(cur.fetchall())
		cur.execute("select * from fight where combatant_two = %s and winner = 'Two'", (i,))
		total_wins+= len(cur.fetchall())
		cur.execute("SELECT name FROM combatant WHERE id=%s", (i,))
		combatant_name = cur.fetchone()[0]
		fighters.append( [i, total_wins, combatant_name] )

	#sorts based on wins reverse
	fighters.sort(key=lambda x: x[1], reverse=True)
	for i in range(len(fighters)):
		fighters[i].append(i+1)

	return(render_template('results.html',combatants=fighters))

if __name__ == '__main__':
	#causing the app to run with my port and and debug turned on
	app.run(debug=True, port=8054)
