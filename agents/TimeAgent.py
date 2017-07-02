from mesa import Agent

import configuration.general_settings as settings
import configuration.occupancy_settings as occupancy_settings
import math
import datetime

class TimeAgent(Agent):

    def __init__(self, timer_id, model):
        super().__init__(timer_id, model)

        # Agent attributes initialization
        self.step_counter = 0
        self.time_by_step = settings.time_by_step
        self.clock = datetime.time(8, 00)
        self.days = 1
        self.hours = self.clock.hour
        self.minutes = self.clock.minute
        self.seconds = self.clock.second-self.time_by_step
        self.new_day = False
        self.new_hour = False
        self.day_interval = 'free_time'
        self.work_remaining_time = 0
        self.worked_time = 0

    def step(self):

        # Step counter
        self.step_counter += 1

        # Calculate time
        self.new_day = False
        self.new_hour = False

        self.seconds = self.seconds + self.time_by_step
        if self.seconds > 59:
            self.minutes = self.minutes + math.floor(self.seconds/60)
            self.seconds = 0
            if self.minutes > 59:
                self.hours = self.hours + math.floor(self.minutes/60)
                self.minutes = 0
                self.new_hour = True
                if self.hours > 23:
                    self.days = self.days + math.floor(self.hours/24)
                    self.hours = 0

        self.clock = datetime.time(self.hours,self.minutes)

        # Check if it is new work day
        if occupancy_settings.workersTiming['arrival_time'] == self.clock:
            self.new_day = True
            self.worked_time = 0

        # Get day interval
        self.getDayInterval()

        print('Day: ', (self.days), ' - Hour: ', self.clock)

        # Calculate remaining time
        self.calculateWorkRemainingTime()

    def getDayInterval(self):
        is_work_time = occupancy_settings.workersTiming['arrival_time'] <= self.clock < occupancy_settings.workersTiming['leaving_time']
        is_overtime = occupancy_settings.workersTiming['leaving_time'] <= self.clock < occupancy_settings.workersTiming['overtime_limit']
        is_sleep_time = occupancy_settings.workersTiming['sleep_start'] <= self.clock < occupancy_settings.workersTiming['sleep_end']

        if is_work_time:
            self.day_interval = 'work_time'
            self.worked_time += 1
        elif is_overtime: self.day_interval = 'overtime'
        elif is_sleep_time: self.day_interval = 'sleep_time'
        else: self.day_interval = 'free_time'

    def calculateWorkRemainingTime(self):
        if self.day_interval == 'work_time':
            remaining_hours = occupancy_settings.workersTiming['leaving_time'].hour-self.hours-1
            remaining_minutes = occupancy_settings.workersTiming['leaving_time'].minute+60-self.minutes if (remaining_hours <= 0 and occupancy_settings.workersTiming['leaving_time'].minute>0) else 60-self.minutes
            self.work_remaining_time = remaining_hours * 60 + remaining_minutes
        else: self.work_remaining_time = 0

        #print("Work remaining time: " + str(self.work_remaining_time))
