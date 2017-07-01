from mesa import Agent
from classes.Task import Task
from classes.Email import Email

import configuration.general_settings as general_settings
import configuration.model_settings as model_settings

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
            self.calculateTimePressure()
            if len(self.tasks) > 0:
                self.workInTask()
                self.addOvertimeHoursContribution()

        elif self.model.timer.day_interval == 'sleep_time':
            if len(self.tasks) == 0:
                self.rest()

        elif self.model.timer.day_interval == 'free_time':
            print("I'm at free time")


        self.printTimePressure()
        self.printEffectiveFatigue()
        self.printTasksNumber()

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

    def calculateEventStress(self):
        self.event_stress = min(1, len(self.tasks)/2/self.average_daily_tasks)

    def calculateTimePressure(self):
        total_tasks_remaining_time = sum(task.remaining_time for task in self.tasks)
        #print("I am worker " + str(self.unique_id) + " and I have a total task duration of " + str(total_tasks_remaining_time))
        self.time_pressure = total_tasks_remaining_time/(total_tasks_remaining_time+max(1, self.model.timer.work_remaining_time))

    def addOvertimeHoursContribution(self):
        wpmf = model_settings.overtime_contribution/general_settings.time_by_step
        self.effective_fatigue += wpmf/(wpmf+self.fatigue_tolerance)
        if self.effective_fatigue > 1: self.effective_fatigue = 1

    def addNewEmailContribution(self):
        wpmf = model_settings.email_reception_contribution
        self.effective_fatigue += wpmf/(wpmf+self.fatigue_tolerance)
        if self.effective_fatigue > 1: self.effective_fatigue = 1

    def addRestTimeContribution(self):
        self.effective_fatigue -= model_settings.rest_time_contribution/general_settings.time_by_step/10
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
