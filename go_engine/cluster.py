from .safe_neighbor_check import safe_neighbor_check
class Cluster:
    def __init__(self, board, square = None, pieces = None, liberties = None):
        self.board_size = len(board)
        if pieces is None and liberties is None and square is not None:
            self.pieces = set()
            self.liberties = set()
            self.pieces.add(square)
            self.update_liberties(square, board)
        elif pieces is not None and liberties is not None:
            self.pieces = pieces.copy()
            self.liberties = liberties.copy()
        else:
            #error
            print("error")
            pass
        


    def add_piece(self, square, board):
        if square not in self.liberties:
            return
        self.liberties.remove(square)
        self.pieces.add(square)
        self.update_liberties(square, board)
    
    def update_liberties(self, square, board):
        x,y = square
        safe_neighbor_check(x, y, self.board_size, lambda x,y: self.update_liberty(x,y, board))
        # if x+1 < self.board_size and self.board[x+1][y] == 0:
        #     self.liberties.add((x+1,y))
        # if x-1 >= 0 and self.board[x-1][y] == 0:
        #     self.liberties.add((x-1,y))
        # if y+1 < self.board_size and self.board[x][y+1] == 0:
        #     self.liberties.add((x,y+1))
        # if y-1 >= 0 and self.board[x][y+1] == 0:
        #     self.liberties.add((x,y-1))

    def update_liberty(self, x, y, board):
        if board[x][y] == 0:
            self.liberties.add((x,y))
        else:
            arbX, arbY = next(iter(self.pieces))
            if board[arbX][arbY] == -1* board[x][y] and (x,y) in self.liberties:
                self.liberties.remove((x,y))
    
    def update_all_liberties(self, board):
        for square in self.pieces:
            self.update_liberties(square, board)
    
    def copy(self, board):
        return Cluster(board, pieces = self.pieces.copy(), liberties = self.liberties.copy())
    
    def is_captured(self, square, board):
        """given a square, updates the liberties for that square being taken, then checks if the cluster has no liberties"""
        self.update_liberties(square, board)
        return len(self.liberties) == 0
    
    def combine_cluster(self, other):
        """given a 2nd cluster, combines the 2 clusters
        ASSUMPTION: the clusters are compatible. Will not actually check to ensure this is the case"""
        for piece in other.pieces:
            self.pieces.add(piece)
        for liberty in other.liberties:
            self.liberties.add(liberty)
    
    def __str__(self):
        return "{"+f"pices: {self.pieces}\tliberties:{self.liberties}"+"}"