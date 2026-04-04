from game import *
from player import *

def main():
    game = Game()
    game.init_game(bot=RandomBot())
    game.play()

if __name__ == "__main__":
    main()