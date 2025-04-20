from .cluster import Cluster
from .safe_neighbor_check import safe_neighbor_check
from enum import Enum

class RejectReason(Enum):
    OOB = "space out of bounds"
    OCCUPIED = "space already occupied"
    SELF_CAP = "self capture violation"
    KO = "Ko violation"

class Board:
    def __init__(self, board_size, first_player = 1):
        self.game_is_over = False
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)] 
        self.size = board_size
        self.turn = first_player #1 for black, -1 for white.
        self.score = {1: 0, -1: 0}
        self.clusters = set() # a set contianing all the clusters
        self.ko_check = {1:Board.__hash_board_state(self.board), -1: Board.__hash_board_state(self.board)}
        self.saved_moves = None
        self.consecutive_passes = 0
        #TODO allow for a manually defined board state, and then

    def get_valid_moves(self):
        if self.saved_moves is None:
            self.__construct_move_list()
        valid_moves = []
        for move in self.saved_moves.keys():
            valid_moves.append(move)
        return valid_moves
    
    def make_move(self, x=None,y=None):
        if self.game_is_over:
            return False
        
        if x is None and y is None:
            self.consecutive_passes += 1
            self.ko_check[self.turn] = Board.__hash_board_state(self.board)
            self.turn *= -1
            return True
        if x is not None and y is not None:
            valid_moves = self.get_valid_moves()
            if (x,y) not in valid_moves:
                # invalid move
                return False
            score_delta, board, clusters = self.saved_moves[(x,y)]
            self.score[self.turn] += score_delta
            self.board = board
            self.clusters = clusters
            self.ko_check[self.turn] = Board.__hash_board_state(self.board)
            self.consecutive_passes = 0
            self.saved_moves = None
            self.turn *= -1
            return True
        else:
            #input 1 coordiante but not the other
            return False


        


    def __construct_move_list(self):
        self.saved_moves = {}
        for i in range(self.size):
            for j in range(self.size):
                valid_move, move_data = self.__get_move_data(i,j)
                if valid_move:
                    self.saved_moves[(i,j)] = move_data
                # elif move_data != RejectReason.OCCUPIED:
                #     print(f"move {(i,j)} rejected. Reason: {move_data.value}")           


    def __get_move_data(self, x, y):
        """given a move, returns the validity of the move alongside the game state to update to if that move is made"""
        if max(x,y) >= self.size or min(x,y) < 0:
            #out of bounds
            return (False, RejectReason.OOB)
        
        if self.board[x][y] != 0:
            #illegal_move: occupied square
            return (False, RejectReason.OCCUPIED)
        
        # copy self.board (this is a backup to revert to in case of a violation)
        backup_board = [self.board[i].copy() for i in range(self.size)]
        backup_clusters = set([cluster.copy(self.board) for cluster in self.clusters])

        # place piece on copy of board
        self.board[x][y] = self.turn
        
        # update allied clusters to combine with this piece

        # a list contianing all unique adjacent clusters
        adjacent_clusters = list(set(safe_neighbor_check(x, y, self.size, lambda x, y: self.__find_cluster_containing_sapce(x,y), lambda x,y: self.board[x][y] == self.turn)))
        if None in adjacent_clusters:
            adjacent_clusters.remove(None)
        
        if len(adjacent_clusters) > 0:
            root_cluster = adjacent_clusters[0]
            for i in range(1, len(adjacent_clusters)):
                root_cluster.combine_cluster(adjacent_clusters[i])
                self.clusters.remove(adjacent_clusters[i])
            # we add the piece at the end to ensure that the liberty doesn't get overwritten
            root_cluster.add_piece((x,y), self.board)
        else:
            #there are no allied adjacent clusters to the current space
            self.clusters.add(Cluster(self.board, (x,y)))
        
        



        # evaluate all adjacent enemy clusters to determine if they have any more remaining liberties'
        #print(f"potential move: {(x,y)}")
        score_deltas = safe_neighbor_check(x, y, self.size, lambda x, y: self.__check_and_process_cluster_capture(x,y), lambda x, y: self.board[x][y] == self.turn *-1)
        #print(score_deltas, end="\t")
        score_delta = 0
        for delta in score_deltas:
            score_delta += delta

        # if x+1 < self.size and self.board[x+1][y] == self.turn * -1:
        #     score_delta += self.__check_and_process_cluster_capture(x+1, y)
        # if x-1 >= 0 and self.board[x-1][y] == self.turn*-1:
        #     score_delta += self.__check_and_process_cluster_capture(x-1,y)
        # if y+1 < self.size and self.board[x][y+1] == self.turn * -1:
        #     score_delta += self.__check_and_process_cluster_capture(x, y+1)
        # if y-1 >= 0 and self.board[x][y-1] == self.turn * -1:
        #     score_delta += self.__check_and_process_cluster_capture(x, y-1)

        # evalute piece for self-capture. If it self-captures, reject and reveret to backup_board
        # print((x,y))
        # for cluster in self.clusters:
        #     print(cluster)
        # print("\n"+"-"*60)
        for cluster in self.clusters:
            if len(cluster.liberties) == 0:
                # for cluster in self.clusters:
                #     print(cluster)
                #self-capture violation

                #restore prior state
                self.board = backup_board
                self.clusters = backup_clusters
                return (False, RejectReason.SELF_CAP)

        # evalute simulation for ko violation (does it hash to the same value as the most recent state for the person's turn?)
        if Board.__hash_board_state(self.board) == self.ko_check[self.turn]:
            #ko violation (repetitive board states)
            self.board = backup_board
            self.clusters = backup_clusters
            return (False, RejectReason.KO)
        
        # valid move, still restore backup state
        update_state = (score_delta, self.board, self.clusters)
        self.board = backup_board
        self.clusters = backup_clusters
        return (True, update_state)


    def __find_cluster_containing_sapce(self, x, y):
        for cluster in self.clusters:
            if (x,y) in cluster.pieces:
                return cluster
        return None

    def __check_and_process_cluster_capture(self, x, y):
        target_cluster = None
        for cluster in self.clusters:
            if self.board[x][y] == self.turn *-1 and (x,y) in cluster.pieces:
                target_cluster = cluster
                break
        
        if target_cluster is not None:
            #self.print_board()
            #print(f"pre liberty update: {target_cluster}")
            target_cluster.update_liberties((x,y), self.board)
            #print(f"post liberty update: {target_cluster}")
            if target_cluster.is_captured((x,y), self.board):
                score_delta = len(target_cluster.pieces)
                self.clusters.remove(target_cluster)
                for x_1,y_1 in target_cluster.pieces:
                    self.board[x_1][y_1] = 0
                for cluster in self.clusters:
                    cluster.update_all_liberties(self.board)
                return score_delta
        return 0
    

    def __hash_board_state(board):
        return hash(tuple([tuple(row) for row in board]))
    
    def check_and_resolve_end(self):
        if self.consecutive_passes < 2:
            # game hasn't ended
            return
        for row in self.board:
            for piece in row:
                if piece != 0:
                    self.score[piece] += 1
        # 1 for black win, -1 for white win, 0 for tie.
        return 1 if self.score[1] > self.score[-1] else -1 if self.score[1] > self.score[-1] else 0

    
    def print_board(self):
        for row in self.board:
            for piece in row:
                print(" B " if piece == 1 else " W " if piece == -1 else " - ", end="")
            print("\n", end='')
    

    def count_open_spaces(self):
        open_spaces = 0
        for row in self.board:
            for square in row:
                if square == 0:
                    open_spaces += 1
        return open_spaces
    
    def get_board(self):
        return tuple([tuple(row) for row in self.board])

