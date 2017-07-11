from mesa import Agent
from classes.Task import Task
from classes.Email import Email
from transitions import Machine
from transitions import State
import space.aStar
from agents.behaviourMarkov import Markov
from collections import OrderedDict

import model.ramenScript
import random
import operator
import configuration.general_settings as general_settings
import configuration.model_settings as model_settings
import configuration.automation_settings as automation_settings
import configuration

import math

class WorkerAgent(Agent):

    def __init__(self, worker_id, model, json):
        super().__init__(worker_id, model)

        #SOBA
        self.behaviour = {}
        for k, v in json['lifeWay'].items():
        	self.behaviour[k] = self.model.clock.getDownCorrectHour(v + random.randrange(-10, 11)/100)
        self.type = json['type']

        #State machine
        self.positionByState = OrderedDict()
        states = []
        for state in json['states']:
            name = state['name']
            pos = self.model.getPosState(name, self.type)
            on_enter = 'start_activity'
            on_exit = 'finish_activity'
            self.positionByState[name] = pos
            states.append(State(name=name, on_enter=[on_enter], on_exit=[on_exit]))
        self.machine = Machine(model=self, states=states, initial=states[0].name)

        self.triggers = {}
        n_state = 0
        for state in json['states']:
            name = state['name']
            self.machine.add_transition('setState'+str(n_state), '*', name)
            self.triggers[name] = 'setState'+str(n_state)+'()'
            n_state = n_state + 1

        self.markov_matrix = json['matrix']
        self.markov_machine = Markov(self)

        #control
        self.markov = True
        self.time_activity = 0
        self.place_to_go = self.model.outBuilding.pos
        self.movements = []
        self.N = 0
        self.onMyWay1 = False
        self.onMyWay2 = False
        self.costMovementToNewRoom = 0
        self.costMovementInNewRoom = 0
        self.lastSchedule = 0.0
        self.room1 = False
        self.room2 = False
        self.stepStartMovement = 0
        self.creation = True

        # Agent attributes initialization
        self.step_counter = 0
        self.average_daily_tasks = 0
        self.total_tasks_number = 0
        self.fatigue_tolerance = 0.5

        self.email_read_distribution_over_time = []
        self.emails = []
        self.tasks = []
        self.emails_read = 0
        self.overtime_hours = 0
        self.rest_at_work_hours = 0
        self.tasks_completed = 0

        # Stress attributes initialization
        self.stress = 0
        self.event_stress = 0.5
        self.effective_fatigue = 0
        self.time_pressure = 0.5
        self.productivity = 1


    # Methods when entering/exit states
    def start_activity(self):
        if (self.state != 'leave') and (self.creation == True):
            self.unique_id = self.model.agentsIn
            self.model.agentsIn = self.model.agentsIn + 1
            model.ramenScript.createAgent(self, self.model.NStep)
            self.creation = ''
        self.markov = False
        self.place_to_go = self.getPlaceToGo()
        if self.pos != self.place_to_go:
            self.movements = space.aStar.getPath(self.model, self.pos, self.place_to_go)
        else:
            self.movements = [self.pos]
        time_in_state = self.model.getTimeInState(self)[list(self.positionByState.keys()).index(self.state)]
        self.time_activity = int(self.model.clock.getMinuteFromHours(time_in_state)*60 / configuration.settings.time_by_step)
        self.N = 0

    def finish_activity(self):
        if self.state == 'resting':
            self.logTV(False)

    #Movement
    def occupantMovePos(self, new_position):
        ux, uy = self.pos
        nx, ny = new_position
        for room in self.model.rooms:
            rx, ry = room.pos
            if room.pos == self.pos:
            #Cost as steps
                if (rx == nx):
                    self.costMovemenToNewRoom = room.dy/2 * (1/configuration.settings.speed) * (1/configuration.settings.time_by_step)# m * seg/m * step/seg
                if (ry == ny):
                    self.costMovemenToNewRoom = room.dx/2 * (1/configuration.settings.speed) * (1/configuration.settings.time_by_step)
            if room.pos == new_position:
                if (rx == ux):
                    self.costMovementInNewRoom = room.dy/2 * (1/configuration.settings.speed) * (1/configuration.settings.time_by_step)
                if (ry == uy):
                    self.costMovementInNewRoom = room.dx/2 * (1/configuration.settings.speed) * (1/configuration.settings.time_by_step)

    def getPlaceToGo(self):
        place_to_go = self.pos
        possible_rooms = []
        for room in self.model.rooms:
            if room.name == self.positionByState[self.state]:
                possible_rooms.append(room.pos)
        if place_to_go in possible_rooms:
            return place_to_go
        if len(possible_rooms) > 1:
            place_to_go = random.choice(possible_rooms)
        elif len(possible_rooms) > 0:
            place_to_go = possible_rooms[0]
        return place_to_go

    def changeSchedule(self):
        beh = sorted(self.behaviour.items(), key=operator.itemgetter(1))
        nextSchedule = False
        for i in beh:
            a, b = i
            if b < self.model.clock.clock:
                nextSchedule = a
        if nextSchedule != self.lastSchedule:
            self.lastSchedule = nextSchedule
            return True
        else:
            return False

    def sobaStep(self):
        self.model.getMatrix(self)
        if self.markov == True or self.changeSchedule():
            self.markov_machine.runStep(self.markov_matrix)
        elif self.onMyWay1 == True:
            if self.costMovemenToNewRoom > 0:
                self.costMovemenToNewRoom = self.costMovemenToNewRoom - 1
            else:
                room1 = self.model.getRoom(self.pos)
                room2 = self.model.getRoom(self.movements[self.N])
                self.room1 = room1
                self.room2 = room2
                if room1.name.split(r".")[0] != room2.name.split(r".")[0]:
                    self.model.openDoor(self, room1, room2)
                self.model.popAgentRoom(self, self.pos)
                self.model.grid.move_agent(self, self.movements[self.N])
                self.model.pushAgentRoom(self, self.pos)
                self.N = self.N + 1
                self.onMyWay1 = False
                self.onMyWay2 = True
        elif self.onMyWay2 == True:
            if self.costMovementInNewRoom > 0:
                self.costMovementInNewRoom = self.costMovementInNewRoom - 1
            else:
                room1 = self.room1
                room2 = self.room2
                if room1.name.split(r".")[0] != room2.name.split(r".")[0]:
                    self.model.closeDoor(self, room1, room2)
                self.onMyWay2 = False
                model.ramenScript.addAgentMovement(self, self.room2.name, self.stepStartMovement, self.model.NStep)
                self.step()
        elif self.pos != self.place_to_go:
            self.occupantMovePos(self.movements[self.N])
            self.onMyWay1 = True
            self.stepStartMovement = self.model.NStep
            self.step()
        else:
            self.N = 0
            if self.state == 'resting':
                self.logTV(True)
            if self.time_activity > 0:
                self.time_activity = self.time_activity - 1
            else:
                self.markov = True

    def step(self):
        self.sobaStep()
        
        # Step counter
        self.step_counter += 1

        # Calculate interval and do tasks
        # if self.state == 'name'
        if self.model.timer.day_interval == 'work_time':

            # Add temperature, humidity and noise contribution
            self.addAmbientContribution()
            self.addNoiseContribution()
            self.addLuminosityContribution()

            self.calculateTimePressure()

            # Check if there is a new email
            if len(self.email_read_distribution_over_time) > 0 and self.email_read_distribution_over_time[self.model.timer.worked_time-1] == 1:
                self.receiveEmail()

            # If there is any email, worker has to read it
            if len(self.emails) > 0:
                self.readEmail()
            else:
                if len(self.tasks) > 0:
                    self.workInTask()
                else:
                    self.rest_at_work_hours += 1/60
                    self.rest()

        elif self.model.timer.day_interval == 'overtime':

            # Add temperature, humidity, luminosity and noise contribution
            self.addAmbientContribution()
            self.addNoiseContribution()
            self.addLuminosityContribution()

            self.calculateTimePressure()
            if len(self.tasks) > 0:
                self.workInTask()
                self.overtime_hours += 1/60
                self.addOvertimeHoursContribution()

        elif self.model.timer.day_interval == 'sleep_time':
            self.rest()

        elif self.model.timer.day_interval == 'free_time':
            self.rest()

        #self.printTimePressure()
        #self.printEffectiveFatigue()
        #self.printTasksNumber()
        self.stress = min(1, (self.event_stress + self.time_pressure + self.effective_fatigue) / 3)
        self.calculateProductivity()

        #self.printStress()
        #self.printProductivity()
        if self.creation != True:
            self.logStress()

    def logStress(self):
    	#model.ramenScript.addAgentEmotion(self, self.stress)
        model.ramenScript.addAgentEmotion(self, random.randrange(0, 10)/10, self.model.NStep)
    
    def logTV(self, state):
        model.ramenScript.stateTV(state, self.model.NStep)

    def workInTask(self):

        # select a task to work in
        current_task = self.tasks[0]

        # work in the task selected
        current_task.remaining_time -= (self.productivity+model_settings.tasks_automation_contribution)*general_settings.time_by_step/60

        # check if the task has finished
        if current_task.remaining_time <= 0:
            self.tasks.pop(0)
            current_task = None
            self.tasks_completed += 1

    def receiveEmail(self):
        self.emails.append(Email())
        self.addNewEmailContribution()

    def readEmail(self):

        # select the email to read
        current_email = self.emails[0]

        # read it
        current_email.read_time -= general_settings.time_by_step/60

        # check if the email has been read
        if current_email.read_time <= 0:
            self.emails.pop(0)
            current_email = None
            self.emails_read += 1

    def rest(self):
        self.addRestTimeContribution()

    def addTask(self, task):
        self.tasks.append(task)
        self.total_tasks_number += 1

    def calculateProductivity(self):
        self.productivity = 1/(0.4*math.sqrt(2*math.pi))*pow(math.e, -0.5*pow(((self.stress-0.5)/0.2), 2))

    def calculateEventStress(self, tasks_number):
        self.event_stress = min(1, tasks_number/2/self.average_daily_tasks)

    def calculateTimePressure(self):
        total_tasks_remaining_time = sum(task.remaining_time for task in self.tasks)
        #print("I am worker " + str(self.unique_id) + " and I have a total task duration of " + str(total_tasks_remaining_time))
        self.time_pressure = total_tasks_remaining_time/(total_tasks_remaining_time+self.model.timer.work_remaining_time+60)

    def addOvertimeHoursContribution(self):
        wpmf = model_settings.overtime_contribution
        self.effective_fatigue += wpmf/(wpmf+self.fatigue_tolerance)/general_settings.time_by_step
        if self.effective_fatigue > 1: self.effective_fatigue = 1

    def addNewEmailContribution(self):
        wpmf = model_settings.email_reception_contribution
        self.effective_fatigue += wpmf/(wpmf+self.fatigue_tolerance)
        if self.effective_fatigue > 1: self.effective_fatigue = 1

    def addRestTimeContribution(self):
        self.effective_fatigue -= model_settings.rest_time_contribution/10/general_settings.time_by_step
        if self.effective_fatigue < 0: self.effective_fatigue = 0

    def addAmbientContribution(self):

        if self.model.sensor.wbgt > 25 or self.model.sensor.wbgt < 20:
            wpmf = abs(self.model.sensor.wbgt-22)*model_settings.ambient_contribution
            self.effective_fatigue += (wpmf/(wpmf+self.fatigue_tolerance))/general_settings.time_by_step
        else:
            wpmf = model_settings.ambient_contribution*22/(6*abs(22-self.model.sensor.wbgt+0.1))
            self.effective_fatigue -= wpmf/10/general_settings.time_by_step
        if self.effective_fatigue > 1: self.effective_fatigue = 1
        if self.effective_fatigue < 0: self.effective_fatigue = 0

    def addNoiseContribution(self):

        if self.model.sensor.noise > 65:
            wpmf = (self.model.sensor.noise - 60)*model_settings.noise_contribution/general_settings.time_by_step
            self.effective_fatigue += (wpmf/(wpmf+self.fatigue_tolerance))/general_settings.time_by_step
        else:
            wpmf = abs(self.model.sensor.noise-60)*model_settings.noise_contribution/general_settings.time_by_step
            self.effective_fatigue -= wpmf/10/general_settings.time_by_step

        if self.effective_fatigue > 1: self.effective_fatigue = 1
        if self.effective_fatigue < 0: self.effective_fatigue = 0

    def addLuminosityContribution(self):

        if self.model.sensor.luminosity > 750 or self.model.sensor.luminosity < 450:
            wpmf = abs(self.model.sensor.luminosity-600)*model_settings.luminosity_contibution
            self.effective_fatigue += (wpmf/(wpmf+self.fatigue_tolerance))/general_settings.time_by_step
        else:
            wpmf = 600/(4*abs(600-self.model.sensor.luminosity))*model_settings.luminosity_contibution
            self.effective_fatigue -= wpmf/10/general_settings.time_by_step

        if self.effective_fatigue > 1: self.effective_fatigue = 1
        if self.effective_fatigue < 0: self.effective_fatigue = 0

    def calculateAverageDailyTasks(self, days):
        self.average_daily_tasks = self.total_tasks_number/days

    def printAverageDailyTasks(self):
        print("I am worker " + str(self.unique_id) + " and I my average daily tasks number is " + str(self.average_daily_tasks))

    def printTasksNumber(self):
        print("I am worker " + str(self.unique_id) + " and I have " + str(len(self.tasks)) + " tasks remaining.")

    def printEventStress(self):
        print("I am worker " + str(self.unique_id) + " and my event stress level is " + str(self.event_stress))

    def printTimePressure(self):
        print("I am worker " + str(self.unique_id) + " and my time pressure level is " + str(self.time_pressure))

    def printEffectiveFatigue(self):
        print("I am worker " + str(self.unique_id) + " and my effective fatigue level is " + str(self.effective_fatigue))

    def printStress(self):
        print("I am worker " + str(self.unique_id) + " and my stress level is " + str(self.stress))

    def printProductivity(self):
        print("I am worker " + str(self.unique_id) + " and my productivity is " + str(self.productivity))
