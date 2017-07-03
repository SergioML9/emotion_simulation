class Room():

    def __init__(self, name, typeRoom, conectedTo, dx, dy, pos = (0,0)):

        self.name = name
        self.typeRoom = typeRoom
        self.conectedTo = conectedTo
        self.dx = dx
        self.dy = dy
        self.pos = pos
        self.roomsConected = []
        self.agentsInRoom = []
        self.walls = []
        self.entrance = None
        self.doors = []
        self.light = False
