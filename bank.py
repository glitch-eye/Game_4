import pygame

class Bank:
    def __init__(self, loader, game, numberofplayer):
        if numberofplayer == 2:
            self.gem = [4,4,4,4,4,5]
        elif numberofplayer == 3:
            self.gem = [5,5,5,5,5,5]
        else:
            self.gem = [7,7,7,7,7,5] #Onyx,Sapphire,Emerald,Ruby,White,Gold
    
    def can_take_3(self, gems):
        for i in range(5):
            if (self.gem-gems[i]<0):
                return False
        
        return True
    
    def can_take_2(self, gems):
        for i in range(5):
            if (self.gem-gems[i]<2):
                return False
            
        return True
    
    def can_book(self):
        if self.gem[5]>0:
            return True
        else:
            return False

    def pay(self, gems):
        for i in range(6):
            self.gem[i] += gems[i]