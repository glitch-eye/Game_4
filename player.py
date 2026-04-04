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
        self.action = None

    def get_gems(self, name = None):
        if name is None:
            return None
        return self.temp[name] + self.perm.get(name, 0)
        
    def purchase(self, cost: dict, card: Card):
        payment = [0,0,0,0,0,0]  # black, blue, green, red, white, gold
        keys = ["black","blue","green","red","white"]

        # ===== CHECK CAN AFFORD (including gold) =====
        total_gold = self.temp["gold"]

        for color, amount in cost.items():
            available = self.temp[color] + self.perm.get(color, 0)
            if available >= amount:
                continue
            else:
                needed = amount - available
                if total_gold >= needed:
                    total_gold -= needed
                else:
                    return False

        # ===== PAY =====
        for i, color in enumerate(keys):
            required = cost[color]

            # discount from permanent
            perm_bonus = self.perm.get(color, 0)
            remaining = max(0, required - perm_bonus)

            # use colored gems first
            use_color = min(self.temp[color], remaining)
            self.temp[color] -= use_color
            payment[i] += use_color

            remaining -= use_color

            # use gold if needed
            if remaining > 0:
                self.temp["gold"] -= remaining
                payment[5] += remaining

        # ===== APPLY EFFECT =====
        self.cards.append(card)
        self.point += card.points

        # remove from reserved if needed
        for idx in range(len(self.deposit_card)):
            if card.is_same_card(self.deposit_card[idx]):
                self.deposit_card.pop(idx)
                break

        return payment
    
    def deposit(self, card : Card):
        self.deposit_card.append(card)

    def add_noble(self, card: Card):
        self.point += 3
        self.noble.append(card)
    
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
    
class RandomBot(Player):
    def __init__(self):
        super().__init__()

    def can_purchase(self, cost):
        for color, amount in cost.items():
            available = self.temp[color] + self.perm.get(color, 0)
            if available < amount:
                return False
        return True

    def get_action(self, cards, bank, players=None):
        valid_actions = []

        # ===== BUY =====
        buyable_cards = []
        for card in cards:
            cost = card_cost_to_dict(card)
            if self.can_purchase(cost): 
                buyable_cards.append(card)

        if buyable_cards:
            valid_actions.append("BUY")

        # ===== RESERVE =====
        if len(self.deposit_card) < 3:
            valid_actions.append("RESERVE")

        # ===== TAKE 3 =====
        available_colors = []
        keys = ["black", "blue", "green", "red", "white"]

        for i, k in enumerate(keys):
            if bank.gem[i] > 0:
                available_colors.append(i)

        if len(available_colors) >= 3:
            valid_actions.append("TAKE 3")

        # ===== TAKE 2 =====
        take2_colors = []
        for i in range(5):
            if bank.gem[i] >= 4:
                take2_colors.append(i)

        if take2_colors:
            valid_actions.append("TAKE 2")

        # ===== if nothing valid =====
        if not valid_actions:
            return None

        # random valid action
        action = random.choice(valid_actions)

        # assign decision details
        if action == "BUY":
            self.current_action = "BUY"
            self.choosing_card = random.choice(buyable_cards)

        elif action == "RESERVE":
            self.current_action = "RESERVE"
            self.choosing_card = random.choice(cards)

        elif action == "TAKE 3":
            self.current_action = "TAKE 3"
            random_number = random.randint(1, 3)
            self.selected_gems = random.sample(available_colors, random_number)

        elif action == "TAKE 2":
            self.current_action = "TAKE 2"
            self.selected_gem = random.choice(take2_colors)

        return action