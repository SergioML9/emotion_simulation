import json

steps = [[] for _ in range(500)]

for i in range(0, 10):
	steps[0].append({ "agent": i, "position": "Hall.1"})

def addAgentMovement(agent, room, stepStart, stepEnd):
	steps[stepStart+1].append({"agent":agent.unique_id, "moveTo": room, "toStep": stepEnd+1})

def addAgentEmotion(agent, stress):
	sentiment = ''

	if 0 < stress < 1:
		sentiment = 'surprise'
	elif 1 < stress < 2:
		sentiment = 'sadness'
	elif 2 < stress < 3:
		sentiment = 'fear'
	elif 3 < stress < 4:
		sentiment = 'happiness'
	elif 4 < stress < 5:
		sentiment = 'anger'
	else:
		sentiment = 'happiness'

	steps[stepStart+1].append({"agent":agent.unique_id, "sentiment": sentiment})

def addLightState(room, state, stepStart):
	steps[stepStart+1].append({"light":state, "room": room})

def generateJSON():
	data = {"type":0, "steps": steps}
	print(data)
	with open('ramen/example/js/lab_move.json', 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()