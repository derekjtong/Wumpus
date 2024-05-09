# Derek Tong
# Professor Lyons
# CISC 6525 Artificial Intelligence
# May 9, 2024
#
# Wumpus World - Knowledge Base Implementation


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


# # Testing
# kb = KnowledgeBase()

# # No wumpus in 21
# kb.tell(["not", "w21"])

# # Stench in 31
# kb.tell(["w21", "or", ["w32", "or", "w41"]])

# # No wumpus 32
# kb.tell(["not", "w32"])

# # print(kb.kb)
# print("result: ", kb.ask(["not", "w32"]))
