import random
from time import sleep
class ComputerPlayer:
    def __init__(self, id, difficulty_level):
        """
        Constructor, takes a difficulty level (likely the # of plies to look
        ahead), and a player ID that's either 1 or 2 that tells the player what
        its number is.
        """
        self.id = id
        self.difficulty = difficulty_level
        pass

    def pick_move(self, board, valid_moves):
        """
        Pick the move to make. It will be passed a rack with the current board
        layout, column-major. A 0 indicates no token is there, and 1 or 2
        indicate discs from the two players. Column 0 is on the left, and row 0 
        is on the bottom. It must return an int indicating in which column to 
        drop a disc. The player current just pauses for half a second (for 
        effect), and then chooses a random valid move.
        """
        #time.sleep(0.5) # pause purely for effect--real AIs shouldn't do this
        # print(ComputerPlayer.__evaluate_state(rack, self.id))
        # while True:
        #     play = random.randrange(0, len(rack))
        #     if rack[play][-1] == 0: return play
           
        sleep(0.2)
        if len(valid_moves) == 0:
            return (None, None)
        return valid_moves[random.randrange(len(valid_moves))]


