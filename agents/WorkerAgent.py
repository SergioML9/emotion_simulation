from mesa import Agent
from classes.Task import Task

import configuration.general_settings as general_settings

class WorkerAgent(Agent):

    def __init__(self, worker_id, model):
        super().__init__(worker_id, model)

        # Agent attributes initialization
        self.step_counter = 0
        self.average_daily_tasks = 0
        self.total_tasks_number = 0

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

        if self.model.timer.day_interval == 'work_time':
            self.calculateTimePressure()
            if len(self.tasks) > 0:
                self.workInTask()
        elif self.model.timer.day_interval == 'overtime':
            print("I'm working overtime hours")
        elif self.model.timer.day_interval == 'sleep_time':
            print("I'm sleeping")
        elif self.model.timer.day_interval == 'free_time':
            print("I'm at free time")

        self.printTimePressure()

    def workInTask(self):

        # select a task to work in
        current_task = self.tasks[0]

        # work in the task selected
        current_task.remaining_time -= self.productivity*general_settings.time_by_step/60

        # check if the task has finished
        if current_task.remaining_time <= 0:
            self.tasks.pop(0)
            current_task = None

    def addTask(self, task):
        self.tasks.append(task)
        self.total_tasks_number += 1

    def calculateEventStress(self):
        self.event_stress = min(1, len(self.tasks)/2/self.average_daily_tasks)

    def calculateTimePressure(self):
        total_tasks_remaining_time = sum(task.remaining_time for task in self.tasks)
        print("I am worker " + str(self.unique_id) + " and I have a total task duration of " + str(total_tasks_remaining_time))
        self.time_pressure = total_tasks_remaining_time/(total_tasks_remaining_time+self.model.timer.work_remaining_time)

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
