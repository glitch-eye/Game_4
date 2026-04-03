from Deck import *
class Player:
    def __init__(self):
        self.temp = {
            "white": 0,
            "green": 0,
            "gold": 0,
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
        self.deposit_card = []
        self.noble = []
        self.point = 0

    def get_gems(self, name = None):
        if name is None:
            return self.temp
        else:
            return self.temp[name]
        
    def purchase(self, cost: dict, card:  Card):
        for color, amount in cost.items():
            available = self.temp[color] + self.perm.get(color, 0)
            if available < amount:
                return False

        for color, amount in cost.items():
            pay = max(0, amount - self.perm.get(color, 0))
            self.temp[color] -= pay

        self.cards.append(card)
        self.point += card.points
        self.perm[card.color] = self.perm[card.color] + 1
        for idx in range(len(self.deposit_card)):
            if card.is_same_card(self.deposit_card[idx]):
                self.deposit_card.pop(idx)
                break
        return True
    
    def deposit(self, card : Card):
        self.temp["gold"] = self.temp["gold"] + 1
        self.deposit_card.append[card]

    def add_noble(self, card: Card):
        self.point += 3
        self.nobles.append(card)
    
    def get_noble(self):
        return self.noble
    
    def add_gems(self, gems):
        for x in gems:
            self.temp[x] = self.temp.get(x, 0) + 1

    def get_deposit_card(self, num = None):
        if num is not None and num < len(self.deposit_card):
            return self.deposit_card[num]
        else:
            return self.deposit_card
    
