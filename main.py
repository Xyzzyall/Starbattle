import sys
import game


def main(args):
    game.start()
    game.loop()
    print('game over')
    return 0

main(sys.argv)  