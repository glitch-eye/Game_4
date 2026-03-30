class Player:
    def __init__(self):
        self.gems = {
            "Diamond": 0,
            "Emerald": 0,
            "Gold": 0,
            "Ruby": 0,
            "Onyx": 0,
            "Sapphire": 0
        }

        self.cards = []

    def get_gems(self, name = None):
        if name is None:
            return self.gems
        else:
            return self.gems[name]
        
    def purchase(self, gems : dict, card):
        for keys, item in gems.items():
            cur = self.gems[keys]
            if item > cur:
                return False
            self.gems[keys] =  cur - item
        self.cards.append(card)
        return True
    
    def get_cards()

        
