from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

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

    def __init__(self, workers_number):

        #random.seed(3)

        # Model attributes initialization
        self.workers_number = workers_number
        self.agents = []
        self.workers = []
        self.average_stress = 0
        self.running = True

        # Schedule
        self.schedule = BaseScheduler(self)

        # Create timer agent
        self.timer = TimeAgent(len(self.agents), self)
        self.schedule.add(self.timer)
        self.agents.append(self.timer)

        # Create sensor agent
        self.sensor = SensorAgent(len(self.agents), self)
        self.schedule.add(self.sensor)
        self.agents.append(self.sensor)

        # Create workers agents
        for i in range(self.workers_number):
            worker = WorkerAgent(i+len(self.agents), self)
            self.schedule.add(worker)
            self.workers.append(worker)

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

    def step(self):
        self.schedule.step()

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
