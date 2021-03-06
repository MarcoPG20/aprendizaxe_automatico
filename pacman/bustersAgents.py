# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from os import wait
from turtle import delay
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

import time

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP


    ##### Codigo extra - Funcion extra #####

    # Funcion que encuentra el fantasma mas cercano
    def closer_ghost(self,gameState):
        # Obtenemos las distancias de los fantasmas.
        ghost_dist = gameState.data.ghostDistances
        # Miramos cual es el fantasma mas cercano.
        dists = [d for d,l in zip(ghost_dist,gameState.getLivingGhosts()[1:]) if l]
        closer_ghost_dist = min(dists)
        closer_ghost = ghost_dist.index(closer_ghost_dist)
        # Nos quedamos con la posicion del fantasma mas cercano.
        closer_ghost_pos = gameState.getGhostPositions()[closer_ghost]

        return closer_ghost_pos




    # Posicion relativa del fantasma mas cercano
    def closer_ghost_relat_dist(self,gameState):

        # Nos quedamos con la posicion del fantasma mas cercano.
        closer_ghost_pos = self.closer_ghost(gameState)
        # Obtenemos la posicion de pacman.
        pacman_pos = gameState.getPacmanPosition()

        # Posicion del fantasma respecto a pacman.
        pos = (closer_ghost_pos[0] - pacman_pos[0], closer_ghost_pos[1] - pacman_pos[1])

        return pos


    def muro_x(self, gameState):

        muro_x = False
        pacman_x = gameState.getPacmanPosition()[0]
        pacman_y = gameState.getPacmanPosition()[1]
        fantasma_x = self.closer_ghost(gameState)[0]

        for i in range(pacman_x,fantasma_x,-1 if (fantasma_x < pacman_x) else 1):
            muro_x = gameState.getWalls()[i][pacman_y]

            if muro_x:
                return True

        if not muro_x:
            return False



        #if not muro_x and not muro_y:
        #   return False

    def muro_y(self, gameState):

        muro_y = False
        pacman_x = gameState.getPacmanPosition()[0]
        pacman_y = gameState.getPacmanPosition()[1]
        fantasma_y = self.closer_ghost(gameState)[1]

        for i in range(pacman_y,fantasma_y,-1 if (fantasma_y < pacman_y) else 1):
            muro_y = gameState.getWalls()[pacman_x][i]

            if muro_y:
                return True

        if not muro_y:
            return False




        
    # Guardamos en un fichero la informacion que consideramos importante.
    def printLineData(self, gameState, fichero, cabeceras, puntuacion_anterior):
        
        if not cabeceras:

            fichero.write("@relation pacman.pract1\n")
            fichero.write("\n@attribute pacman_x numeric")
            fichero.write("\n@attribute pacman_y numeric")
            fichero.write("\n@attribute num_fantasmas numeric")

            for i in range(1,len(gameState.getLivingGhosts())):
                # Usamos getLivingGhosts() para saber la cantidad de fantasmas.
                fichero.write("\n@attribute fantasma" + str(i) + "_x numeric")
                fichero.write("\n@attribute fantasma" + str(i) + "_y numeric")

            for i in range(1,len(gameState.getLivingGhosts())):
                fichero.write("\n@attribute fantasma" + str(i) + "_vivo {True,False}")

            fichero.write("\n@attribute fantasma_cercano_x numeric")
            fichero.write("\n@attribute fantasma_cercano_y numeric")
            # Anadido en la practica 1
            fichero.write("\n@attribute muro_x {True,False}") 
            fichero.write("\n@attribute muro_y {True,False}")
            # Anadido en la practica 1
            fichero.write("\n@attribute dif_puntuacion numeric")
            fichero.write("\n@attribute direccion_pacman {West, Stop, East, North, South}\n")

            fichero.write("\n@data\n")


        dif_puntuacion = int(gameState.getScore()) - int(puntuacion_anterior)

        data = ""
        # Definimos los datos que vamos a guardar.
        data += str(gameState.getPacmanPosition()[0]) # PacMan x
        data += ", " + str(gameState.getPacmanPosition()[1]) # PacMan y

        data += ", " + str(len(gameState.getGhostPositions())) # Numero de fantasmas
 
        for f in gameState.getGhostPositions():

            
            data += ", " + str(f[0]) # Fantasma x
            data += ", " + str(f[1]) # Fantasma y

        for i in range(1,len(gameState.getLivingGhosts())):
            data += ", " + str(gameState.getLivingGhosts()[i]) # Fantasma vivo

        data += ", " + str(self.closer_ghost_relat_dist(gameState)[0]) # Fantasma mais cercano x   
        data += ", " + str(self.closer_ghost_relat_dist(gameState)[1]) # Fantasma mais cercano y

        data += ", " + str(self.muro_x(gameState)) # Existencia de muro en el eje x
        data += ", " + str(self.muro_y(gameState)) # Existencia de muro en el eje y

        data += ", " + str(dif_puntuacion) # Diferencia de puntacion entre el tick actual y pasado

        data += ", " + str(gameState.data.agentStates[0].getDirection()) # Direccion que toma pacman

        # escribimos los datos en fichero.
        fichero.write(str(data) + "\n")


class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------"
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Map:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()
        
        
    def chooseAction_old(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman

        position = self.closer_ghost_relat_dist(gameState)
        print("posicion fantasma",position)
        x = position[0]
        y = position[1]

        move = self.evaluar_x(x,legal)
        if move == -1:
            move = self.evaluar_y(y,legal)
        if move == -1:
            dirs = [Directions.WEST,Directions.EAST,Directions.NORTH,Directions.SOUTH]
            self.bloqueado = True
            while (move==-1):
                rand = random.randint(0, 3)
                if dirs[rand] in legal:
                    move = dirs[rand]

        print("Movimiento:",move)
        return move


    def evaluar_x(self,x,legal):
        print("distancia x:",x)
        if x == 0:
            move = -1
        if x > 0:
            if   Directions.EAST in legal: move = Directions.EAST
            else: move = -1
        if x < 0:
            if   Directions.WEST in legal:  move = Directions.WEST
            else: move = -1
        return move


    def evaluar_y(self,y,legal):
        print("distancia y:",y)
        if y == 0:
            move = -1
        if y > 0:
            if   Directions.NORTH in legal:   move = Directions.NORTH
            else: move = -1
        if y < 0:
            if   Directions.SOUTH in legal: move = Directions.SOUTH
            else: move = -1
        return move
