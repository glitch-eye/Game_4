from player import *
from bank import *
import random
from copy import deepcopy

class Monte_carlo(RandomBot):
    def __init__(self, num_simulations=50):
        super().__init__()
        self.players = None
        self.bank = None
        self.num_simulations = num_simulations
        self.action_values = {}  # For storing action evaluation scores

    def copy(self):
        """Create a deep copy of this bot for simulation"""
        new_bot = Monte_carlo(self.num_simulations)
        new_bot.temp = self.temp.copy()
        new_bot.cards = self.cards.copy()
        new_bot.perm = self.perm.copy()
        new_bot.deposit_card = self.deposit_card.copy()
        new_bot.noble = self.noble.copy()
        new_bot.point = self.point
        new_bot.total_temp = self.total_temp
        return new_bot

    def get_action(self, cards: list, bank: Bank, players = [], shown_nobles = None):
        """
        Main decision function that uses Monte Carlo simulation.
        Returns a tuple: (action_type, action_data)
        action_type: "TAKE_3", "TAKE_2", "RESERVE", "BUY"
        action_data: indices for TAKE_3/TAKE_2, card for BUY/RESERVE
        """
        if self.players is None:
            self.players = players
        if self.bank is None:
            self.bank = bank
        self.shown_nobles = shown_nobles if shown_nobles else []

        available_actions = self._get_available_actions(cards, bank)
        
        if not available_actions:
            return None

        # Evaluate each action through simulation
        best_action = None
        best_score = -float('inf')

        for action in available_actions:
            score = self._simulate_action(action, cards, bank, players, self.shown_nobles)
            self.action_values[str(action)] = score
            
            if score > best_score:
                print(score)
                print(str(action))
                best_score = score
                best_action = action

        return self.resolve(best_action)
    
    def resolve(self, best_action):
        if best_action[0] == "BUY":
            self.current_action = "BUY"
            self.choosing_card = best_action[1]
            return self.current_action
        elif best_action[0] == "RESERVE":
            self.current_action = "RESERVE"
            self.choosing_card = best_action[1]
            return self.current_action
        elif best_action[0] == "TAKE_GEMS":
            self.current_action = "TAKE 3"
            self.selected_gems = best_action[1]
            return self.current_action
        elif best_action[0] == "TAKE_SAME":
            self.current_action = "TAKE 2"
            self.selected_gems = best_action[1]
            return self.current_action
        return None

    def _get_available_actions(self, cards: list, bank: Bank):
        """Generate all valid actions from current state"""
        actions = []
        current_gems = sum(self.temp.get(color, 0) for color in ["black", "blue", "green", "red", "white"])
        
        # BUY actions: cards we can afford
        for card in cards:
            if self._can_afford_card(card):
                actions.append(("BUY", card))
        
        # RESERVE action: if we have room
        if len(self.deposit_card) < 3:
            for card in cards:
                actions.append(("RESERVE", card))
        
        # GEM GATHERING: Try to take combinations of 1, 2, or 3 different gems
        gem_indices = [0, 1, 2, 3, 4]  # Exclude gold (index 5)
        
        # TAKE 1 gem
        if current_gems + 1 <= 10:
            for i in gem_indices:
                if bank.gem[i] > 0:
                    actions.append(("TAKE_GEMS", [i]))
        
        # TAKE 2 different gems
        if current_gems + 2 <= 10:
            for i in range(len(gem_indices)):
                for j in range(i + 1, len(gem_indices)):
                    if bank.gem[gem_indices[i]] > 0 and bank.gem[gem_indices[j]] > 0:
                        actions.append(("TAKE_GEMS", [gem_indices[i], gem_indices[j]]))
        
        # TAKE 3 different gems
        if current_gems + 3 <= 10:
            for i in range(len(gem_indices)):
                for j in range(i + 1, len(gem_indices)):
                    for k in range(j + 1, len(gem_indices)):
                        if (bank.gem[gem_indices[i]] > 0 and 
                            bank.gem[gem_indices[j]] > 0 and 
                            bank.gem[gem_indices[k]] > 0):
                            actions.append(("TAKE_GEMS", [gem_indices[i], gem_indices[j], gem_indices[k]]))
        
        # TAKE 2 of same gem type (special rule - only if at least 4 available)
        if current_gems + 2 <= 10:
            for i in range(5):  # Exclude gold
                if bank.gem[i] >= 4:
                    actions.append(("TAKE_SAME", i))
        
        return actions

    def _can_afford_card(self, card) -> bool:
        """Check if we can afford to buy a card (gold can substitute for any gem)"""
        total_gold = self.temp.get("gold", 0)
        remaining_gold = total_gold
        
        for i in range(5):
            color = ["black", "blue", "green", "red", "white"][i]
            cost = card.resources[i]
            available = self.temp.get(color, 0) + self.perm.get(color, 0)
            
            if available < cost:
                # Need gold to make up the difference
                needed_gold = cost - available
                remaining_gold -= needed_gold
                if remaining_gold < 0:
                    return False
        
        return True

    def _simulate_action(self, action, cards: list, bank: Bank, players: list, shown_nobles=None) -> float:
        """
        Run N simulations of an action and return average score gain
        """
        if shown_nobles is None:
            shown_nobles = []
            
        total_score_gain = 0.0
        
        for _ in range(self.num_simulations):
            # Deep copy state
            sim_players = [self._copy_player(p) for p in players]
            sim_bank = self._copy_bank(bank)
            sim_nobles = shown_nobles.copy()  # Nobles don't change in simulation
            sim_cards = cards  # Cards don't change in simulation
            
            # Find current player in simulation - search by identity or type
            current_idx = None
            for i, p in enumerate(players):
                if p is self or isinstance(p, Monte_carlo):
                    current_idx = i
                    break
            
            if current_idx is None:
                # Fallback: assume first player is the Monte Carlo bot
                current_idx = 0
            
            sim_current_player = sim_players[current_idx]
            
            # Execute the action
            self._execute_simulated_action(sim_current_player, action, sim_bank, sim_cards)
            
            # Check for noble acquisition after action
            self._acquire_available_nobles(sim_current_player, sim_nobles)
            
            # Play out rest of game with random moves
            final_score = self._playout(sim_players, current_idx, sim_bank, sim_cards, sim_nobles)
            
            total_score_gain += final_score
        
        return total_score_gain / self.num_simulations

    def _execute_simulated_action(self, player: Player, action, bank: Bank, cards: list):
        """Execute an action in the simulation"""
        action_type, action_data = action
        
        if action_type == "BUY":
            card = action_data
            cost_dict = self._card_cost_to_dict(card)
            player.purchase(cost_dict, card)
            
        elif action_type == "RESERVE":
            card = action_data
            player.deposit(card)
            # Gain gold if available
            if bank.can_book():
                total_gems = sum(player.temp.get(c, 0) for c in ["black", "blue", "green", "red", "white"])
                if total_gems < 10:
                    bank.gem[5] -= 1
                    player.temp["gold"] += 1
                    player.total_temp += 1
                
        elif action_type == "TAKE_GEMS":
            indices = action_data
            # Take individual gems from each index
            for i in indices:
                if bank.gem[i] > 0:
                    bank.gem[i] -= 1
                    gem_name = ["black", "blue", "green", "red", "white"][i]
                    player.temp[gem_name] += 1
                    player.total_temp += 1
                    
        elif action_type == "TAKE_SAME":
            index = action_data
            if bank.gem[index] >= 2:
                bank.gem[index] -= 2
                gem_name = ["black", "blue", "green", "red", "white"][index]
                player.temp[gem_name] += 2
                player.total_temp += 2

    def _playout(self, players: list, current_player_idx: int, bank: Bank, cards: list, shown_nobles=None) -> float:
        """
        Mô phỏng ngẫu nhiên qua một số lượt (chiều sâu) 
        sau đó đánh giá trạng thái đạt được.
        """
        if shown_nobles is None:
            shown_nobles = []
            
        bot_index = current_player_idx
        max_depth = 6  # Độ sâu mô phỏng (tương đương khoảng 2-3 vòng chơi)
        
        for _ in range(max_depth):
            current_player = players[current_player_idx]
            
            # Lấy danh sách hành động khả thi tại trạng thái giả lập này
            actions = self._get_available_actions_sim(current_player, cards, bank)
            if not actions:
                break
            
            # Chọn ngẫu nhiên một hành động để đi tiếp (Random Playout)
            action = random.choice(actions)
            self._execute_simulated_action(current_player, action, bank, cards)
            
            # Kiểm tra Noble ngay trong giả lập
            self._acquire_available_nobles(current_player, shown_nobles)
            
            # Chuyển sang người chơi tiếp theo
            current_player_idx = (current_player_idx + 1) % len(players)

        # --- SAU KHI ĐI HẾT ĐỘ SÂU, TÍNH SCORE ĐỂ ĐÁNH GIÁ HÀNH ĐỘNG BAN ĐẦU ---
        
        bot_player = players[bot_index]
        colors = ["black", "blue", "green", "red", "white"]

        # --- 1. PHÂN TÍCH NHU CẦU NOBLE (Noble Demand) ---
        # Tính xem mỗi màu đang được các Noble yêu cầu tổng cộng bao nhiêu
        noble_demand = {color: 0 for color in colors}
        for noble in shown_nobles:
            for i in range(5):
                color = colors[i]
                # Nếu Noble yêu cầu màu này, cộng dồn vào nhu cầu
                noble_demand[color] += noble.resources[i]

        # --- 2. TÍNH ĐIỂM TÀI NGUYÊN CÓ TRỌNG SỐ (Weighted Perm Score) ---
        perm_score = 0
        for color in colors:
            count = bot_player.perm.get(color, 0)
            # Hệ số cơ bản là 6, nếu màu đó Noble đang cần thì cộng thêm bonus (ví dụ +4)
            # Bạn có thể điều chỉnh noble_demand[color] * 2 để tăng độ "cuồng" màu đó
            weight = 6 + (noble_demand[color] * 1.5) 
            perm_score += count * weight

        # --- 3. ĐÁNH GIÁ CHÊNH LỆCH ĐIỂM SỐ ---
        opponents = [p for i, p in enumerate(players) if i != bot_index]
        max_opponent_point = max(p.point for p in opponents)
        score_eval = (bot_player.point - max_opponent_point) * 25 

        # --- 4. BONUS QUÝ TỘC (Tiến độ trực tiếp) ---
        noble_bonus = 0
        for noble in shown_nobles:
            needed = 0
            for i in range(5):
                color = colors[i]
                diff = noble.resources[i] - bot_player.perm.get(color, 0)
                if diff > 0:
                    needed += diff
            
            if needed == 0:
                noble_bonus += 75
            elif needed == 1:
                noble_bonus += 40
            elif needed == 2:
                noble_bonus += 20

        # --- 5. TỔNG HỢP ---
        temp_score = sum(bot_player.temp.values()) * 1.5
        reserve_penalty = len(bot_player.deposit_card) * -2

        return (bot_player.point * 50) + score_eval + perm_score + temp_score + noble_bonus + reserve_penalty


    def _get_available_actions_sim(self, player: Player, cards: list, bank: Bank):
        """Get available actions for a player in simulation"""
        actions = []
        current_gems = sum(player.temp.get(color, 0) for color in ["black", "blue", "green", "red", "white"])
        
        # BUY actions
        for card in cards:
            if self._can_afford_card_sim(player, card):
                actions.append(("BUY", card))
        
        # RESERVE
        if len(player.deposit_card) < 3:
            for card in cards:
                actions.append(("RESERVE", card))
        
        # GEM GATHERING: Try to take combinations of 1, 2, or 3 different gems
        gem_indices = [0, 1, 2, 3, 4]
        
        # TAKE 1 gem
        if current_gems + 1 <= 10:
            for i in gem_indices:
                if bank.gem[i] > 0:
                    actions.append(("TAKE_GEMS", [i]))
        
        # TAKE 2 different gems
        if current_gems + 2 <= 10:
            for i in range(len(gem_indices)):
                for j in range(i + 1, len(gem_indices)):
                    if bank.gem[gem_indices[i]] > 0 and bank.gem[gem_indices[j]] > 0:
                        actions.append(("TAKE_GEMS", [gem_indices[i], gem_indices[j]]))
        
        # TAKE 3 different gems
        if current_gems + 3 <= 10:
            for i in range(len(gem_indices)):
                for j in range(i + 1, len(gem_indices)):
                    for k in range(j + 1, len(gem_indices)):
                        if (bank.gem[gem_indices[i]] > 0 and 
                            bank.gem[gem_indices[j]] > 0 and 
                            bank.gem[gem_indices[k]] > 0):
                            actions.append(("TAKE_GEMS", [gem_indices[i], gem_indices[j], gem_indices[k]]))
        
        # TAKE 2 of same gem type (special rule - only if at least 4 available)
        if current_gems + 2 <= 10:
            for i in range(5):
                if bank.gem[i] >= 4:
                    actions.append(("TAKE_SAME", i))
        
        return actions

    def _can_afford_card_sim(self, player: Player, card) -> bool:
        """Check affordability for simulation (gold can substitute for any gem)"""
        total_gold = player.temp.get("gold", 0)
        remaining_gold = total_gold
        
        for i in range(5):
            color = ["black", "blue", "green", "red", "white"][i]
            cost = card.resources[i]
            available = player.temp.get(color, 0) + player.perm.get(color, 0)
            
            if available < cost:
                # Need gold to make up the difference
                needed_gold = cost - available
                remaining_gold -= needed_gold
                if remaining_gold < 0:
                    return False
        
        return True

    def _card_cost_to_dict(self, card) -> dict:
        """Convert card resources to cost dictionary"""
        keys = ["black", "blue", "green", "red", "white"]
        return {keys[i]: card.resources[i] for i in range(5)}

    def _copy_player(self, player: Player) -> Player:
        """Deep copy a player"""
        new_player = Player()
        new_player.temp = player.temp.copy()
        new_player.cards = player.cards.copy()
        new_player.perm = player.perm.copy()
        new_player.deposit_card = player.deposit_card.copy()
        new_player.noble = player.noble.copy()
        new_player.point = player.point
        new_player.total_temp = player.total_temp
        return new_player

    def _copy_bank(self, bank: Bank) -> Bank:
        """Deep copy the bank"""
        new_bank = Bank(None, None, len(self.players))
        new_bank.gem = bank.gem.copy()
        return new_bank

    def _can_acquire_noble(self, player: Player, noble) -> bool:
        """Check if player meets noble's requirements"""
        for i in range(5):
            color = ["black", "blue", "green", "red", "white"][i]
            required = noble.resources[i]
            available = player.perm.get(color, 0)
            if available < required:
                return False
        return True

    def _acquire_available_nobles(self, player: Player, shown_nobles: list):
        """Automatically acquire all available nobles for a player"""
        nobles_to_acquire = []
        for noble in shown_nobles:
            if self._can_acquire_noble(player, noble):
                nobles_to_acquire.append(noble)
        
        # Add acquired nobles to player
        for noble in nobles_to_acquire:
            player.add_noble(noble)
            shown_nobles.remove(noble)


