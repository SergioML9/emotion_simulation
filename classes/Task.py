import configuration.workload_settings as settings

class Task():

    def __init__(self):

        # Task attributes
        self.estimated_time = settings.task_estimated_time
        self.remaining_time = self.estimated_time
