import pygame
import random
from pygame.locals import *

class Card:
    def __init__(self, level, resources: list, color=None, points=0, path_dir=None):
        self.level = level
        self.color = color 
        self.resources = resources
        self.points = points
        self.dir = f"asset/level{level}/{path_dir}" if path_dir else None
        self.image = None
        self.is_draw = False

    def load(self):
        if self.image is None and self.dir:
            self.image = pygame.image.load(self.dir).convert_alpha()

    def draw(self, screen, position):
        if self.is_draw and self.image:
            rect = self.image.get_rect(center=position)
            screen.blit(self.image, rect)


class Noble(Card):
    def __init__(self, level, color, resources, points=0, path_dir=None):
        super().__init__(level, resources, color, points, path_dir)


class NobleDeck:
    def __init__(self, nobles):
        self.nobles = nobles

    def draw(self):
        if not self.nobles:
            return None
        card = random.choice(self.nobles)
        self.nobles.remove(card)
        return card

class CardDeck:
    def __init__(self, cards, level):
        self.level = level
        self.cards = cards

    def draw(self):
        if not self.can_draw():
            return None
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card
        
    def can_draw(self):
        return bool(self.cards)