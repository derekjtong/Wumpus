"""
Modified from wwagent.py written by Greg Scott

Modified to only do random motions so that this can be the base
for building various kinds of agent that work with the wwsim.py 
wumpus world simulation -----  dml Fordham 2019

# FACING KEY:
#    0 = up
#    1 = right
#    2 = down
#    3 = left

# Actions
# 'move' 'grab' 'shoot' 'left' right'

"""

from random import randint
from knowledge_base import *


# This is the class that represents an agent
class WWAgent:
    def __init__(self):
        self.max = 4  # number of cells in one side of square world
        self.stopTheAgent = False  # set to true to stop th agent at end of episode
        self.position = (0, 3)  # top is (0,0)
        self.directions = ["up", "right", "down", "left"]
        self.facing = "right"
        self.arrow = 1
        self.percepts = (None, None, None, None, None)
        self.map = [[self.percepts for i in range(self.max)] for j in range(self.max)]
        self.kb = KnowledgeBase()
        self.planned_destination = None
        print("New agent created")

    # Add the latest percepts to list of percepts received so far
    # This function is called by the wumpus simulation and will
    # update the sensory data. The sensor data is placed into a
    # map structured KB for later use

    def update(self, percept):
        self.percepts = percept
        # [stench, breeze, glitter, bump, scream]
        if self.position[0] in range(self.max) and self.position[1] in range(self.max):
            self.map[self.position[0]][self.position[1]] = self.percepts
        # puts the percept at the spot in the map where sensed

        # stench, tell kb about possible wumpus locations
        if "stench" in self.percepts:
            print(
                # f"Agent detected a stench at {self.position}, put wumpus in neighbors"
            )
            clause = []
            for dir in self.get_directions():
                if not clause:
                    clause.append(f"w{dir}")
                else:
                    clause.append([f"w{dir}", "or", [clause]])
            self.kb.tell(clause)
        else:
            # print(
            #     f"Agent detected a no stench at {self.position}, put no wumpus in neighbors"
            # )
            for dir in self.get_directions():
                self.kb.tell(["not", f"w{dir}"])

        # breeze, tell kb about possible pit locations
        if "breeze" in self.percepts:
            # print(f"Agent detected a breeze at {self.position}, put pits in neighbors")
            clause = []
            for dir in self.get_directions():
                if not clause:
                    clause.append(f"p{dir}")
                else:
                    clause.append([f"p{dir}", "or", [clause]])
            self.kb.tell(clause)
        else:
            # print(
            #     f"Agent detected a no breeze at {self.position}, put no pits in neighbors"
            # )
            for dir in self.get_directions():
                self.kb.tell(["not", f"p{dir}"])

        # not dead
        self.kb.tell(["not", f"w{self.position[0]}{self.position[1]}"])
        self.kb.tell(["not", f"p{self.position[0]}{self.position[1]}"])

    # Since there is no percept for location, the agent has to predict
    # what location it is in based on the direction it was facing
    # when it moved

    def calculateNextPosition(self, action):
        if self.facing == "up":
            self.position = (self.position[0], max(0, self.position[1] - 1))
        elif self.facing == "down":
            self.position = (self.position[0], min(self.max - 1, self.position[1] + 1))
        elif self.facing == "right":
            self.position = (min(self.max - 1, self.position[0] + 1), self.position[1])
        elif self.facing == "left":
            self.position = (max(0, self.position[0] - 1), self.position[1])
        return self.position

    # and the same is true for the direction the agent is facing, it also
    # needs to be calculated based on whether the agent turned left/right
    # and what direction it was facing when it did

    def calculateNextDirection(self, action):
        if self.facing == "up":
            if action == "left":
                self.facing = "left"
            else:
                self.facing = "right"
        elif self.facing == "down":
            if action == "left":
                self.facing = "right"
            else:
                self.facing = "left"
        elif self.facing == "right":
            if action == "left":
                self.facing = "up"
            else:
                self.facing = "down"
        elif self.facing == "left":
            if action == "left":
                self.facing = "down"
            else:
                self.facing = "up"

    # this is the function that will pick the next action of
    # the agent. This is the main function that needs to be
    # modified when you design your new intelligent agent
    # right now it is just a random choice agent

    def action(self):
        # test for controlled exit at end of successful gui episode
        if self.stopTheAgent:
            print("Agent has won this episode.")
            return "exit"  # will cause the episide to end

        # reflect action -- get the gold!
        if "glitter" in self.percepts:
            print("Agent will grab the gold!")
            self.stopTheAgent = True
            return "grab"

        if not self.planned_destination or self.planned_destination == self.position:
            possible_moves = []
            possible_dirs = self.get_directions()
            if not possible_dirs:
                print("No possible move")
                return
            for dir in self.get_directions():
                if self.kb.ask([["not", f"w{dir}"], "and", ["not", f"p{dir}"]]):
                    possible_moves.append(dir)

            print("possible_moves=", possible_moves)
            if not possible_moves:
                # No 100% safe move
                print("No safe move")
                return
            else:
                # Get random move
                move = possible_moves[randint(0, len(possible_moves) - 1)]
                self.planned_destination = (int(move[0]), int(move[1]))
                print("setting planned action to", self.planned_destination)

        # move towards planned destination
        if self.planned_destination[0] == self.position[0]:
            # vertical move
            if self.planned_destination[1] < self.position[1]:
                goal_face = "up"
            else:
                goal_face = "down"
        else:
            if self.planned_destination[0] > self.position[0]:
                goal_face = "right"
            else:
                goal_face = "left"

        if goal_face == self.facing:
            action = "move"
            self.calculateNextPosition(action)
        else:
            action = "left"
            self.calculateNextDirection(action)

        print("planned action:", action)
        return action

    def get_directions(self):
        dirs = [0, 1, 0, -1, 0]
        surroundings = []
        for k in range(4):
            new_x = self.position[0] + dirs[k]
            new_y = self.position[1] + dirs[k + 1]
            if new_x >= 0 and new_x < self.max and new_y >= 0 and new_y < self.max:
                surroundings.append(f"{new_x}{new_y}")
        return surroundings
