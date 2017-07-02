from mesa.visualization.ModularVisualization import VisualizationElement
import numpy as np

class StressHistogram(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["visualization/client/StressHistogram.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new StressHistogram({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        stress_vals = [worker.stress for worker in model.workers]
        hist = np.histogram(stress_vals, bins=self.bins)[0]
        return [int(x) for x in hist]
