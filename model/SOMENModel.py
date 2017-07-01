from mesa import Model
from mesa.time import BaseScheduler

from agents.WorkerAgent import WorkerAgent
from agents.TimeAgent import TimeAgent
from classes.Task import Task

import configuration.workload_settings as workload_settings
import configuration.email_settings as email_settings

import numpy as np
import math
import random

# somen
# Simulation Of Multiagent emotional Environments

class SOMENModel(Model):

    def __init__(self, workers_number):

        # Model attributes initialization
        self.workers_number = workers_number
        self.agents = []
        self.workers = []

        # Schedule
        self.schedule = BaseScheduler(self)

        # Create timer agent
        self.timer = TimeAgent(len(self.agents), self)
        self.schedule.add(self.timer)
        self.agents.append(self.timer)

        # Create workers agents
        for i in range(self.workers_number):
            worker = WorkerAgent(i+len(self.agents), self)
            self.schedule.add(worker)
            self.workers.append(worker)

    def step(self):
        self.schedule.step()
        
        if self.timer.new_day:
            self.addTasks()
            self.createEmailsDistribution()


    def addTasks(self):
        ''' Add tasks to workers '''

        # Get task distribution params
        mu, sigma = workload_settings.tasks_arriving_distribution_params
        tasks_arriving_distribution = np.random.normal(mu, sigma, self.workers_number*10)

        for worker in self.workers:

            # Get number of tasks to add
            tasks_number = math.floor(abs(tasks_arriving_distribution [random.randint(0, 10*self.workers_number-1)]))

            # Add tasks
            for i in range(tasks_number):
                worker.addTask(Task())

            worker.calculateAverageDailyTasks(self.timer.days)
            worker.calculateEventStress()

            # worker.printTasksNumber()
            # worker.printAverageDailyTasks()
            worker.printEventStress()

    def createEmailsDistribution(self):
        '''Create emails distribution'''
        # Get emails distribution
        mu, sigma = email_settings.emails_read_distribution_params
        emails_read_distribution = np.random.normal(mu, sigma, self.workers_number*10)

        for worker in self.workers:

            emails_received = math.floor(abs(emails_read_distribution[random.randint(0, 10*self.workers_number-1)]))
            emails_distribution_over_time = np.random.choice([0, 1], size=(480,), p=[(480-emails_received)/480, emails_received/480])
            worker.email_read_distribution_over_time = emails_distribution_over_time
            #print("Should have " + str(emails_received) + " and I have " + str(np.sum(emails_distribution_over_time == 1)))
