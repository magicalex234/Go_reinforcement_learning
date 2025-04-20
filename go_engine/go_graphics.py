import sys
from .HumanPlayer import HumanPlayer
import random
from functools import partial
from .board import Board

################################################################################
# CONSTANTS
################################################################################

DEFAULT_PLAYER1_COLOR = "#FF0000"
DEFAULT_PLAYER2_COLOR = "#0000FF"
BACKGROUND_COLOR = "black"
BOARD_SIZE = 800
NUM_SQUARES = 9
SQUARE_SIZE = BOARD_SIZE//NUM_SQUARES
FRAME_TIME = 25
GRAVITY = 20
DEFAULT_AI_LEVEL = 4
DEFAULT_AI_FILE = "goPlayer"

# AUTOMATIC CONSTANTS--DON'T MESS WITH THESE
HALF_SQUARE = SQUARE_SIZE // 2

# ANSI ESCAPE SEQUENCES TO MAKE ASCII MODE IN COLOR--MAY NOT ALWAYS WORK
P1_ESCAPE = "\33[91m\33[1m"
P2_ESCAPE = "\33[34m\33[1m"
END_ESCAPE = "\33[0m"
BOARD_ESCAPE = "\33[90m"


do_graphics = True
try:
    import tkinter as tk
except ImportError:
    print("Warning: Could not find the tkinter module. Graphics disabled.", file=sys.stderr)
    do_graphics = False

try:        
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    print("Warning: Could not find the PIL module (or one of its components). Graphics disabled.", file=sys.stderr)
    do_graphics = False

if do_graphics:
    class App(tk.Tk):
        def __init__(self, players = None, player_colors = None, board_size = NUM_SQUARES):
            tk.Tk.__init__(self)
            self.title("Go")
            self.configure(bg=BACKGROUND_COLOR)

            # parse the passed players to set the field holding the AIs
            if players == None or len(players) == 0: self.players = (None, HumanPlayer(), HumanPlayer())
            elif len(players) == 1: self.players = (None, HumanPlayer(), players[0])
            elif len(players) == 2: self.players = (None, players[0], players[1])
            elif len(players) == 3: self.players = players

            # parse the player color args, define the color strings we'll need
            if player_colors == None:
                player_color_tuples = (None, self._make_color_tuple(DEFAULT_PLAYER1_COLOR), self._make_color_tuple(DEFAULT_PLAYER2_COLOR))
            elif len(player_colors) == 2:
                player_color_tuples = (None, self._make_color_tuple(player_colors[0]), self._make_color_tuple(player_colors[1]))

            self.color_strs = (None, App._make_color_string(player_color_tuples[1]), App._make_color_string(player_color_tuples[2]))
            self.dark_strs = (None, App._make_color_string(App._darken(player_color_tuples[1])), App._make_color_string(App._darken(player_color_tuples[2])))
            self.light_strs = (None, App._make_color_string(App._lighten(player_color_tuples[1])), App._make_color_string(App._lighten(player_color_tuples[2])))

            # make the necessary images
            self.overlay_image = self._make_board_image()
            self.piece1_image = self._make_piece_image(player_color_tuples[1])
            self.piece2_image = self._make_piece_image(player_color_tuples[2])
            self.wm_iconphoto(self, App._make_icon(player_color_tuples[1], player_color_tuples[2]))
            
            # other data structures
            self.board = Board(board_size)

            # start forming up the screen--here's the top banner
            self.top_banner = tk.Label(self, bg=BACKGROUND_COLOR, font=("Arial", 20))
            self.top_banner.grid(column=0, row=0, columnspan=board_size, sticky='w')

            

            self.canvas = tk.Canvas(width = board_size*SQUARE_SIZE, height = board_size*SQUARE_SIZE, bg="white", highlightthickness=0)
            self.canvas.grid(column=0, row=2, columnspan=board_size, rowspan=board_size, sticky='')
            # random player goes 1st
            self.buttons = []
            for i in range(board_size):
                self.grid_columnconfigure(i, minsize=SQUARE_SIZE)
                self.buttons.append([])
                for j in range(board_size):
                    self.grid_rowconfigure(j+2, minsize=SQUARE_SIZE)
                    b = tk.Button(self, command=partial(self._make_move, (i,j)), highlightthickness=0, height=1, width=2, padx=0, pady=0)
                    b.grid(row=j+2, column=i,sticky='')
                    self.buttons[i].append(b)

            self._set_player(random.randrange(1,3))
            self.pieces = []
            self.board_images = []
            # make the board
            for r in range(board_size):
                self.board_images.append([])
                for c in range(board_size):
                    position = (c*SQUARE_SIZE + HALF_SQUARE, r*SQUARE_SIZE + HALF_SQUARE)
                    self.board_images[r].append({0: self.canvas.create_image(position, image=self.overlay_image),
                                                 1: self.canvas.create_image(position, image=self.piece1_image if self.current_player == 1 else self.piece2_image),
                                                 -1:self.canvas.create_image(position, image=self.piece2_image if self.current_player == 1 else self.piece1_image)
                                                 })
                    self.canvas.tag_raise(self.board_images[r][c][0])
                    
            # buttons

            

            
                    
        # actually make a play--modifies the board, and starts up the animation
        def _make_move(self, location, player_num = None):
            if player_num == None: player_num = self.current_player

            # disable all the buttons while the piece is dropping
            for b_row in self.buttons: 
                for b in b_row: 
                    b.config(state=tk.DISABLED)
            

            # create the new piece
            x,y = location
            self.board.make_move(x,y)
            temp_board = self.board.get_board()
            for i in range(self.board.size):
                for j in range(self.board.size):
                    self.canvas.tag_raise(self.board_images[i][j][temp_board[j][i]])
            self.after(1, self._finish_turn)
            


        # check for victory, swap player
        def _finish_turn(self):
            if self.board.game_is_over:
                self.resolve_game_end()
            else: self._swap_player()

        def resolve_game_end(self):
            winner = self.board.check_and_resolve_end()
            if winner is None:
                return
            if winner == 1:
                self.top_banner.config(text="Player 1 Wins!", fg=DEFAULT_PLAYER1_COLOR)
            elif winner == -1:
                self.top_banner.config(text="Player 2 Wins!", fg=DEFAULT_PLAYER2_COLOR)
            else:
                self.top_banner.config(text="Tie", fg="white")
            while True:
                pass

        # # handle the UI aspect of the victory
        # def _declare_victory(self, winner, win_location):
        #     self.top_banner.config(text="Player " +str(winner) + " wins!", fg=self.light_strs[self.current_player])
        #     num_rows = len(self.board[0])
        #     coords = [(x[0]*SQUARE_SIZE+HALF_SQUARE, (num_rows-1-x[1])*SQUARE_SIZE+HALF_SQUARE) for x in win_location]
        #     self.canvas.create_line(coords[0][0], coords[0][1], coords[1][0], coords[1][1], fill=self.light_strs[winner], width=SQUARE_SIZE/10, capstyle=tk.ROUND)

        # set a button to the colors of the given player
        def _set_button_colors(self, button, player):
            button.config(fg = self.dark_strs[player], bg = self.color_strs[player],
                          activeforeground=self.color_strs[player], activebackground=self.light_strs[player],
                          highlightcolor="#ff0000", disabledforeground=self.color_strs[player])

        # switch players
        def _swap_player(self):
            if self.current_player == 1: self._set_player(2)
            else: self._set_player(1)

        # change to the specified player
        def _set_player(self, player_id):
            score = self.board.score
            score_string = f"\tPieces Captured:(P1-P2): {score[1]}-{score[-1]}"
            self.current_player = player_id
            # if the next player is human, set the banner & activate the appropriate buttons
            if type(self.players[player_id]) == HumanPlayer:
                self.top_banner.config(text="Player " +str(self.current_player)+score_string, fg=self.color_strs[self.current_player])
                legal_moves = self.board.get_valid_moves()
                if len(legal_moves) == 0:
                    self.board.make_move()
                    self.resolve_game_end()
                    self._swap_player()
                for i,b_row in enumerate(self.buttons):
                    for j,button in enumerate(b_row):
                        if (i,j) in legal_moves:
                            button.grid()
                            self._set_button_colors(button, self.current_player)
                            button.config(state=tk.NORMAL)
                        else:
                            button.grid_remove()

            # if it's an AI, disable buttons & start up its turn
            else:
                self.top_banner.config(text="Player " +str(self.current_player)+ " is thinking..."+score_string, fg=self.color_strs[self.current_player])
                legal_moves = self.board.get_valid_moves()
                self.resolve_game_end()
                for i,b_row in enumerate(self.buttons):
                    for j,b in enumerate(b_row):
                        self._set_button_colors(b, self.current_player)
                        b.config(state=tk.DISABLED)
                        if (i,j) in legal_moves:
                            b.grid()
                        else:
                            b.grid_remove()

                self.after(50, self._do_computer_turn)

        # let the computer take a turn
        def _do_computer_turn(self):
            # pass the player a tuple (so it can't mess with the original board)
            board_tuple = self.board.get_board()
            valid_moves = self.board.get_valid_moves()
            x,y = self.players[self.current_player].pick_move(board_tuple, valid_moves)

            # checks to make sure that the AI has made a valid move
            assert self.board.make_move(x,y) == True
            
            self.top_banner.config(text="Player " +str(self.current_player))
            self._make_move((x,y))
            
        # take in a color string or tuple, return a tuple
        @staticmethod
        def _make_color_tuple(color, alpha=255):
            if type(color) == str:
                full_int = int(color.lstrip("#"), 16)
                red = full_int // 65536
                green = (full_int // 256) % 256
                blue = full_int % 256
                return (red, green, blue, alpha)
            if type(color) == tuple or type(color) == list:
                if len(color) == 3: return (color[0], color[1], color[2], 255)
                elif len(color) == 4: return tuple(color)

        # return a darker version of the passed color tuple
        @staticmethod
        def _darken(color):
            return (color[0]//2, color[1]//2, color[2]//2, color[3])

        # return a lighter version of the passed color tuple
        @staticmethod
        def _lighten(color):
            return ((color[0]+255)//2, (color[1]+255)//2, (color[2]+255)//2, color[3])

        # given a color tuple, return a string in the form "#rrggbb"
        @staticmethod
        def _make_color_string(color_tuple):
            return "#" +hex(256*65536 + 65536 * color_tuple[0] + 256 * color_tuple[1] + color_tuple[2])[3:]

        # make an image for one square in the board
        @staticmethod
        def _make_board_image():
            # start by making something double-size, so we can shrink it and get anti-aliasing
            im = Image.new("RGBA", (2*SQUARE_SIZE,2*SQUARE_SIZE), (0,0,0,0)) #(255,255,0,255))
            draw = ImageDraw.Draw(im)
            draw.rectangle((0, 0, 2*SQUARE_SIZE, 2*SQUARE_SIZE), fill='black')
            draw.rectangle((0, SQUARE_SIZE-1, SQUARE_SIZE*2, SQUARE_SIZE+1), fill='white')
            draw.rectangle((SQUARE_SIZE-1, 0, SQUARE_SIZE+1, SQUARE_SIZE*2), fill='white')
            return ImageTk.PhotoImage(im.resize((SQUARE_SIZE, SQUARE_SIZE), resample=Image.BICUBIC))

        # make a piece out of the passed color
        @staticmethod
        def _make_piece_image(color):
            im = Image.new("RGBA", (2*SQUARE_SIZE,2*SQUARE_SIZE), (0,0,0,0))
            draw = ImageDraw.Draw(im)

            color = App._make_color_tuple(color)
            dark = (color[0]//2, color[1]//2, color[2]//2, color[3])
            padding = SQUARE_SIZE* 0.1
            draw.ellipse((padding, padding, 2*SQUARE_SIZE-padding, 2*SQUARE_SIZE-padding), color, dark)
            draw.ellipse((SQUARE_SIZE//2, SQUARE_SIZE//2, 2*SQUARE_SIZE-SQUARE_SIZE//2, 2*SQUARE_SIZE-SQUARE_SIZE//2), None, dark)
            return ImageTk.PhotoImage(im.resize((SQUARE_SIZE, SQUARE_SIZE), resample=Image.BICUBIC))

        # make an 64x64 image of a "4" on a piece
        @staticmethod
        def _make_icon(color1, color2):
            im = Image.new("RGBA", (100,100), (0,0,0,0))
            draw = ImageDraw.Draw(im)
            draw.ellipse((0, 0, 100, 100), color2)
            draw.line(((53,93),(69,14),(21,62),(78,60)), fill=color1, width=12)
            return ImageTk.PhotoImage(im.resize((64, 64), resample=Image.BICUBIC))


################################################################################
# FUNCTIONS TODO: Remove or update for Go
################################################################################

def load_player(player_id, module_name = None, level = 1):
    """
    Load up a ComputerPlayer class from the given module. A module of None means 
    a human player.
    """
    class_name = "Player" +str(player_id)+ "Class"

    # if module_name is None, that means we have a human player
    if module_name == None:
        exec(class_name + " = HumanPlayer", globals())
        return HumanPlayer()

    # look for the file specified, see if we have a proper ComputerPlayer
    try:
        exec("from " +module_name+ " import ComputerPlayer as " +class_name, globals())
    except ImportError:
        print("Could not find ComputerPlayer in file \"" +module_name+ ".py\". Exiting.", file=sys.stderr)
        sys.exit(1)

    # make a local pointer to the ComputerPlayer class, and return a new instance
    exec("Player = " +class_name)
    return locals()["Player"](player_id, level)

def parse_command_line_args(args):
    """
    Search the command-line args for the various options (see the help function).
    """

    # print help message
    if "-h" in args or "--help" in args: print_help = True
    else: print_help = False

    # AI file
    if "-f" in args: ai_file = args[args.index("-f") + 1].rstrip(".py")
    else: ai_file = DEFAULT_AI_FILE
    
    # number of players
    if "-0" in args: players = (ai_file, ai_file)
    elif "-2" in args: players = (None, None)
    else: players = (None, ai_file)

    # level of players
    if "-l" in args:
        levels = args[args.index("-l") + 1].split(',')
        if len(levels) == 1: levels = (int(levels[0]), int(levels[0]))
        else: levels = (int(levels[0]), int(levels[1]))
    else: levels = (DEFAULT_AI_LEVEL, DEFAULT_AI_LEVEL)

    # colors
    if "-c" in args:
        color_string = args[args.index("-c") + 1]
        colors = color_string.split(',')
    else: colors = None
        
    # manually turn off the graphics
    if "-n" in args or "--nographics" in args: graphics_wanted = False
    else: graphics_wanted = True
    
    return (print_help, players, levels, colors, graphics_wanted)

def print_help(output = sys.stderr):
    """
    Print out a help screen for the user (probably to stderr).
    """
    
    print("Usage: python3 " +sys.argv[0]+ " <options>", file=output)
    print("Options include:", file=output)
    print("\t-0\t0-player (computer-v-computer)", file=output)
    print("\t-1\t1-player (human-v-computer)", file=output)
    print("\t-2\t2-player (human-v-human)", file=output)
    print("\t-c\tuse colors (RRGGBB,RRGGBB)", file=output)
    print("\t-f\tuse a non-standard AI file", file=output)
    print("\t-h\tprint this help", file=output)
    print("\t-l\tset AI level (#,#)", file=output)
    print("\t-n\tnon-graphics mode", file=output)

def play_game_in_ascii(player1, player2, board_size=NUM_SQUARES):
    """
    ASCII game. Boring. May not implement this.
    """
    board = Board(board_size)
    players = (None, player1, player2)

    current_player = random.randrange(1,3)
    winning_quartet = None

    while not winning_quartet:
        current_player = 3 - current_player
        if current_player == 1: player_escape = P1_ESCAPE
        else: player_escape = P2_ESCAPE

        # print out board state
        print(player_escape + "Player " + str(current_player) + ":" + END_ESCAPE)
        board.print_board()

        if type(players[current_player]) == HumanPlayer: move = do_human_turn(board, players[current_player])
        else: move = do_computer_turn(board, players[current_player])
        print()
        x,y = move
        board.make_move(x,y)
        winning_quartet = board.is_game_over

    board.print_ending_info()

def do_human_turn(board, player):
    while True:
        print("Your move? ", end="")
        user_input = input()
        try:
            column = int(user_input) - 1 # -1 for 0/1 based counting
        except ValueError:
            column = -1

        if column >= 0 and column < len(board) and board[column][-1] == 0: return column
        else: print("INVALID")
    
        
def do_computer_turn(board, player):
    # pass the player a tuple (so it can't mess with the original board)
    board_tuple = tuple([tuple(column) for column in board])
    valid_moves = board.get_valid_moves()
    move = player.pick_move(board_tuple, valid_moves)

    # checks to make sure that the AI has made a valid move
    assert move >=0 and move < len(board)
    assert board[move][-1] == 0

    return move
    


def exists_legal_move(board):
    return len(board.get_valid_moves()) != 0

    
