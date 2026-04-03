class Player:
    def __init__(self):
        self.temp = {
            "white": 0,
            "green": 0,
            "Gold": 0,
            "red": 0,
            "black": 0,
            "blue": 0
        }

        self.cards = []

        self.perm = {
            "white": 0,
            "green": 0,
            "red": 0,
            "black": 0,
            "blue": 0
        }

    def get_gems(self, name = None):
        if name is None:
            return self.temp
        else:
            return self.temp[name]
        
    def purchase(self, cost: dict, card):
        for color, amount in cost.items():
            available = self.temp[color] + self.perm.get(color, 0)
            if available < amount:
                return False

        for color, amount in cost.items():
            pay = max(0, amount - self.perm.get(color, 0))
            self.temp[color] -= pay

        self.cards.append(card)
        self.perm[card.color] += 1
        return True
    
    def get_cards():
        pass

        
