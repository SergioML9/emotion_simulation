from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.space import ContinuousSpace

from collections import defaultdict
import random
from model.time import Time
from space.room import Room
from space.door import Door
from space.wall import Wall
from agents.Light import Light
import configuration.settings
import configuration.defineOccupancy
import configuration.defineMap

from agents.WorkerAgent import WorkerAgent
from agents.TimeAgent import TimeAgent
from agents.SensorAgent import SensorAgent
from datacollection.WorkerCollector import WorkerCollector
from datacollection.SensorCollector import SensorCollector
from datacollection.TimeCollector import TimeCollector

from classes.Task import Task

import configuration.workload_settings as workload_settings
import configuration.email_settings as email_settings

import numpy as np
import math
import random

# somen
# Smart Office Multiagent emotional Environments

class SOMENModel(Model):

    def __init__(self, width, height):


        # Model attributes initialization
        self.workers_number = 10
        self.agents = []
        self.workers = []
        self.average_stress = 0
        self.running = True

        #SOBA
        configuration.settings.init()
        configuration.defineOccupancy.init()
        configuration.defineMap.init()

        self.clock = Time()

        #Vars of control
        self.num_occupants = 0
        self.day = self.clock.day
        self.NStep = 0
        self.placeByStateByTypeAgent = {}
        self.agentsWorkingByStep = []

        # Schedule
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(width, height, False)

        #Create the map
        self.createRooms()
        self.setMap(width, height)
        self.createDoors()
        self.createWalls()
        #Create agents
        self.setAgents()

        # Create timer agent
        self.timer = TimeAgent(len(self.agents), self)
        self.schedule.add(self.timer)
        self.agents.append(self.timer)

        # Create sensor agent
        self.sensor = SensorAgent(len(self.agents), self)
        self.schedule.add(self.sensor)
        self.agents.append(self.sensor)

        '''
        # Create workers agents
        for i in range(self.workers_number):
            worker = WorkerAgent(i+len(self.agents), self)
            self.schedule.add(worker)
            self.workers.append(worker)
        '''

        # Create data collectors
        self.model_collector = DataCollector(model_reporters={"Average Stress": lambda a: a.average_stress})
        self.worker_collector = WorkerCollector(agent_reporters={"Stress": lambda a: a.stress,
            "Event Stress": lambda a: a.event_stress, "Time Pressure": lambda a: a.time_pressure,
            "Effective Fatigue": lambda a: a.effective_fatigue, "Productivity": lambda a: a.productivity,
            'Emails read': lambda a: a.emails_read, 'Pending tasks': lambda a: len(a.tasks),
            'Overtime hours': lambda a: a.overtime_hours, 'Rest at work hours': lambda a: a.rest_at_work_hours,
            'Tasks completed': lambda a: a.tasks_completed})
        self.sensor_collector = SensorCollector(agent_reporters={"Temperature": lambda a: a.wbgt,
            "Noise": lambda a: a.noise, "Luminosity": lambda a: a.luminosity})
        self.time_collector = TimeCollector(agent_reporters={"Day": lambda a: a.days,
            "Time": lambda a: a.clock})


    #SOBA
    def setAgents(self):        
        self.lights = []
        id_light = 0
        for room in self.rooms:
            if room.typeRoom != 'out' and room.light == False:
                light = Light(id_light, self, room)
                self.lights.append(light)
                id_light = id_light + 1
                room.light = light
                for room2 in self.rooms:
                    if room.name.split(r".")[0] == room2.name.split(r".")[0]:
                        room2.light = light
        # Height and Width
        height = self.grid.height
        width = self.grid.width

        # CREATE AGENTS

        self.agents = []
        # Create occupants
        for n_type_occupants in configuration.defineOccupancy.occupancy_json:
            self.placeByStateByTypeAgent[n_type_occupants['type']] = n_type_occupants['states']
            n_agents = n_type_occupants['N']
            for i in range(0, n_agents):
                a = WorkerAgent(i+len(self.agents), self, n_type_occupants)
                self.workers.append(a)
                self.schedule.add(a)
                self.grid.place_agent(a, self.outBuilding.pos)
                self.pushAgentRoom(a, self.outBuilding.pos)
                self.num_occupants = self.num_occupants + 1

        self.schedule.add(self.clock)

    def isConected(self, pos):
        nextRoom = False
        for room in self.rooms:
            if room.pos == pos:
                nextRoom = room
        if nextRoom == False:
            return False
        for x in range(0, width):
            for y in range(0, height):
                self.pos_out_of_map.append(x, y)
        for room in self.rooms:
            self.pos_out_of_map.remove(room.pos)

    def createRooms(self):
        rooms = configuration.defineMap.rooms_json
        self.rooms = []
        for room in rooms:
            newRoom  = 0
            name = room['name']
            typeRoom = room['type']
            if typeRoom != 'out':
                conectedTo = room.get('conectedTo')
                entrance = room.get('entrance')
                measures = room['measures']
                dx = measures['dx']
                dy = measures['dy']
                newRoom = Room(name, typeRoom, conectedTo, dx, dy)
                newRoom.entrance = entrance
            else:
                newRoom = Room(name, typeRoom, None, 0, 0,)
                self.outBuilding = newRoom
            self.rooms.append(newRoom)
        for room1 in self.rooms:
            if room1.conectedTo is not None:
                for otherRooms in list(room1.conectedTo.values()):
                    for room2 in self.rooms:
                        if room2.name == otherRooms:
                            room1.roomsConected.append(room2)
                            room2.roomsConected.append(room1)
        for room in self.rooms:
            room.roomsConected = list(set(room.roomsConected))
        sameRoom = {}
        for room in self.rooms:
            if sameRoom.get(room.name.split(r".")[0]) is None:
                sameRoom[room.name.split(r".")[0]] = 1
            else:
                sameRoom[room.name.split(r".")[0]] = sameRoom[room.name.split(r".")[0]] + 1

    def setMap(self, width, height):
        rooms_noPos = self.rooms
        rooms_using = []
        rooms_used = []
        for room in self.rooms:
            if room.entrance is not None:
                room.pos = (int(1), 1)
                rooms_using.append(room)
                rooms_used.append(room)
                rooms_noPos.remove(room)
                break
        while len(rooms_noPos) > 0:
            for roomC in rooms_using:
                xc, yc = roomC.pos
                rooms_conected = roomC.conectedTo
                rooms_using.remove(roomC)
                if rooms_conected is not None:
                    orientations = list(rooms_conected.keys())
                    for orientation in orientations:
                        if orientation == 'R':
                            for room in rooms_noPos:
                                if room.name == rooms_conected['R']:
                                    room.pos = (int(xc + 1), yc)
                                    rooms_noPos.remove(room)
                                    rooms_used.append(room)
                                    rooms_using.append(room)
                        elif orientation == 'U':
                            for room in rooms_noPos:
                                if room.name == rooms_conected['U']:
                                    room.pos = (xc, int(yc + 1))
                                    rooms_noPos.remove(room)
                                    rooms_used.append(room)
                                    rooms_using.append(room)
                        elif orientation == 'D':
                            for room in rooms_noPos:
                                if room.name == rooms_conected['D']:
                                    room.pos = (xc, int(yc - 1))
                                    rooms_noPos.remove(room)
                                    rooms_used.append(room)
                                    rooms_using.append(room)
                        elif orientation == 'L':
                            for room in rooms_noPos:
                                if room.name == rooms_conected['L']:
                                    room.pos = (int(xc -1), yc)
                                    rooms_noPos.remove(room)
                                    rooms_used.append(room)
                                    rooms_using.append(room)
                else:
                    pass
        self.rooms = rooms_used

    def createDoors(self):
        self.doors = []
        for roomC in self.rooms:
            roomsConected = roomC.roomsConected
            for room in roomsConected:
                door_created = False
                same_corridor = False
                if room.name != roomC.name:
                    for door in self.doors:
                        if (door.room1.name == roomC.name and door.room2.name == room.name) or (door.room2.name == roomC.name and door.room1.name == room.name):
                            door_created = True
                        if room.name.split(r".")[0] == roomC.name.split(r".")[0]:
                            same_corridor = True
                    if door_created == False and same_corridor == False:
                        d = Door(roomC, room)
                        self.doors.append(d)
                        room.doors.append(d)
                        roomC.doors.append(d)

    def createWalls(self):
        for room in self.rooms:
            if room.typeRoom != 'out':
                walls = []
                xr, yr = room.pos
                roomA = self.getRoom((xr, yr+1))
                if roomA != False:
                    if roomA.name.split(r".")[0] == room.name.split(r".")[0]:
                        pass
                    else:
                        wall = Wall(room, roomA)
                        walls.append(wall)
                else:
                    wall = Wall(room)
                    walls.append(wall)
                roomB = self.getRoom((xr, yr-1))
                if roomB != False:
                    if roomB.name.split(r".")[0] == room.name.split(r".")[0]:
                        pass
                    else:
                        wall = Wall(room, roomB)
                        walls.append(wall)
                else:
                    wall = Wall(room)
                    walls.append(wall)
                roomC = self.getRoom((xr+1, yr))
                if roomC != False:
                    if roomC.name.split(r".")[0] == room.name.split(r".")[0]:
                        pass
                    else:
                        wall = Wall(room, roomC)
                        walls.append(wall)
                else:
                    wall = Wall(room)
                    walls.append(wall)
                roomD = self.getRoom((xr-1, yr))
                if roomD != False:
                    if roomD.name.split(r".")[0] == room.name.split(r".")[0]:
                        pass
                    else:
                        wall = Wall(room, roomD)
                        walls.append(wall)
                else:
                    wall = Wall(room)
                    walls.append(wall)

                room.walls = walls

    def getPosState(self, name, typeA):
        placeByStateByTypeAgent = self.placeByStateByTypeAgent
        n = 0
        for state in self.placeByStateByTypeAgent[typeA]:
            if state.get('name') == name:
                pos1 = state.get('position')
                if isinstance(pos1, dict):
                    for k,v in pos1.items():
                        if v > 0:
                            placeByStateByTypeAgent[typeA][n]['position'][k] = v - 1
                            self.placeByStateByTypeAgent = placeByStateByTypeAgent
                            return k
                    return list(pos1.keys())[-1]
                else:
                    return pos1
            n = n +1

    def thereIsClosedDoor(self, beforePos, nextPos):
        oldRoom = False
        newRoom = False
        for room in rooms:
            if room.pos == beforePos:
                oldRoom = room
            if room.pos == nextPos:
                newRoom = room
        for door in self.doors:
            if (door.room1.name == oldRoom.name and door.room2.name == newRoom.name) or (door.room2.name == oldRoom.name and door.room1.name == newRoom.name):
                if door.state == False:
                    return True
        return False

    def thereIsOccupant(self, pos):
        possible_occupant = self.grid.get_cell_list_contents([pos])
        if (len(possible_occupant) > 0):
            for occupant in possible_occupant:
                if isinstance(occupant,Occupant):
                    return True
        return False

    def ThereIsOtherOccupantInRoom(self, room, agent):
        for roomAux in self.rooms:
            possible_occupant = []
            if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
                possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
            for occupant in possible_occupant:
                if isinstance(occupant, Occupant) and occupant != agent:
                    return True
        return False

    def ThereIsSomeOccupantInRoom(self, room):
        for roomAux in self.rooms:
            possible_occupant = []
            if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
                possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
            for occupant in possible_occupant:
                if isinstance(occupant, Occupant):
                    return True
        return False

    def thereIsOccupantInRoom(self, room, agent):
        for roomAux in self.rooms:
            possible_occupant = []
            if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
                possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
            for occupant in possible_occupant:
                if isinstance(occupant, Occupant) and occupant == agent:
                    return True
        return False

    def getRoom(self, pos):
        for room in self.rooms:
            if room.pos == pos:
                return room
        return False

    def pushAgentRoom(self, agent, pos):
        room = self.getRoom(pos)
        room.agentsInRoom.append(agent)

    def popAgentRoom(self, agent, pos):
        room = self.getRoom(pos)
        room.agentsInRoom.remove(agent)

    def openDoor(self, agent, room1, room2):
        for door in self.doors:
            if ((door.room1 == room1 and door.room2 == room2) or (door.room1 == room2 and door.room2 == room1)):
                door.state = False

    def closeDoor(self, agent, room1, room2):
        numb = random.randint(0, 10)
        for door in self.doors:
            if ((door.room1 == room1 and door.room2 == room2) or (door.room1 == room2 and door.room2 == room1)):
                if  7 >= numb:
                    door.state = False
                else:
                    door.state = True

    def getMatrix(self,agent):
        new_matrix = configuration.defineOccupancy.returnMatrix(agent, self.clock.clock)
        agent.markov_matrix = new_matrix
    
    def getTimeInState(self, agent):
        matrix_time_in_state = configuration.defineOccupancy.getTimeInState(agent, self.clock.clock)
        return matrix_time_in_state



    def sobaStep(self):
        aw = 0
        for agent in self.agents:
            if agent.state == 'working in my workplace':
                aw = aw + 1
        self.agentsWorkingByStep.append(aw)
        self.schedule.step()


        if (self.clock.day > self.day):
            self.day = self.day + 1
        self.NStep = self.NStep + 1

    def step(self):

        self.sobaStep()

        if self.timer.new_day:
            self.addTasks()
            self.createEmailsDistribution()


        self.average_stress = sum(worker.stress for worker in self.workers)/len(self.workers)

        if self.timer.new_hour:
            self.worker_collector.collect(self)
            self.sensor_collector.collect(self)
            self.time_collector.collect(self)
            self.model_collector.collect(self)

    def addTasks(self):
        ''' Add tasks to workers '''

        # Get task distribution params
        mu, sigma = workload_settings.tasks_arriving_distribution_params
        tasks_arriving_distribution = np.random.normal(mu, sigma, self.workers_number*10)

        for worker in self.workers:

            # Get number of tasks to add
            tasks_number = math.floor(abs(tasks_arriving_distribution [random.randint(0, 10*self.workers_number-1)]))
            worker.tasks_completed = 0

            # Add tasks
            for i in range(tasks_number):
                worker.addTask(Task())

            worker.calculateAverageDailyTasks(self.timer.days)
            worker.calculateEventStress(tasks_number)

            # worker.printTasksNumber()
            # worker.printAverageDailyTasks()
            # worker.printEventStress()

    def createEmailsDistribution(self):
        '''Create emails distribution'''
        # Get emails distribution
        mu, sigma = email_settings.emails_read_distribution_params
        emails_read_distribution = np.random.normal(mu, sigma, self.workers_number*10)

        for worker in self.workers:

            emails_received = math.floor(abs(emails_read_distribution[random.randint(0, 10*self.workers_number-1)]))
            emails_distribution_over_time = np.random.choice([0, 1], size=(480,), p=[(480-emails_received)/480, emails_received/480])
            worker.emails_read = 0
            worker.email_read_distribution_over_time = emails_distribution_over_time

            #print("Should have " + str(emails_received) + " and I have " + str(np.sum(emails_distribution_over_time == 1)))
