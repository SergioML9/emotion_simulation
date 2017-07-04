import json

steps = [[] for _ in range(500)]

for i in range(0, 10):
	steps[0].append({ "agent": i, "position": "Hall.1"})

def addAgentMovement(agent, room, stepStart, stepEnd):
	steps[stepStart+1].append({"agent":agent.unique_id, "moveTo": room, "toStep": stepEnd})

def generateJSON():
	data = {"type":0, "steps": steps}
	print(data)
	with open('move.json', 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()