from .board import Board
from random import randint
import argparse

from .go_graphics import *
# parser = argparse.ArgumentParser()
# parser.add_argument("--black", choices=['random', 'player'], help='Select who is controlling the black pieces\n' \
# 'random: a CPU making random moves\nplayer: you as the user select the move', default='random')
# parser.add_argument("--white", choices=['random', 'player'], help='Select who is controlling the white pieces\n' \
# 'random: a CPU making random moves\nplayer: you as the user select the move', default='random')
# args = parser.parse_args()



# game = Board(9)
# user_input = ""
# turn = 1
# users = {1: args.black, -1: args.white}
# while user_input != "stop":
#     print(f"TURN: {"BLACK" if turn == 1 else "WHITE"}")
#     game.print_score()
#     game.print_board()
#     possible_moves = game.get_valid_moves()
#     print(f"potential moves:{game.count_open_spaces()}, legal moves: {len(possible_moves)}")
#     if users[turn] == "random":
#         if len(possible_moves) == 0:
#             game.make_move()
#         else:
#             x,y = possible_moves[randint(0, len(possible_moves)-1)]
#             game.make_move(x,y)
#             print(f"({x},{y})")
#         user_input = input("-"*27).strip()
#     elif users[turn] == 'player':
#         x,y = (-1,-1)
#         valid = False
#         while not valid:
#             try:
#                 x = int(input("Please enter an x coordinate: "))
#                 y = int(input("Please enter a y coordinate: "))
#                 if (x,y) in possible_moves:
#                     valid = True
#                 else:
#                     print("that is an invalid move")
#             except ValueError:
#                 print("that is not a vliad number. Please enter valid numbers for x and y")
#                 valid = False
#             except KeyboardInterrupt:
#                 exit()
            
#     game.make_move(x,y)
#     turn *= -1



# look at the command line for what the user wants
do_print_help, player_files, levels, colors, graphics_wanted = parse_command_line_args(sys.argv[1:])

# help message for user, if -h or --help
if do_print_help:
    print_help()
    sys.exit(1)

# load up the player classes
players = (load_player(1, player_files[0], levels[0]), load_player(2, player_files[1], levels[1]))

# user can override graphics mode if desired
if not graphics_wanted: do_graphics = False

# hit it!
if do_graphics:
    app = App(players, colors)
    app.mainloop()

else:
    play_game_in_ascii(players[0], players[1])
    #print("Sorry--this game is not implemented yet in ASCII.", file=sys.stderr)