import json

steps = [[] for _ in range(500000)]

steps[0].append({"light":'low', "room": 'Hall.1'})
steps[0].append({"light":'low', "room": 'Lab1.1'})
steps[0].append({"light":'low', "room": 'Lab2.1'})


def addAgentMovement(agent, room, stepStart, stepEnd):
	steps[stepStart+1].append({"agent":agent.unique_id, "moveTo": room, "toStep": stepEnd+1})

def createAgent(agent, step):
	steps[step].append({ "agent": agent.unique_id, "position": "entrance"})

def addAgentEmotion(agent, stressAux, step):
	sentiment = ''
	stress = stressAux
	if stress < 0.1:
		sentiment = 'surprise'
	elif 0.1 < stress < 0.2:
		sentiment = 'sadness'
	elif 0.2 < stress < 0.3:
		sentiment = 'fear'
	elif 0.3 < stress < 0.4:
		sentiment = 'happiness'
	elif 0.4 < stress:
		sentiment = 'anger'
	else:
		sentiment = 'happiness'
	steps[step].append({"agent":agent.unique_id, "sentiment": sentiment})
	print(agent.unique_id, agent.state, sentiment)

def addLightState(room, state, step):
	steps[step+2].append({"light":state, "room": room.name})

def stateTV(state, step):
	stateTV = 'false'
	if state == True:
		stateTV = 'true'
	steps[step].append({"video": stateTV, "room": "Hall.4"})

def generateJSON():
	data = {"type":0, "steps": steps}
	print(data)
	with open('ramen-module/example/js/lab_move.json', 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()