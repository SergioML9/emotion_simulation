from transitions import Machine
from mesa import Agent, Model
from transitions import State
import configuration.settings

class Light(Agent):

    states = [
        State(name='off', on_enter=['set_off']),
        State(name='medium', on_enter=['set_medium']),
        State(name='high', on_enter=['set_high'])
        ]

    def __init__(self, unique_id, model, room):
        super().__init__(unique_id, model)

        self.room = room
        #self.wait_off = int(configuration.settings.time_to_off_light * 60 * 100 /configuration.settings.time_by_step)
        
        self.machine = Machine(model=self, states=Light.states, initial='off')
        self.machine.add_transition('switch_on', '*', 'on')
        self.machine.add_transition('switch_medium', '*', 'medium')
        self.machine.add_transition('switch_high', '*', 'high')

    def sensorCheck(self):

        pass

        '''
        #Comportamiento inteligente

        userInRoom = self.model.ThereIsSomeOccupantInRoom(self.room)
        if userInRoom == True:
            if self.state == 'on':
                pass
            else:
                self.switch_on()
        else:
            if self.state == 'on':
                if self.wait_off > 0:
                    self.wait_off = self.wait_off - 1
                else:
                    self.switch_off()
                    self.wait_off = int(configuration.settings.time_to_off_light * 60 * 100 /configuration.settings.time_by_step)
            else:
                pass
        '''

    def regularBehaviour(self):
        pass

    def step(self):
        pass
        #print('light: ', self.unique_id, self.state, self.room.name)
        '''
        if (comportamientoInteligenteOn):
            self.sensorCheck()
        else:
            self.regularBehaviour()
        '''

    #Metodos de entrada y salida de los estados
    def set_off(self):
        pass

    def set_medium(self):
        pass

    def set_high(self):
        pass
