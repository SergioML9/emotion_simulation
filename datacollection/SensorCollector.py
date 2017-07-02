from mesa.datacollection import DataCollector

class SensorCollector(DataCollector):

    def collect(self, model):
        """ Collect all the data for the given model object. """
        if self.model_reporters:
            for var, reporter in self.model_reporters.items():
                self.model_vars[var].append(reporter(model))

        if self.agent_reporters:
            for var, reporter in self.agent_reporters.items():
                agent_records = []
                agent_records.append((model.sensor.unique_id, reporter(model.sensor)))
                self.agent_vars[var].append(agent_records)
