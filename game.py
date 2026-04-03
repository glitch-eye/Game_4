import pygame
from concurrent.futures import ThreadPoolExecutor

from pygame.locals import *
from settings import * 
from Deck import *
from bank import *
from Menu import *
import time

class Game():
    def __init__(self, workers=4):
        # pygame stuff
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_RESOLUTION)
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()

        # Menu
        self.menu = Menu()
        self.start = False

        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=workers)
        # game stuffs here
        self.cards = None
        self.nobles = None
        self.shown_nobles = []
        self.players = []
        self.bank = None

        self.level1 = None
        self.level2 = None
        self.level3 = None

        self.board = {}

        self.gems = []
        # Sửa dòng này trong __init__
        for gem_name in GEMS_INDEX:
            img = pygame.image.load(f"asset/{gem_name}.png").convert_alpha()
            self.gems.append(img)

        self.current_player = 0
        self.num_player = 2

    # Setting up game (can be used to restart new game)
    def init_game(self, num_player = 2):
        cards_by_level, self.cards, self.nobles = process_card_data()
        self.level1 = CardDeck(cards_by_level[1], 1)
        self.level2 = CardDeck(cards_by_level[2], 2)
        self.level3 = CardDeck(cards_by_level[3], 3)
        self.board = {
            1: [self.level1.draw() for _ in range(4)],
            2: [self.level2.draw() for _ in range(4)],
            3: [self.level3.draw() for _ in range(4)]
        }
        self.num_player = num_player
        
        self.bank = Bank(self.gems, None, num_player)
        # load sprites trước khi draw
        for card in self.cards:
            self.executor.submit(card.load)
        for noble in self.nobles.nobles:
            self.executor.submit(noble.load)
        
        # Chờ noble load xong trước khi bắt đầu game
        for noble in self.nobles.nobles:
            while noble.image is None:
                time.sleep(0.01)
        
        self.shown_nobles = [self.nobles.draw() for _ in range(num_player + 1)]

    def play(self):
        while self.running:
            self.handle_input()
            self.draw()
            self.update()
            self.clock.tick(FPS)
        
        pygame.quit()

    def draw(self):
        # Clear screen
        self.screen.fill((30, 30, 30))

        if not self.start:
            self.menu.draw(self.screen)
            pygame.display.flip()
            return

        main_width = int(WINDOW_RESOLUTION[0] * 0.75)
        main_height = WINDOW_RESOLUTION[1]

        main_rect = pygame.Rect(0, 0, main_width, WINDOW_RESOLUTION[1])
        pygame.draw.rect(self.screen, (0, 200, 200), main_rect)


        # 2. VẼ NOBLE (Hàng trên cùng)
        noble_rect = pygame.Rect(START_X , 20, CARD_W, CARD_W) 
        pygame.draw.rect(self.screen, (100, 100, 100), noble_rect)
        for i, noble in enumerate(self.shown_nobles):
            noble_rect = pygame.Rect(START_X + (i + 1) * (CARD_W + GAP), 20, CARD_W, CARD_W) # Noble thường hình vuông
            pygame.draw.rect(self.screen, (255, 255, 255), noble_rect, 2)
            noble.draw(self.screen,(START_X + (i + 1) * (CARD_W + GAP), 20))

        # 3. VẼ CÁC LÁ BÀI TRÊN BOARD (Level 3 ở trên, Level 1 ở dưới)
        for level in [3, 2, 1]:
            # Tính tọa độ Y dựa trên Level (3 là cao nhất)
            row_y = 150 + (3 - level) * (CARD_H + GAP)
            
            # Vẽ tập bài (Deck) của level đó (đại diện bằng 1 hình chữ nhật)
            deck_rect = pygame.Rect(START_X, row_y, CARD_W, CARD_H)
            pygame.draw.rect(self.screen, (100, 100, 100), deck_rect)
            
            # Vẽ các lá bài đang lật trên bàn
            if level in self.board:
                for i, card in enumerate(self.board[level]):
                    card_x = START_X + (i + 1) * (CARD_W + GAP)
                    card_rect = pygame.Rect(card_x, row_y, CARD_W, CARD_H)
                    
                    # Vẽ khung lá bài
                    color_map = {"Black": (0,0,0), "Blue": (0,0,255), "Red": (255,0,0), "Green": (0,255,0), "White": (255,255,255)}
                    bg_color = color_map.get(card.color, (200, 200, 200))
                    
                    pygame.draw.rect(self.screen, bg_color, card_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 2)
                    
                    # Nếu card đã load xong image:
                    if card.image:
                        card.draw(self.screen, (card_x, row_y))

        # 4. VẼ KHU VỰC HÀNH ĐỘNG (HÀNG DƯỚI CÙNG)
        # Đây là nơi người chơi hiện tại thực hiện thao tác
        action_zone_h = 150
        action_rect = pygame.Rect(0, main_height - action_zone_h, main_width, action_zone_h)
        pygame.draw.rect(self.screen, (40, 40, 40), action_rect)
        pygame.draw.rect(self.screen, (0, 255, 200), action_rect, 3) # Viền nổi bật cho người chơi hiện tại


        side_width = WINDOW_RESOLUTION[0] - main_width
        side_height = WINDOW_RESOLUTION[1] // 3

        # other player's resource zone
        for i in range(3):
            rect = pygame.Rect(main_width, i * side_height, side_width, side_height)
            pygame.draw.rect(self.screen, (150, 150, 150), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)  
        


        self.menu.draw(self.screen)
        pygame.display.flip()

    def update(self):
        if self.menu.in_menu:
            self.menu.update()
            return
        for level in [1,2,3]:
            while len(self.board[level]) < 4:
                card = getattr(self, f"level{level}").draw()
                if card:
                    self.board[level].append(card)

    def handle_input(self):
        for event in pygame.event.get():
            if self.menu.in_menu:
                if self.menu.handle_input(event):
                    self.start = True
                continue
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu.in_menu = True
            

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)