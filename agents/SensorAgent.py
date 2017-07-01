from mesa import Agent

import pandas as pd
import math
import random
import configuration.general_settings as general_settings

class SensorAgent(Agent):

    def __init__(self, sensor_id, model):
        super().__init__(sensor_id, model)

        self.temperature_data = pd.read_csv('data/temperature_data.csv')
        self.temperature = 22.0
        self.humidity = 55.0
        self.luminosity = 500
        self.noise = 55

    def step(self):
        #self.temperature = self.temperature_data[self.temperature_data['day'] == self.model.timer.days%29][self.temperature_data['hour'] == self.model.timer.clock].at[0, 'temp']
        #print(self.model.timer.days)
        #print(self.model.timer.clock)
        self.temperature = self.temperature_data[self.temperature_data['day'] == self.model.timer.days%30][self.temperature_data['hour'] == '' + str(self.model.timer.hours).zfill(2) + ':00'].iloc[0]['temp']
        self.humidity = self.temperature_data[self.temperature_data['day'] == self.model.timer.days%30][self.temperature_data['hour'] == '' + str(self.model.timer.hours).zfill(2) + ':00'].iloc[0]['humidity']
        self.wbgt = 0.567*self.temperature+0.393*(6.105*self.humidity/100*pow(math.e, (17.27*self.temperature/(237.7+self.temperature)))) + 3.94

        # noise
        if random.choice([True, False]): self.noise += (1+self.model.average_stress)*2/general_settings.time_by_step*self.model.workers_number
        else: self.noise -= 2/general_settings.time_by_step*self.model.workers_number*(1+self.model.average_stress)

        if random.choice([True, False]): self.luminosity += 20/general_settings.time_by_step
        else: self.noise -= 20/general_settings.time_by_step


        print(self.luminosity)
