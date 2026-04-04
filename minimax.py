import copy
from player import *
from Deck import card_cost_to_dict

class MinmaxPlayer(Player):
    def __init__(self):
        super().__init__()

    # ===== ENTRY =====
    def get_action(self, cards, bank, players):
        _, action = self.minimax(
            cards, bank, players,
            depth=2,
            alpha=-float("inf"),
            beta=float("inf"),
            maximizing=True,
            current_idx=0
        )

        if action:
            self.apply_action(action)

        return self.current_action

    # ===== APPLY TO REAL GAME =====
    def apply_action(self, action):
        t = action[0]

        if t == "BUY":
            self.current_action = "BUY"
            self.choosing_card = action[1]

        elif t == "RESERVE":
            self.current_action = "RESERVE"
            self.choosing_card = action[1]

        elif t == "TAKE3":
            self.current_action = "TAKE 3"
            self.selected_gems = action[1]

        elif t == "TAKE2":
            self.current_action = "TAKE 2"
            self.selected_gem = action[1]

    # ===== ACTION GENERATION =====
    def get_actions(self, board, bank, player):
        actions = []
        keys = ["black","blue","green","red","white"]

        # ===== BUY =====
        for card in board:
            cost = card_cost_to_dict(card)
            if self.can_purchase_sim(player, cost):
                actions.append(("BUY", card))

        # ===== GEM PRIORITY =====
        gem_scores = []
        for i, color in enumerate(keys):
            if bank.gem[i] <= 0:
                continue

            owned = player.temp[color] + player.perm.get(color, 0)

            # PRIORITY RULE:
            # - fewer gems => higher priority
            # - monopoly (perm) => higher priority
            score = (5 - owned) * 2 + player.perm.get(color, 0) * 3

            gem_scores.append((score, i))

        gem_scores.sort(reverse=True)

        # ===== TAKE 3 (ALWAYS MAX) =====
        best = [i for _, i in gem_scores[:3]]
        if len(best) >= 3 and bank.can_take_3(best):
            actions.append(("TAKE3", best))

        # ===== TAKE 2 =====
        for _, i in gem_scores:
            if bank.can_take_2(i):
                actions.append(("TAKE2", i))

        # ===== RESERVE =====
        if len(player.deposit_card) < 3:
            for card in board[:3]:
                actions.append(("RESERVE", card))

        return actions[:12]

    # ===== MINIMAX + ALPHA-BETA =====
    def minimax(self, board, bank, players, depth, alpha, beta, maximizing, current_idx):
        if depth == 0:
            return self.evaluate(players), None

        actions = self.get_actions(board, bank, players[current_idx])
        if not actions:
            return self.evaluate(players), None

        if maximizing:
            best_val = -float("inf")
            best_action = None

            for action in actions:
                nb, nbk, npl = self.simulate(action, board, bank, players, current_idx)

                val, _ = self.minimax(
                    nb, nbk, npl,
                    depth - 1,
                    alpha, beta,
                    False,
                    (current_idx + 1) % len(players)
                )

                if val > best_val:
                    best_val = val
                    best_action = action

                alpha = max(alpha, val)
                if beta <= alpha:
                    break  # 🔥 PRUNE

            return best_val, best_action

        else:
            best_val = float("inf")

            for action in actions:
                nb, nbk, npl = self.simulate(action, board, bank, players, current_idx)

                val, _ = self.minimax(
                    nb, nbk, npl,
                    depth - 1,
                    alpha, beta,
                    True,
                    (current_idx + 1) % len(players)
                )

                best_val = min(best_val, val)

                beta = min(beta, val)
                if beta <= alpha:
                    break  # 🔥 PRUNE

            return best_val, None

    # ===== EVALUATION =====
    def evaluate(self, players):
        me = players[0]

        temp_total = sum(me.temp.values())
        perm_total = sum(me.perm.values())

        # temp_difference (less spending is better)
        temp_diff = temp_total

        score = (
            me.point * 3 +
            temp_total +
            perm_total * 2 +
            temp_diff
        )

        # opponent pressure
        opp = sum(p.point for p in players[1:])
        return score - opp * 2

    # ===== SIMULATION =====
    def simulate(self, action, board, bank, players, idx):
        board = copy.deepcopy(board)
        bank = copy.deepcopy(bank)
        players = copy.deepcopy(players)

        player = players[idx]
        keys = ["black","blue","green","red","white"]

        # ===== TAKE 3 =====
        if action[0] == "TAKE3":
            if bank.get_3(action[1]):
                for i in action[1]:
                    player.temp[keys[i]] += 1

        # ===== TAKE 2 =====
        elif action[0] == "TAKE2":
            if bank.get_2(action[1]):
                player.temp[keys[action[1]]] += 2

        # ===== BUY =====
        elif action[0] == "BUY":
            cost = card_cost_to_dict(action[1])

            payment = player.purchase(cost, action[1])

            if payment:
                # 🔥 IMPORTANT: give gems back to bank
                bank.pay(payment)

        # ===== RESERVE =====
        elif action[0] == "RESERVE":
            if len(player.deposit_card) < 3:
                player.deposit(action[1])

                if bank.can_book():
                    bank.gem[5] -= 1
                    player.temp["gold"] += 1

        return board, bank, players

    # ===== PURCHASE CHECK =====
    def can_purchase_sim(self, player, cost):
        gold = player.temp["gold"]

        for color, amount in cost.items():
            available = player.temp[color] + player.perm.get(color, 0)

            if available >= amount:
                continue

            need = amount - available

            if gold >= need:
                gold -= need
            else:
                return False

        return True