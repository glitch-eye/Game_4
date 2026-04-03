import pygame

class Bank:
    def __init__(self, loader, game, numberofplayer):
        if numberofplayer == 2:
            self.gem = [4,4,4,4,4,5] #Onyx,Sapphire,Emerald,Ruby,White,Gold
        elif numberofplayer == 3:
            self.gem = [5,5,5,5,5,5]
        else:
            self.gem = [7,7,7,7,7,5]

    def can_take_3(self, indices):
        if len(indices) != 3:
            return False
        if len(set(indices)) != 3:
            return False
        if 5 in indices:  # no gold
            return False

        for i in indices:
            if self.gem[i] <= 0:
                return False
        return True

    def get_3(self, indices):
        if not self.can_take_3(indices):
            return False

        for i in indices:
            self.gem[i] -= 1
        return True

    def can_take_2(self, index):
        return index != 5 and self.gem[index] >= 4

    def get_2(self, index):
        if not self.can_take_2(index):
            return False

        self.gem[index] -= 2
        return True

    def can_book(self):
        return self.gem[5] > 0

    def pay(self, gems):
        for i in range(6):
            self.gem[i] += gems[i]