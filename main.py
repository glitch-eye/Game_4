from game import *
from player import *
from minimax import *

def main():
    game = Game()
    # game.init_game(bot=RandomBot())
    # game.init_game(bot=MinmaxPlayer())
    game.init_game(bot=Monte_carlo())
    game.play()

if __name__ == "__main__":
    main()