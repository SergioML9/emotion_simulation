from mesa import Agent
from classes.Task import Task
from classes.Email import Email

import configuration.general_settings as general_settings
import configuration.model_settings as model_settings

import math

class WorkerAgent(Agent):

    def __init__(self, worker_id, model):
        super().__init__(worker_id, model)

        # Agent attributes initialization
        self.step_counter = 0
        self.average_daily_tasks = 0
        self.total_tasks_number = 0
        self.fatigue_tolerance = 0.5

        self.email_read_distribution_over_time = []
        self.emails = []
        self.tasks = []

        # Stress attributes initialization
        self.stress = 0
        self.event_stress = 0
        self.effective_fatigue = 0
        self.time_pressure = 0
        self.productivity = 1

    def step(self):

        # Step counter
        self.step_counter += 1

        # Calculate interval and do tasks
        if self.model.timer.day_interval == 'work_time':

            # Add temperature, humidity and noise contribution
            self.addAmbientContribution()
            self.addNoiseContribution()

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
                    self.rest()

        elif self.model.timer.day_interval == 'overtime':

            # Add temperature, humidity and noise contribution
            self.addAmbientContribution()
            self.addNoiseContribution()

            self.calculateTimePressure()
            if len(self.tasks) > 0:
                self.workInTask()
                self.addOvertimeHoursContribution()

        elif self.model.timer.day_interval == 'sleep_time':
            if len(self.tasks) == 0:
                self.rest()

        elif self.model.timer.day_interval == 'free_time':
            self.rest()

        #self.printTimePressure()
        #self.printEffectiveFatigue()
        #self.printTasksNumber()
        self.stress = min(1, (self.event_stress + self.time_pressure + self.effective_fatigue) / 3)
        self.calculateProductivity()

        self.printStress()
        self.printProductivity()

    def workInTask(self):

        # select a task to work in
        current_task = self.tasks[0]

        # work in the task selected
        current_task.remaining_time -= self.productivity*general_settings.time_by_step/60

        # check if the task has finished
        if current_task.remaining_time <= 0:
            self.tasks.pop(0)
            current_task = None

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

    def rest(self):
        self.addRestTimeContribution()

    def addTask(self, task):
        self.tasks.append(task)
        self.total_tasks_number += 1

    def calculateProductivity(self):
        self.productivity = 1/(0.4*math.sqrt(2*math.pi))*pow(math.e, -0.5*pow(((self.stress-0.5)/0.2), 2))

    def calculateEventStress(self):
        self.event_stress = min(1, len(self.tasks)/2/self.average_daily_tasks)

    def calculateTimePressure(self):
        total_tasks_remaining_time = sum(task.remaining_time for task in self.tasks)
        #print("I am worker " + str(self.unique_id) + " and I have a total task duration of " + str(total_tasks_remaining_time))
        self.time_pressure = total_tasks_remaining_time/(total_tasks_remaining_time+max(1, self.model.timer.work_remaining_time))

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

        wpmf = abs(self.model.sensor.wbgt-22)*model_settings.ambient_contribution

        if self.model.sensor.wbgt > 25 or self.model.sensor.wbgt < 20:
            self.effective_fatigue += (wpmf/(wpmf+self.fatigue_tolerance))/general_settings.time_by_step
        else:
            self.effective_fatigue -= wpmf/10
        if self.effective_fatigue > 1: self.effective_fatigue = 1
        if self.effective_fatigue < 0: self.effective_fatigue = 0

    def addNoiseContribution(self):
        wpmf = (self.model.sensor.noise - 60)*model_settings.noise_contribution/general_settings.time_by_step
        self.effective_fatigue += (wpmf/(wpmf+self.fatigue_tolerance))/general_settings.time_by_step

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
