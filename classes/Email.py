import configuration.email_settings as settings

import math, random, numpy as np

class Email():

    def __init__(self):

        mu, sigma = settings.email_read_time_distribution_params
        self.read_time = math.floor(abs(np.random.normal(mu, sigma, 10)[random.randint(0,9)]))
