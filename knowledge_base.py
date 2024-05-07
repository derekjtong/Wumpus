# Derek Tong
# Professor Lyons
# CISC 6525 Artificial Intelligence
# May 9, 2024
#
# Wumpus World - Knowledge Base Implementation


class KnowledgeBase:
    def __init__(self):
        self.kb = []

    def tell(self, clause):
        """Add a clause in propositional logic to the KB."""
        if not self.kb:
            self.kb.append(clause)
        else:
            newkb = [clause, "and"]
            newkb.append(self.kb)
            self.kb = newkb

    def ask(self, alpha):
        """Query the KB to see if alpha is entailed by the KB."""
        return self.tt_entails(self.kb, alpha)

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

    def tt_entails(self, kb, alpha):
        """Check all models to determine if kb entails alpha."""
        symbols = self.get_symbols(self.kb + [alpha])
        # print("--------- all truth tables ---------")
        # self.tt_enumerate(symbols, [])
        # print("---------   check tables   ---------")
        return self.tt_check_all(symbols, [], kb, alpha)

    def tt_check_all(self, symbols, model, kb, alpha):
        """Recursively check all possible models."""
        if len(symbols) == 0:
            # print("model ", model)
            # print("checking...")
            if self.is_true(kb, model):
                print("found model where kb=true")
                # print(
                #     "KB true, KB=T alpha? ", self.is_true(alpha, model)
                # )  # to illustrate how it works
                if self.is_true(alpha, model):
                    print("    kb entails alpha:", model)
                    return True
                print("    kb does not alpha:", model)
                return False
            else:
                # print("model is not true")
                return True
        else:
            p = symbols[0]
            rest = list(symbols[1 : len(symbols)])
            return self.tt_check_all(
                rest, model + [(p, True)], kb, alpha
            ) and self.tt_check_all(rest, model + [(p, False)], kb, alpha)

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

    def tt_enumerate(self, symbols, model):
        """Truth Table Enumeration for debugging purposes"""
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
