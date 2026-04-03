import pygame
from concurrent.futures import ThreadPoolExecutor

from pygame.locals import *
from settings import * 
from Deck import *
from bank import *
from Menu import *
from player import *
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
        self.choosing_card = None
        self.choosing_cost = [0,0,0,0,0,0]
        self.choosing_gems = [0,0,0,0,0]
        self.action_button_rects = []
        self.cost_rects = []
        self.gems_rect = []
        self.card_rects = [[],[],[]]
        self.noble_rects = []
        self.board_rect = None
        self.bank_rect = None
        self.action_box_rect = None
        self.noble_area_rect = None

        self.current_action = None   # "TAKE 3", "TAKE 2", "RESERVE", "BUY"
        self.selected_gems = []      # indices for TAKE 3
        self.selected_gem = None     # index for TAKE 2
    # Setting up game (can be used to restart new game)
    def init_game(self, num_player = 2):
        if not hasattr(self, 'font'):
            self.font = pygame.font.SysFont("Arial", 16, bold=True)
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
        self.players = [Player() for _ in range(num_player)]
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


        main_width = int(WINDOW_RESOLUTION[0] * 0.75)
        main_height = WINDOW_RESOLUTION[1]

        self.noble_area_rect = pygame.Rect(START_X + (CARD_W + GAP), 20, (num_player + 1) * (CARD_W + GAP), CARD_W)
        board_height = 3 * (CARD_H + GAP)
        board_width = 4 * (CARD_W + GAP)
        self.board_rect = pygame.Rect(START_X + (CARD_W + GAP), 150, board_width, board_height)


        for i, noble in enumerate(self.shown_nobles):
            noble_rect = pygame.Rect(START_X + (i + 1) * (CARD_W + GAP), 20, CARD_W, CARD_W) # Noble thường hình vuông
            self.noble_rects.append(noble_rect)

        for level in [1, 2, 3]:
            # Tính tọa độ Y dựa trên Level (3 là cao nhất)
            row_y = 150 + (3 - level) * (CARD_H + GAP)
            # Vẽ các lá bài đang lật trên bàn
            if level in self.board:
                for i, card in enumerate(self.board[level]):
                    card_x = START_X + (i + 1) * (CARD_W + GAP)
                    card_rect = pygame.Rect(card_x, row_y, CARD_W, CARD_H)
                    self.card_rects[level-1].append(card_rect)
        # 4. Draw gem
        gems_start_x = START_X + 5 * (CARD_W + GAP) + 30 
        bank_h = len(GEMS_INDEX) * (GEM_SIZE + VERTICAL_GAP)
        self.bank_rect = pygame.Rect(gems_start_x, GEMS_START_Y, GEM_SIZE, bank_h)

        for i, gem_img in enumerate(self.gems):
            # Chỉ tính toán theo hàng dọc (row), không dùng cột (col)
            gem_x = gems_start_x
            gem_y = GEMS_START_Y + i * (GEM_SIZE + VERTICAL_GAP)
           
            gem_rect = pygame.Rect(gem_x, gem_y, GEM_SIZE, GEM_SIZE)
            self.gems_rect.append(gem_rect)

        # 5. Draw action box
        action_y_start = main_height - ACTION_ZONE_H
        self.action_box_rect = pygame.Rect(0, action_y_start, main_width, ACTION_ZONE_H)
        

        for i, _ in enumerate(GEMS_INDEX):
            # Tính toán cột và hàng (3 cột, 2 hàng)
            col = i % 3
            row = i // 3
            
            gx = RESOURCE_START_X + col * ( GAP * 2 + GEM_DISPLAY_SIZE)
            gy = action_y_start + 20 + row * (GAP + GEM_DISPLAY_SIZE)
            
            # Vẽ hình ảnh viên đá
        
            
            # Lưu rect để handle click
            gem_rect = pygame.Rect(gx, gy, GEM_DISPLAY_SIZE, GEM_DISPLAY_SIZE)
            self.cost_rects.append(gem_rect)


        # def action
        actions = [
            "TAKE 3",
            "TAKE 2",
            "RESERVE",
            "BUY"
        ]
        
        # position in map
        start_button_x = main_width - (ACTION_BTN_W + ACTION_GAP) * 2 - ACTION_GAP
        start_button_y = main_height - ACTION_ZONE_H + ACTION_GAP 

        for i, _ in enumerate(actions):
            # Sắp xếp thành lưới 2x2
            col = i % 2
            row = i // 2
            
            bx = start_button_x + col * (ACTION_BTN_W + ACTION_GAP)
            by = start_button_y + row * (60 + ACTION_GAP) # 60 là chiều cao nút rút gọn
            
            btn_rect = pygame.Rect(bx, by, ACTION_BTN_W, 60)
            self.action_button_rects.append(btn_rect)




    def play(self):
        while self.running:
            self.handle_input()
            self.draw()
            self.update()
            self.clock.tick(FPS)
        
        pygame.quit()

    def draw(self):
        # 1. Clear screen & Background
        self.screen.fill((30, 30, 30))

        if not self.start:
            self.menu.draw(self.screen)
            pygame.display.flip()
            return

        main_width = int(WINDOW_RESOLUTION[0] * 0.75)
        main_height = WINDOW_RESOLUTION[1]

        main_rect = pygame.Rect(0, 0, main_width, main_height)
        pygame.draw.rect(self.screen, (0, 200, 200), main_rect)

        # 2. Draw NOBLES
        noble_rect = pygame.Rect(START_X , 20, CARD_W, CARD_W) 
        pygame.draw.rect(self.screen, (100, 100, 100), noble_rect)
        for i, noble in enumerate(self.shown_nobles):
            if i < len(self.noble_rects):
                rect = self.noble_rects[i]
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                noble.draw(self.screen, rect.topleft)

        # 3. Draw cards on BOARD 
        for level_idx in range(3): # level 0, 1, 2 tương ứng level 1, 2, 3
            level = level_idx + 1
            # Vẽ Deck placeholder (Nếu bạn muốn lưu deck_rect riêng cũng được, ở đây dùng tạm logic cũ)
            row_y = 150 + (3 - level) * (CARD_H + GAP)
            pygame.draw.rect(self.screen, (100, 100, 100), (START_X, row_y, CARD_W, CARD_H))
            
            if level in self.board:
                for i, card in enumerate(self.board[level]):
                    if i < len(self.card_rects[level_idx]):
                        rect = self.card_rects[level_idx][i]
                        
                        # Vẽ khung nền dựa trên màu lá bài
                        color_map = {"Black": (0,0,0), "Blue": (0,0,255), "Red": (255,0,0), "Green": (0,255,0), "White": (255,255,255)}
                        bg_color = color_map.get(card.color, (200, 200, 200))
                        
                        pygame.draw.rect(self.screen, bg_color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                        
                        if card.image:
                            card.draw(self.screen, rect.topleft)
                        
                        if self.choosing_card and card.is_same_card(self.choosing_card):
                            pygame.draw.rect(self.screen, (255, 255, 0), rect, 4)

        # 4. Draw BANK GEMS (Sử dụng self.gems_rect)
        for i, gem_img in enumerate(self.gems):
            rect = self.gems_rect[i]
            # Vẽ hình ảnh viên đá
            scaled_gem = pygame.transform.smoothscale(gem_img, (GEM_SIZE, GEM_SIZE))
            self.screen.blit(scaled_gem, rect.topleft)
            
            if self.bank:
                count = self.bank.gem[i]
                count_txt = self.font.render(str(count), True, (255, 255, 255))
                # Căn số lượng vào góc dưới bên phải của rect
                txt_rect = count_txt.get_rect(bottomright=(rect.right - 5, rect.bottom - 5))
                self.screen.blit(count_txt, txt_rect)
            if i < len(self.choosing_gems) and self.choosing_gems[i] > 0:
                # Vẽ số lượng dự tính lấy màu xanh lá
                select_txt = self.font.render(f"{self.choosing_gems[i]}", True, (0, 255, 0))
                self.screen.blit(select_txt, (rect.x + 5, rect.y + 5))

            if i in self.selected_gems or i == self.selected_gem:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)

        # 5. Draw ACTION BOX & PLAYER RESOURCES (Sử dụng self.cost_rects)
        action_rect = pygame.Rect(0, main_height - ACTION_ZONE_H, main_width, ACTION_ZONE_H)
        pygame.draw.rect(self.screen, (40, 40, 40), action_rect)
        pygame.draw.rect(self.screen, (0, 255, 200), action_rect, 3)

        current_p = self.players[self.current_player]
        gem_to_key = {"Onyx": "black", "Sapphire": "blue", "Emerald": "green", "Ruby": "red", "Diamond": "white", "Gold": "gold"}
        score_txt = self.font.render(f"YOUR SCORE: {current_p.point}", True, (255, 255, 0))
        self.screen.blit(score_txt, (20, action_rect.y + 5))
        for i, gem_name in enumerate(GEMS_INDEX):
            rect = self.cost_rects[i]
            # Vẽ hình ảnh viên đá nhỏ trong túi player
            scaled_img = pygame.transform.smoothscale(self.gems[i], (GEM_DISPLAY_SIZE, GEM_DISPLAY_SIZE))
            self.screen.blit(scaled_img, rect.topleft)
            
            key = gem_to_key[gem_name]
            # Vẽ số lượng Gems đang có (temp)
            count_surf = self.font.render(f"x{current_p.temp.get(key, 0)}", True, (255, 255, 255))
            self.screen.blit(count_surf, (rect.right + 8, rect.top + 2))
            
            # Vẽ số lượng Card vĩnh viễn (perm)
            if key != "gold":
                perm_count = current_p.perm.get(key, 0)
                perm_surf = self.font.render(f"+{perm_count}", True, (0, 255, 100))
                self.screen.blit(perm_surf, (rect.right + 8, rect.top + 22))
            if i < len(self.choosing_cost) and self.choosing_cost[i] > 0:
                cost_txt = self.font.render(f"{self.choosing_cost[i]}", True, (0, 255, 0))
                # Vẽ đè ngay trung tâm icon gem của player
                self.screen.blit(cost_txt, (rect.x + 5, rect.y + 5))

        # 6. Draw ACTION BUTTONS (Sử dụng self.action_button_rects)
        actions_labels = ["TAKE 3", "TAKE 2", "RESERVE", "BUY"]
        for i, label in enumerate(actions_labels):
            rect = self.action_button_rects[i]
            # Vẽ nút
            if self.current_action == label:
                color = (0, 150, 200)
            else:
                color = (60, 60, 60)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
            
            # Vẽ text
            txt_surf = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

        # Draw CONFIRM BUTTON
        if self.current_action:
            confirm_rect = pygame.Rect(self.bank_rect.right - 100, self.bank_rect.bottom , 120, 50)
            self.confirm_rect = confirm_rect

            valid = self.can_confirm()
            color = (0, 200, 0) if valid else (80, 80, 80)

            pygame.draw.rect(self.screen, color, confirm_rect)
            pygame.draw.rect(self.screen, (255,255,255), confirm_rect, 2)

            txt = self.font.render("CONFIRM", True, (255,255,255))
            self.screen.blit(txt, txt.get_rect(center=confirm_rect.center))

        # 7. Draw SIDE BAR
        side_width = WINDOW_RESOLUTION[0] - main_width
        side_height = WINDOW_RESOLUTION[1] // 3
        for i in range(3):
            s_rect = pygame.Rect(main_width, i * side_height, side_width, side_height)
            pygame.draw.rect(self.screen, (150, 150, 150), s_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), s_rect, 2)

        others = [ (idx, p) for idx, p in enumerate(self.players) if idx != self.current_player ]
        
        for i, (idx, p_other) in enumerate(others):
            # Vẽ từng ô từ trên xuống dưới
            s_rect = pygame.Rect(main_width, i * side_height, side_width, side_height)
            pygame.draw.rect(self.screen, (60, 60, 60), s_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), s_rect, 2)
            
            # Tên và điểm đối thủ
            name_txt = self.font.render(f"PLAYER {idx + 1}", True, (255, 255, 255))
            p_score_txt = self.font.render(f"Score: {p_other.point}", True, (255, 255, 0))
            self.screen.blit(name_txt, (s_rect.x + 10, s_rect.y + 10))
            self.screen.blit(p_score_txt, (s_rect.x + 10, s_rect.y + 30))

            # Vẽ tài nguyên tóm tắt của đối thủ
            for g_idx, g_name in enumerate(GEMS_INDEX):
                key = gem_to_key[g_name]
                # Tính tổng khả năng chi trả của đối thủ (đá + thẻ)
                total = p_other.temp.get(key, 0) + (p_other.perm.get(key, 0) if key != "gold" else 0)
                
                # Sắp xếp icon nhỏ theo 2 cột trong ô side bar
                gx = s_rect.x + 10 + (g_idx % 2) * (side_width // 2)
                gy = s_rect.y + 60 + (g_idx // 2) * 25
                
                small_gem = pygame.transform.smoothscale(self.gems[g_idx], (20, 20))
                self.screen.blit(small_gem, (gx, gy))
                
                res_txt = self.font.render(f": {total}", True, (255, 255, 255))
                self.screen.blit(res_txt, (gx + 22, gy))

        if self.choosing_card is not None:
            # Vẽ chấm tròn màu xanh lá (0, 255, 0) tại tâm của rect bài
            pygame.draw.circle(self.screen, (0, 255, 0), self.choosing_card.center, 20)
            # Vẽ thêm viền trắng mỏng cho chấm tròn để nổi bật hơn
            pygame.draw.circle(self.screen, (255, 255, 255), self.choosing_card.center, 20, 2)

        self.menu.draw(self.screen)
        pygame.display.flip()

    def update(self):
        self.card_rects = [[], [], []]
        for level in [1, 2, 3]:
            row_y = 150 + (3 - level) * (CARD_H + GAP)
            for i, card in enumerate(self.board[level]):
                card_x = START_X + (i + 1) * (CARD_W + GAP)
                rect = pygame.Rect(card_x, row_y, CARD_W, CARD_H)
                self.card_rects[level-1].append(rect)
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
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                player = self.players[self.current_player]

                # ===== CLICK ACTION BUTTON =====
                for i, rect in enumerate(self.action_button_rects):
                    if rect.collidepoint(pos):
                        actions = ["TAKE 3", "TAKE 2", "RESERVE", "BUY"]
                        action = actions[i]

                        # toggle behavior
                        if self.current_action == action:
                            self.current_action = None
                        else:
                            self.current_action = action

                        # reset selections
                        self.selected_gems = []
                        self.selected_gem = None
                        self.choosing_card = None
                        return
                    
                # ===== CLICK CARD =====        
                if self.board_rect.collidepoint(pos):
                    for level_idx in range(3):
                        for i, rect in enumerate(self.card_rects[level_idx]):
                            if rect.collidepoint(pos):
                                if i < len(self.board[level_idx + 1]):
                                    card = self.board[level_idx + 1][i]

                                    if self.current_action in ["BUY", "RESERVE"]:
                                        if self.choosing_card and card.is_same_card(self.choosing_card):
                                            self.choosing_card = None
                                        else:
                                            self.choosing_card = card
                                return
                            
                # ===== CLICK BANK =====
                if self.bank_rect.collidepoint(pos):
                    for i, rect in enumerate(self.gems_rect):
                        if rect.collidepoint(pos):

                            # TAKE 3 (select up to 3 different)
                            if self.current_action == "TAKE 3":
                                if i == 5:
                                    return  # ignore gold
                                if i in self.selected_gems:
                                    self.selected_gems.remove(i)
                                elif len(self.selected_gems) < 3:
                                    self.selected_gems.append(i)

                            # TAKE 2 (only 1 type)
                            elif self.current_action == "TAKE 2":
                                if self.selected_gem == i:
                                    self.selected_gem = None
                                else:
                                    self.selected_gem = i

                            return
                        
                # ===== CONFIRM =====
                if self.current_action and hasattr(self, "confirm_rect") and self.confirm_rect.collidepoint(pos):
                    if self.can_confirm():
                        self.execute_action()

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.choosing_card = None
        self.choosing_cost = [0,0,0,0,0,0]
        self.choosing_gems = [0,0,0,0,0]

    def can_confirm(self):
        player = self.players[self.current_player]
        total = sum(player.temp.values())

        # BUY
        if self.current_action == "BUY":
            if not self.choosing_card:
                return False

            cost = card_cost_to_dict(self.choosing_card)
            for color, amount in cost.items():
                if player.temp[color] + player.perm.get(color, 0) < amount:
                    return False
            return True

        # RESERVE
        if self.current_action == "RESERVE":
            return self.choosing_card is not None and len(player.deposit_card) < 3

        # TAKE 3
        if self.current_action == "TAKE 3":
            if total + len(self.selected_gems) > 10:
                return False
            return self.bank.can_take_3(self.selected_gems)

        # TAKE 2
        if self.current_action == "TAKE 2":
            if total + 2 > 10:
                return False
            return self.selected_gem is not None and self.bank.can_take_2(self.selected_gem)

        return False
    
    def remove_card_from_board(self, target):
        for level in [1,2,3]:
            for i, card in enumerate(self.board[level]):
                if card.is_same_card(target):
                    self.board[level].pop(i)
                    return
                
    def execute_action(self):
        player = self.players[self.current_player]

        # ===== BUY =====
        if self.current_action == "BUY":
            cost = card_cost_to_dict(self.choosing_card)

            if player.purchase(cost, self.choosing_card):
                # ADD PERMANENT BONUS
                color_map = {
                    "Black": "black",
                    "Blue": "blue",
                    "Green": "green",
                    "Red": "red",
                    "White": "white"
                }

                bonus_color = color_map.get(self.choosing_card.color)
                if bonus_color:
                    player.perm[bonus_color] = player.perm.get(bonus_color, 0) + 1

                self.remove_card_from_board(self.choosing_card)

        # ===== RESERVE =====
        elif self.current_action == "RESERVE":
            if len(player.deposit_card) < 3:
                player.deposit(self.choosing_card)
                self.remove_card_from_board(self.choosing_card)

                # take gold if available
                if self.bank.can_book():
                    self.bank.gem[5] -= 1
                    player.temp["gold"] += 1

        # ===== TAKE 3 =====
        elif self.current_action == "TAKE 3":
            if self.bank.get_3(self.selected_gems):
                keys = ["black","blue","green","red","white"]
                for i in self.selected_gems:
                    player.temp[keys[i]] += 1

        # ===== TAKE 2 =====
        elif self.current_action == "TAKE 2":
            if self.bank.get_2(self.selected_gem):
                keys = ["black","blue","green","red","white"]
                player.temp[keys[self.selected_gem]] += 2

        # ===== END TURN =====
        self.next_turn()

        # reset everything
        self.current_action = None
        self.selected_gems = []
        self.selected_gem = None
        self.choosing_card = None

def card_cost_to_dict(card):
    keys = ["black", "blue", "green", "red", "white"]
    return {keys[i]: card.resources[i] for i in range(5)}