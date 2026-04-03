import pygame
import sys

from settings import *
from pygame.locals import *

class Menu:
    def __init__(self):
        # bg
        self.bg = pygame.transform.scale(
            pygame.image.load("asset/Menubg.png").convert_alpha(),
            (WINDOW_RESOLUTION[0]*GAME_SCALE, WINDOW_RESOLUTION[1]*GAME_SCALE)
        )
        # dark overlay
        self.overlay = pygame.Surface(WINDOW_RESOLUTION)
        self.overlay.set_alpha(180)
        self.overlay.fill((0,0,0))

        # black bg
        self.blackbg = pygame.Surface(WINDOW_RESOLUTION)
        self.blackbg.fill((0, 0, 0))

        self.image = self.bg

        self.state = 0
        self.in_menu = True
        self.settings = False
        self.rect = self.image.get_rect(topleft=(0,0))
        self.font = pygame.font.SysFont("Arial", 28, bold=True)

        button_size = (300*GAME_SCALE, 70*GAME_SCALE)
        center_x, center_y = 870*GAME_SCALE, 500*GAME_SCALE
        spacing = 70

        # init menu buttons
        self.init_buttons = [
            MenuButton("Start Game (PvE)", (center_x, center_y), button_size),
            MenuButton("Settings", (center_x, center_y+spacing), button_size),
            MenuButton("Quit", (center_x, center_y+2*spacing), button_size),
        ]

        # pause menu buttons
        cx, cy = WINDOW_RESOLUTION[0]*GAME_SCALE//2, WINDOW_RESOLUTION[1]*GAME_SCALE//2
        self.pause_buttons = [
            MenuButton("Continue", (cx, cy-spacing), button_size, (0,0,200), (100,100,255)),
            MenuButton("Settings", (cx, cy), button_size, (0,0,200), (100,100,255)),
            MenuButton("Quit", (cx, cy+spacing), button_size, (0,0,200), (100,100,255)),
        ]

        # settings menu buttons (always centered, pure black background)
        self.settings_buttons = [
            MenuButton("Volume -", (cx-150, cy-spacing), (150, 60), (0,0,200), (100,100,255)),
            MenuButton("Volume +", (cx+150, cy-spacing), (150, 60), (0,0,200), (100,100,255)),
            MenuButton("Scale -", (cx-150, cy), (150, 60), (0,0,200), (100,100,255)),
            MenuButton("Scale +", (cx+150, cy), (150, 60), (0,0,200), (100,100,255)),
            MenuButton("Back", (cx, cy+spacing), button_size, (0,0,200), (100,100,255)),
        ]
        self.buttons = self.init_buttons

    def draw(self, screen):
        if not self.in_menu:
            return
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.image, self.rect)
        for b in self.buttons:
            b.draw(screen, self.font)

    def update(self):
        if self.settings:
            self.image = self.blackbg
            self.buttons = self.settings_buttons
        elif self.state == 0:
            self.image = self.bg
            self.buttons = self.init_buttons
        else:
            self.image = self.overlay
            self.buttons = self.pause_buttons

        mousepos = pygame.mouse.get_pos()
        for b in self.buttons:
            b.update(mousepos)

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.settings:
            for b in self.settings_buttons:
                if b.handle(event):
                    print(f"{b.name} clicked")
                    match b.name:
                        case "Back":
                            self.settings = False
                        case "Volume -":
                            print("Decrease volume")
                        case "Volume +":
                            print("Increase volume")
                        case "Scale -":
                            print("Decrease scale")
                        case "Scale +":
                            print("Increase scale")
            return False

        for b in self.buttons:
            if b.handle(event):
                print(f"{b.name} clicked")
                match b.name:
                    case "Quit":
                        pygame.quit()
                        sys.exit()
                    case "Settings":
                        self.settings = True
                        return False
                    case _:
                        self.in_menu = False
                        self.state = 1
                        return True

class MenuButton:
    def __init__(self, name, pos, button_size, 
                 normal_color=(200,0,0), hover_color=(255,100,100)):
        self.name = name
        self.rect = pygame.Rect(0, 0, *button_size)
        self.rect.center = pos
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.color = self.normal_color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0,0,0), self.rect, 2, border_radius=8)
        label = font.render(self.name, True, (255,255,255))
        screen.blit(label, (
            self.rect.centerx - label.get_width()//2,
            self.rect.centery - label.get_height()//2
        ))

    def update(self, mouse_pos):
        self.color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.normal_color

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False