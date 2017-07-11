from transitions import Machine
from mesa import Agent, Model
from transitions import State
import configuration.settings
import model.ramenScript

class Light(Agent):

    states = [
        State(name='off', on_enter=['set_off']),
        State(name='low', on_enter=['set_low']),
        State(name='medium', on_enter=['set_medium']),
        State(name='high', on_enter=['set_high'])
        ]

    def __init__(self, unique_id, model, room):
        super().__init__(unique_id, model)

        self.room = room
        self.wait_off = 15
        self.luminosity = 500

        self.machine = Machine(model=self, states=Light.states, initial='off')
        self.machine.add_transition('switch_off', '*', 'off')
        self.machine.add_transition('switch_low', '*', 'low')
        self.machine.add_transition('switch_medium', '*', 'medium')
        self.machine.add_transition('switch_high', '*', 'high')

    def sensorCheck(self):
        userInRoom = self.model.ThereIsSomeOccupantInRoom(self.room)
        if userInRoom == True:
            if 450 > self.luminosity:
                self.switch_low()
            elif 750 > self.luminosity > 450:
                self.switch_medium()
            else:
                self.switch_high()
        else:
            if self.state != 'off':
                if self.wait_off > 0:
                    self.wait_off = self.wait_off - 1
                else:
                    self.switch_off()
                    self.wait_off = 3
            else:
                pass

    def regularBehaviour(self):
        pass

    def step(self):
        #print('light: ', self.unique_id, self.state, self.room.name)
        self.sensorCheck()

    #Metodos de entrada y salida de los estados
    def set_off(self):
        model.ramenScript.addLightState(self.room, 'low', self.model.NStep)

    def set_low(self):
        model.ramenScript.addLightState(self.room, 'medium', self.model.NStep)

    def set_medium(self):
        model.ramenScript.addLightState(self.room, 'medium', self.model.NStep)

    def set_high(self):
        model.ramenScript.addLightState(self.room, 'high', self.model.NStep)
