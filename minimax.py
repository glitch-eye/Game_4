from player import *
import copy

class MinmaxPlayer(Player):
    def __init__(self):
        super().__init__()
        self.player1 = None
        self.player2 = None
        self.player3 = None

    # return action of player to game loop to execute
    def get_action(self, board, bank, players): 
        _, action = self.minimax(board, bank, players, depth=2, maximizing=True, current_idx=0)
        return action

    # choose action (with maximizing for self and minimizing for opponents)
    def choose_action(self,):
        pass

    def evaluate(self, players):
        # if ANY player is close to winning → switch to endgame evaluation
        endgame = any(p.points >= 15 for p in players)

        def eval_player(p):
            if endgame:
                return p.points * 100
            else:
                return p.points * 3 + sum(p.temp.values()) + sum(p.perm.values()) * 2

        my_score = eval_player(players[0])
        opp_score = sum(eval_player(p) for p in players[1:])

        return my_score - opp_score
    
    # obtain list of all possible action of chosen player    
    def get_action_list(self, board, bank, player):
        actions = []

        keys = ["black","blue","green","red","white"]

        # ===== PRIORITY 1: BUY =====
        for level in [1,2,3]:
            for card in board[level]:
                actions.append(("BUY", card))

        # ===== PRIORITY 2: SMART TAKE 3 =====
        gem_scores = []

        for i, color in enumerate(keys):
            if bank.gem[i] <= 0:
                continue

            owned = player.temp.get(color, 0) + player.perm.get(color, 0)
            missing = max(0, 4 - owned)

            # Tune
            score = missing * 2 + owned * 1.5

            gem_scores.append((score, i))

        # sort best → worst
        gem_scores.sort(reverse=True)

        best_gems = [i for _, i in gem_scores[:3]]

        if best_gems:
            actions.append(("TAKE3", best_gems))

        # ===== TAKE 2 (prefer monopoly gems) =====
        for score, i in gem_scores:
            if bank.can_take_2(i):
                actions.append(("TAKE2", i))

        # ===== PRIORITY 3: RESERVE =====
        if len(player.reserve) < 3:
            for level in [1,2,3]:
                for card in board[level]:
                    actions.append(("RESERVE", card))

        # ===== LIMIT ACTIONS =====
        return actions[:12]

    def minimax(self, board, bank, players, depth, maximizing, current_idx, alpha=-float("inf"), beta=float("inf")):
        if depth == 0:
            return self.evaluate(players), None

        best_action = None
        actions = self.get_action_list(board, bank, players[current_idx])

        if maximizing:
            max_eval = -float("inf")

            for action in actions:
                new_board, new_bank, new_players = self.simulate_action(
                    action, board, bank, players, current_idx
                )

                eval_score, _ = self.minimax(
                    new_board, new_bank, new_players,
                    depth - 1, False,
                    (current_idx + 1) % len(players),
                    alpha, beta
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = action

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # ✂️ PRUNE

            return max_eval, best_action

        else:
            min_eval = float("inf")

            for action in actions:
                new_board, new_bank, new_players = self.simulate_action(
                    action, board, bank, players, current_idx
                )

                eval_score, _ = self.minimax(
                    new_board, new_bank, new_players,
                    depth - 1, True,
                    (current_idx + 1) % len(players),
                    alpha, beta
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_action = action

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # ✂️ PRUNE

            return min_eval, best_action
        
    def simulate_action(self, action, board, bank, players, current_idx):
        board = copy.deepcopy(board)
        bank = copy.deepcopy(bank)
        players = copy.deepcopy(players)

        player = players[current_idx]

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
            card = action[1]

            cost = {
                "black": card.resources[0],
                "blue": card.resources[1],
                "green": card.resources[2],
                "red": card.resources[3],
                "white": card.resources[4]
            }

            if player.purchase(cost, card):
                # add permanent bonus
                color = card.color.lower()
                player.perm[color] = player.perm.get(color, 0) + 1

                # remove card from board
                for level in [1,2,3]:
                    for i, c in enumerate(board[level]):
                        if c.id == card.id:
                            board[level].pop(i)
                            break

        # ===== RESERVE =====
        elif action[0] == "RESERVE":
            if len(player.reserve) < 3:
                player.reserve.append(action[1])

                if bank.can_book():
                    bank.gem[5] -= 1
                    player.temp["gold"] += 1

                # remove from board
                for level in [1,2,3]:
                    for i, c in enumerate(board[level]):
                        if c.id == action[1].id:
                            board[level].pop(i)
                            break

        return board, bank, players