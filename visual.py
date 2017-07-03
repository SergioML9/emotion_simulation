from mesa.visualization.ModularVisualization import ModularServer
from model.SOMENModel import SOMENModel
from visualization.drawModelBack import MapVisualization
from visualization.drawModelBack import GraphVisualization

def occupancyVisualization(agent):
    
    json = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "blue",
                 "r": 0.5}
    return json


mapVisualization = MapVisualization(occupancyVisualization, 6, 6, 600, 600)

graphVisualization = GraphVisualization()

server = ModularServer(SOMENModel,
                       [mapVisualization, graphVisualization],
                       "SOMEN Model",
                       10, 10)

server.port = 8882
server.launch()