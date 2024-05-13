# Derek Tong
# Professor Lyons
# CISC 6525 Artificial Intelligence
# May 9, 2024
#
# Wumpus World - Agent Implementation
# See KnowledgeBase class at bottom

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


class WWAgent:
    def __init__(self):
        self.max = 4  # number of cells in one side of square world
        self.stopTheAgent = False  # set to true to stop the agent at end of episode
        self.position = (0, 3)  # top is (0,0)
        self.directions = ["up", "right", "down", "left"]
        self.facing = "right"
        self.arrow = 1
        self.percepts = (None, None, None, None, None)
        self.map = [[self.percepts for i in range(self.max)] for j in range(self.max)]

        # KnowledgeBase object, see bottom
        self.kb = KnowledgeBase()

        self.planned_destination = None
        self.visited = dict()
        print("New agent created")

    def update(self, percept):
        self.percepts = percept
        # [stench, breeze, glitter, bump, scream]
        if self.position[0] in range(self.max) and self.position[1] in range(self.max):
            self.map[self.position[0]][self.position[1]] = self.percepts
        # puts the percept at the spot in the map where sensed

        # stench, tell kb about possible wumpus locations
        if "stench" in self.percepts:
            # print(
            # f"Agent detected a stench at {self.position}, put wumpus in neighbors"
            # )
            clause = []
            for dir in self.get_directions():
                if not clause:
                    clause = ["w{dir}"]
                else:
                    clause = [f"w{dir}", "or", [clause]]
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
                    clause = ["p{dir}"]
                else:
                    clause = [f"p{dir}", "or", [clause]]
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

        if self.position in self.visited:
            self.visited[self.position] += 1
        else:
            self.visited[self.position] = 1

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

        if self.visited[self.position] > 100:
            print("Exceeded limit, unsolvable")
            print("Visisted:", self.visited)
            return "exit"

        if not self.planned_destination or self.planned_destination == self.position:
            possible_moves = []
            possible_dirs = self.get_directions()
            if not possible_dirs:
                print("No possible move")
                return
            for dir in self.get_directions():
                prob = self.kb.ask([["not", f"w{dir}"], "and", ["not", f"p{dir}"]])
                pos_tuple = (int(dir[0]), int(dir[1]))
                visits = self.visited.get(pos_tuple, 0)
                # adjust probability based on visits, less visited = more likely to choose
                adjusted_prob = prob * (1 / (1 + visits / 10))
                possible_moves.append((adjusted_prob, pos_tuple))

            if not possible_moves:
                # No 100% safe move
                print("No safe move")
                return "exit"
            else:
                # Sort possible moves based on probability of safety (highest first)
                possible_moves.sort(reverse=True, key=lambda x: x[0])
                print(
                    "Sorted possible moves based on safety probability:", possible_moves
                )
                prob, move = possible_moves[0]
                self.planned_destination = (int(move[0]), int(move[1]))
                # print("setting planned action to", self.planned_destination)

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

        # print("planned action:", action)
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


class KnowledgeBase:
    def __init__(self):
        self.kb = []

        # Use seen clauses rather than searching kb due to recursion problems
        self.seen_clauses = []

        # Tracks symbols in kb so tt_entails does not have to recalculate
        self.cached_symobls = []

        # Visual indicator for model checking progress
        self.progress_bar = 0
        self.expected_maximum_checks = 1000000

    def tell(self, clause):
        """Add a clause in propositional logic to the KB."""
        if clause in self.seen_clauses:
            return
        else:
            self.seen_clauses.append(clause)
        if not self.kb:
            self.kb.append(clause)
        else:
            self.kb = [clause, "and"] + [self.kb]
        self.cached_symobls = self.get_symbols(self.kb)

    def ask(self, alpha):
        """Query the KB to see if alpha is entailed by the KB."""
        self.progress_bar = 0
        print("\rAsking", alpha)
        result = self.tt_entails(self.kb, alpha)
        print(f"\n")
        return result

    def tt_entails(self, kb, alpha):
        """Check all models to determine if kb entails alpha."""
        symbols = self.cached_symobls + self.get_symbols(alpha)
        # print("--------- all truth tables ---------")
        # self.tt_enumerate(symbols, [])
        # print("---------   check tables   ---------")
        true_counts, total_counts = self.tt_check_all(symbols, [], kb, alpha)
        if total_counts == 0:
            return 0
        return true_counts / total_counts

    def tt_check_all(self, symbols, model, kb, alpha):
        """Recursively check all possible models."""
        self.update_progress_bar()
        if len(symbols) == 0:
            if self.is_true(kb, model):
                if self.is_true(alpha, model):
                    # alpha true, kb true
                    return 1, 1
                # alpha false, kb true
                return 0, 1
            else:
                # alpha false, kb false
                return 0, 0
        else:
            p = symbols[0]
            rest = list(symbols[1 : len(symbols)])

            self.progress_bar += 1

            true1, total1 = self.tt_check_all(rest, model + [(p, True)], kb, alpha)
            true2, total2 = self.tt_check_all(rest, model + [(p, False)], kb, alpha)
            return true1 + true2, total1 + total2

    def is_true(self, prop, model):
        """Check whether prop is true in model"""
        if isinstance(prop, str):
            return (prop, True) in model
        elif len(prop) == 1:
            return self.is_true(prop[0], model)
        elif prop[0] == "not":
            return not self.is_true(prop[1], model)
        elif prop[1] == "and":
            return self.is_true(prop[0], model) and self.is_true(prop[2], model)
        elif prop[1] == "or":
            return self.is_true(prop[0], model) or self.is_true(prop[2], model)
        elif prop[1] == "implies":
            return (not self.is_true(prop[0], model)) or self.is_true(prop[2], model)
        elif prop[1] == "iff":
            left = (not self.is_true(prop[0], model)) or self.is_true(prop[2], model)
            right = (not self.is_true(prop[2], model)) or self.is_true(prop[0], model)
            return left and right
        return False

    def get_symbols(self, clauses):
        """Extract all unique symbols from the KB."""
        symbols = set()
        for clause in clauses:
            self.extract_symbols(clause, symbols)
        return list(symbols)

    def extract_symbols(self, clause, symbols):
        """Helper to extract symbols from a clause."""
        if isinstance(clause, str) and not self.is_operator(clause):
            symbols.add(clause)
        elif isinstance(clause, list):
            for part in clause:
                self.extract_symbols(part, symbols)

    def is_operator(self, item):
        """Check if the item is a logical operator."""
        return item in ["not", "and", "or", "implies", "iff"]

    def update_progress_bar(self):
        """Prints a simple progress bar based on the model check count, capped at maximum."""
        total_bar_length = 100

        filled_length = int(
            round(
                total_bar_length
                * self.progress_bar
                / max(1, self.expected_maximum_checks)
            )
        )
        filled_length = min(filled_length, total_bar_length)  # Cap at max

        bar = "█" * filled_length + "-" * (total_bar_length - filled_length)
        print(f"\rProgress: [{bar}] {self.progress_bar} checks", end="\r")

    def tt_enumerate(self, symbols, model):
        """Truth table enumeration for debugging purposes"""
        if len(symbols) == 0:
            print("model ", model)
            return
        else:
            p = symbols[0]
            rest = list(symbols[1 : len(symbols)])
            self.tt_enumerate(rest, model + [(p, True)])
            self.tt_enumerate(rest, model + [(p, False)])
            return
