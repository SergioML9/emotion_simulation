import random

def init():

	global occupancy_json
	#Store the occupancy
	occupancy_json = []

		#Workers
	#Number of Occupants
	NWorkers = 10

	#Define states: name (str), position: str or ditc
	statesWorkers = [
		{'name':'leave', 'position': 'outBuilding'}, #initial state (the first)
		{'name':'working in my workplace', 'position': {'Lab1.3': 1, 'Lab1.4': 1, 'Lab1.6': 1, 'Lab1.7': 1, 'Lab1.8': 1, 'Lab2.3': 1, 'Lab2.4': 1, 'Lab2.6': 1, 'Lab2.7': 1, 'Lab2.8': 1}},
		{'name':'resting', 'position':'Hall.4'},
		{'name':'lunch', 'position': 'outBuilding'}
	]

	#Define initial markov matrix
	markov_matrixWorkers = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

	controlBehaviourWorkers = {'arriveTime': 9.00, 'lunchTime': 13.00, 'backLunchTime': 14.00, 'leaveWorkTime': 17.30}

	WorkersOccupants = {'type':'workers' , 'N':NWorkers, 'states': statesWorkers ,'matrix': markov_matrixWorkers, 'lifeWay': controlBehaviourWorkers}
	
	occupancy_json.append(WorkersOccupants)

def returnMatrix(agent, time):
	new_matrix = False
	behaviour = agent.behaviour

	if agent.type == 'workers':
		if time < behaviour['arriveTime']:
			new_matrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
		elif behaviour['lunchTime'] >= time >= behaviour['arriveTime']:
			new_matrix = [[55, 35, 0, 0], [0, 75, 35, 0], [0, 100, 0, 0], [0, 0, 0, 0, 0]]
		elif behaviour['backLunchTime']  >= time >= behaviour['lunchTime']:
			new_matrix = [[0, 0, 0, 0], [0, 70, 0, 30], [0, 100, 0, 0], [0, 0, 0, 0]]
		elif behaviour['leaveWorkTime'] >= time >= behaviour['backLunchTime']:
			new_matrix = [[0, 0, 0, 0], [0, 75, 40, 0], [0, 100, 0, 0], [0, 100, 0, 0]]
		elif time >= behaviour['leaveWorkTime']:
			new_matrix = [[100, 0, 0, 0], [70, 30, 0, 0], [0, 100, 0, 0], [0, 0, 0, 0]]
		return new_matrix 

	else:
		return new_matrix

def getTimeInState(agent, time): #Hours.Minutes
	timeActivity_matrix = False
	behaviour = agent.behaviour

	if agent.type == 'workers':
		if time < behaviour['arriveTime']:
			timeActivity_matrix = [8.0, 0, 0, 0]
		elif behaviour['lunchTime'] >= time >= behaviour['arriveTime']:
			timeActivity_matrix = [0.30, 1.00, 0.30, 0]
		elif behaviour['backLunchTime']  >= time >= behaviour['lunchTime']:
			timeActivity_matrix = [0, 0.05, 0, 1.0]
		elif behaviour['leaveWorkTime'] >= time >= behaviour['backLunchTime']:
			timeActivity_matrix = [0, 1.00, 0.30, 0.1]
		elif time >= behaviour['leaveWorkTime']:
			timeActivity_matrix = [5, 0.30, 0.10, 0]
		return timeActivity_matrix

	else:
		return timeActivity_matrix