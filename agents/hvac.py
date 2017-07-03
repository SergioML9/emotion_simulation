from mesa import Agent, Model
from transitions import Machine
from transitions import State
import json
import math
import configuration.settings

class HVAC(Agent):

	states = [
		State(name='off', on_enter=['set_off']),
		State(name='on', on_enter=['set_on'])
		]

	def __init__(self, unique_id, model, thermalZone):
		super().__init__(unique_id, model)

		self.machine = Machine(model=self, states=HVAC.states, initial='off')
		self.machine.add_transition('turn_on', '*', 'on')
		self.machine.add_transition('turn_off', '*', 'off')

		#init
		self.time = configuration.settings.time_by_step
		self.thermalZone = thermalZone

		self.power = self.setPower()*1.25
		self.consumeOn = self.power*configuration.settings.consume_hvac_on*0.8
		self.getComfortValues =  int(configuration.settings.timeGetComfortValues*60/configuration.settings.time_by_step)
		self.desiredTemperature = 0
		if self.thermalZone.season == 'summer':
			self.desiredTemperature = configuration.settings.temperatureSummerIn
		else:
			self.desiredTemperature = configuration.settings.temperatureWinterIn
		if (self.thermalZone.rooms[0].typeRoom == 'hall') or (self.thermalZone.rooms[0].typeRoom == 'corridor'):
			self.desiredTemperature = configuration.settings.temperatureSummerInCorridors
		self.fangerValue = 0
		self.comfortMedium = 0
		self.updateTcomfort = int((configuration.settings.timeGetTComfort*60)/self.time)
		
		#Control
		self.lastStep = 0
		self.working = False
		self.thermalZoneWithoutPeople = (configuration.settings.timeToReduceTemperatureThermalZoneWithoutPeople*60*100)/(configuration.settings.time_by_step)
		self.justEnterPeople = False
		self.initPeople = True

	def setPower(self):
		if self.thermalZone.season == 'summer':
			valueHigher = 0
			for value in configuration.settings.temperatureSummerOut:
				if value > valueHigher:
					valueHigher = value
			self.model.clock.hour = configuration.settings.temperatureSummerOut.index(valueHigher)
		else:
			valueLower = 0
			for value in configuration.settings.temperatureSummerOut:
				if valueLower > value:
					valueLower = value
			self.model.clock.hour = configuration.settings.temperatureSummerOut.index(valueLower)
		self.thermalZone.getMaximunQ(self.model)
		power = self.thermalZone.Qtotal
		self.thermalZone.Qtotal = 0
		self.model.clock.hour = 0
		return power

	def getFangerValue(self):
		Ta = self.thermalZone.temperature
		HR = configuration.settings.humiditySummerIn*100
		fh = 0.0084 #0.0080 invierno
		fr = 0.1300 #0.1 invierno
		Tr = Ta + 1 #-1 invierno
		IVM0Array = [-1.49, -1.24, -1, -0.74, -0.48, -0.26, 0.04, 0.3, 0.56, 0.82, 1.09, 1.36, 1.62, 1.86, 2.17] #[-1.42, -1.26, -1.03, -0.84, -0.64, -0.45, -0.25, -0.05, 0.16, 0.365, 0.57, 0.78, 0.99, 1.12, 1.40] invierno , de 18 a 32 grados en verano y de 14 a 28 en invierno
		IVM0 = -3
		if(Ta>32):
			 IVM0 = 3
		elif(Ta<18):
			 pass
		else:
			IVM0 = IVM0Array[int(math.floor(Ta-18+0.5))]
		IVM = IVM0 + fh*(HR-50) + fr*(Tr-Ta)
		#IVMValues = [-3, -2.7, -2.4, -2.1, -1.8, -1.5, -1.2, -0.9, -0.6, -0.3, 0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3]
		#PerUnsatisfied = [100, 95, 90, 80, 67, 50, 35, 22, 12, 7, 5, 7, 12, 22, 35, 50, 67, 80, 90, 95, 100]
		PerUnsatisfied =(100-(95*math.exp(-0.03353*math.pow(IVM,4)-0.2179*math.pow(IVM,2))))
		'''
		pos = 0
		preValue = -10
		satisfaction = 0
		for value in IVMValues:
			if value > IVM and IVM > preValue:
				satisfaction = 100 - PerUnsatisfied #PerUnsatisfied[IVMValues.index(value)]
				break
			else:
				preValue = value
		'''
		satisfaction =  100 - PerUnsatisfied
		self.fangerValue = satisfaction
		self.fangerValuesByTime = [self.model.NStep*configuration.settings.time_by_step, satisfaction]

	def getComfort(self, TComfAgent, Tin):
	    C = 0
	    T = Tin
	    diffAux = T - TComfAgent
	    if diffAux < 0:
	        T = TComfAgent - diffAux
	    diff = math.fabs(T - TComfAgent)
	    if(2>=diff):
	        C = 100-10*math.pow((T-TComfAgent)/1.5, 2)
	    elif(diff>2 and 4>=diff):
	        m = -(82-50)/(4-2)
	        x0 = (TComfAgent+2)-(82/m)
	        C = m*(T-x0)
	    else:
	        x0 = math.log(50) + (TComfAgent+4)
	        C = math.pow(math.e, x0-T)
	        C = float(int(C))
	    return C

	def getTComfort(self):
		tComfort = []
		for room in self.thermalZone.rooms:
			for agent in room.agentsInRoom:
				tComfort.append(agent.TComfort)
		if len(tComfort) < 1:
			if self.thermalZone.season == 'summer':
				tComfort.append(configuration.settings.temperatureSummerIn)
			else:
				tComfort.append(configuration.settings.temperatureWinterIn)
		Tmin = 0
		Tmax = 0
		if self.thermalZone.season == 'summer':
			Tmin = configuration.settings.TminSummer
			Tmax = configuration.settings.TmaxSummer
		else:
			Tmin = configuration.settings.TminWinter
			Tmax = configuration.settings.TmaxWinter
		cases = {}
		n = 0
		Taux = Tmin
		while(Taux < Tmax):
			Ctotal = 0
			n1 = 0
			n2 = 0
			n3 = 0
			n4 = 0
			n5 = 0
			for t in tComfort:
				C = self.getComfort(t, (int(Taux*100)/100))
				Ctotal = Ctotal + C
				if C >= 90:
					n1 = n1 + 1
				elif C >= 75:
					n2 = n2 + 1
				elif C >= 60:
					n3 = n3 + 1
				elif C >= 50:
					n4 = n4 + 1
				else:
					n5 = n5 + 1
			Cm = Ctotal / len(tComfort)
			cases[n] = [Taux, Cm, n1, n2, n3, n4, n5]
			n = n +1
			Taux = Taux + 0.01

		Tgood = 0
		cmAux = 0
		n1Aux = 0
		n2Aux = 0
		n3Aux = 0
		n4Aux = 100
		n5Aux = 100
		for n in range(0, n):
			values = cases[n]
			if values[6] < n5Aux:
				n5Aux = values[6]
				n4Aux = values[5]
				n3Aux = values[4]
				n2Aux = values[3]
				n1Aux = values[2]
				cmAux = values[1]
				Tgood = values[0]
			elif values[6] == n5Aux:
				if values[5] < n4Aux:
					n5Aux = values[6]
					n4Aux = values[5]
					n3Aux = values[4]
					n2Aux = values[3]
					n1Aux = values[2]
					cmAux = values[1]
					Tgood = values[0]
				elif values[5] == n4Aux:
					if values[2] > n1Aux:
						n5Aux = values[6]
						n4Aux = values[5]
						n3Aux = values[4]
						n2Aux = values[3]
						n1Aux = values[2]
						cmAux = values[1]
						Tgood = values[0]
					elif values[2] == n1Aux:
						if values[3] > n2Aux:
							n5Aux = values[6]
							n4Aux = values[5]
							n3Aux = values[4]
							n2Aux = values[3]
							n1Aux = values[2]
							cmAux = values[1]
							Tgood = values[0]
						elif values[3] == n2Aux:
							if values[4] > n3Aux:
								n5Aux = values[6]
								n4Aux = values[5]
								n3Aux = values[4]
								n2Aux = values[3]
								n1Aux = values[2]
								cmAux = values[1]
								Tgood = values[0]
							elif values[4] == n3Aux:
								if values[1] > cmAux:
									n5Aux = values[6]
									n4Aux = values[5]
									n3Aux = values[4]
									n2Aux = values[3]
									n1Aux = values[2]
									cmAux = values[1]
									Tgood = values[0]
								else:
									pass
							else:
								pass
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		Tgood1 = math.floor(10*(Tgood+0.05))/10
		Taux = Tgood1
		change = 0
		while(Taux < Tgood1+(configuration.settings.var/2 + 0.01)):
			for t in tComfort:
				C = self.getComfort(t, (int(Taux*100)/100))
				Ctotal = Ctotal + C
				if C<60:
					change = change + 0.01
					break
			Taux = Taux + 0.01
		Tgood2 = math.floor(10*(Tgood1+0.05 - change))/10
		Taux = Tgood2
		change = 0
		while(Taux > Tgood2-(configuration.settings.var/2 + 0.01)):
			for t in tComfort:
				C = self.getComfort(t, (int(Taux*100)/100))
				Ctotal = Ctotal + C
				if C<60:
					change = change + 0.01
					break
			Taux = Taux - 0.01
		TFinal =  math.floor(10*(Tgood2 + 0.05 + change))/10
		self.desiredTemperature = TFinal

	def set_off(self):
		pass

	def set_on(self):
		pass

	def set_standby(self):
		pass

	def step(self):
		if (self.working == True):
			if self.model.modelWay == 2 and self.initPeople == True:
				for room in self.thermalZone.rooms:
					if self.model.ThereIsSomeOccupantInRoom(room) == True:
						self.initPeople == False 
			if self.state == 'on':
				self.thermalZone.QHVAC = self.thermalZone.QHVAC + (self.power * (configuration.settings.time_by_step/3600))
				if(self.thermalZone.rooms[0].typeRoom != 'hall' or self.thermalZone.rooms[0].typeRoom != 'class' or self.thermalZone.rooms[0].typeRoom != 'corridor'):
					self.model.consumeEnergy(self)
			if self.getComfortValues == 0:
				self.getFangerValue()
				comfortAux = 0
				NAgentsAux = 0
				for room in self.thermalZone.rooms:
					for agent in room.agentsInRoom:
						agent.comfort = self.getComfort(agent.TComfort, self.thermalZone.temperature)
						comfortAux = comfortAux + agent.comfort
					NAgentsAux = NAgentsAux + len(room.agentsInRoom)
				if NAgentsAux != 0:
					comfortMedium = comfortAux /(NAgentsAux)
				else:
					comfortMedium = 0
				self.comfortMedium = comfortMedium 
				self.getComfortValues = int(configuration.settings.timeGetComfortValues*60/configuration.settings.time_by_step)
			else:
				self.getComfortValues = self.getComfortValues - 1
			if self.model.modelWay != 0:
				thereIsAgent = False
				for room in self.thermalZone.rooms:
					if len(room.agentsInRoom) > 0:
						thereIsAgent = True
						self.thermalZoneWithoutPeople = (configuration.settings.timeToReduceTemperatureThermalZoneWithoutPeople*60*100)/(configuration.settings.time_by_step)
						#self.thermalZoneWithoutPeopleSetOff = (configuration.settings.timeToSetOffThermalZoneWithoutPeople)/(configuration.settings.time_by_step/60)
				if thereIsAgent == False:
					self.justEnterPeople = True
					if self.thermalZoneWithoutPeople == 0:
						if self.thermalZone.season == 'summer':
							self.desiredTemperature = configuration.settings.temperatureSummerInWithoutPeople
						else:
							self.desiredTemperature = configuration.settings.temperatureWinterInWithoutPeople
						self.thermalZoneWithoutPeople = (configuration.settings.timeToReduceTemperatureThermalZoneWithoutPeople*60*100)/(configuration.settings.time_by_step)
					else:
						self.thermalZoneWithoutPeople = self.thermalZoneWithoutPeople - 1
					if(self.model.modelWay == 2 and self.initPeople == True):
						self.desiredTemperature = configuration.settings.temperatureSummerIn
				else:
					if self.model.modelWay == 2 and self.thermalZone.rooms[0].typeRoom != 'hall' and self.thermalZone.rooms[0].typeRoom != 'corridor':
						if self.updateTcomfort == 0 or self.justEnterPeople == True:
							self.justEnterPeople = False
							self.getTComfort()
							self.updateTcomfort = int((configuration.settings.timeGetTComfort*60)/configuration.settings.time_by_step)
						else:
							self.updateTcomfort = self.updateTcomfort - 1
					else:
						if self.thermalZone.season == 'summer' and self.thermalZone.rooms[0].typeRoom != 'hall' and self.thermalZone.rooms[0].typeRoom != 'corridor':
							self.desiredTemperature = configuration.settings.temperatureSummerIn
						else:
							self.desiredTemperature = configuration.settings.temperatureSummerInCorridors
			if self.thermalZone.season == 'summer':
				if self.thermalZone.temperature > (self.desiredTemperature + configuration.settings.var):
					self.turn_on()
				elif (self.desiredTemperature - configuration.settings.var) > self.thermalZone.temperature:
					self.turn_off()
			else:
				if(self.thermalZone.temperature > (self.desiredTemperature + configuration.settings.var)):
					self.turn_off()
				elif(self.desiredTemperature - configuration.settings.var) > self.thermalZone.temperature:
					self.turn_on()
		else:
			if self.state == 'on':
				self.turn_off()