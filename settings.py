from __future__ import annotations
import pygame
import random
from pygame.locals import *
from functools import reduce
import csv

GAME_NAME = "Peak Boardgame"
WINDOW_RESOLUTION = (1024, 768)
GAME_SCALE = 1
FPS = 120

CARD_W, CARD_H = 100, 140  # Kích thước lá bài
GAP = 20                   # Khoảng cách giữa các lá
START_X = 50

COLOR_INDEX = ["black","blue","green","red","white"]
GEMS_INDEX = ["Onyx","Sapphire","Emerald","Ruby","Diamond","Gold"]