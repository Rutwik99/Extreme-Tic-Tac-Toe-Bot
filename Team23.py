

import sys
import random
import signal
import time
import copy
import traceback
import numpy
from copy import deepcopy

class Team23:
    def __init__(self):
        self.weightage_matrix = [[3, 2, 3], [2, 4, 2], [3, 2, 3]]

        patt = []

        for i in range(2):
            patt.append(((i, 0, 0), (i, 1, 0), (i, 2, 0)))
            patt.append(((i, 0, 1), (i, 1, 1), (i, 2, 1)))
            patt.append(((i, 0, 2), (i, 1, 2), (i, 2, 2)))

            patt.append(((i, 0, 0), (i, 0, 1), (i, 0, 2)))
            patt.append(((i, 1, 0), (i, 1, 1), (i, 1, 2)))
            patt.append(((i, 2, 0), (i, 2, 1), (i, 2, 2)))

            patt.append(((i, 0, 0), (i, 1, 1), (i, 2, 2)))
            patt.append(((i, 0, 2), (i, 1, 1), (i, 2, 0)))

        self.patterns = patt
        self.blockPoints = 500



    def reverse_flag(self, flag):
        # NOT operation on flag
        if flag == 'x':
            return 'o'
        else:
            return 'x'

    def big_board_heuristic_func(self, small_boards_heuristic):
        boardHeur = 0
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if small_boards_heuristic[k][i][j] <= 0:
                    # if small_boards_heuristic[i][j] <= 0:
                        pass
                    else:
                        boardHeur += 0.02 * self.weightage_matrix[i][j] * small_boards_heuristic[k][i][j]
                        # boardHeur += 0.02 * self.weightage_matrix[i][j] * small_boards_heuristic[i][j]

        return boardHeur

    def big_board_pattern_checker(self, pattern, small_boards_heuristic):
        count_flag_symbols = 0
        count_reverse_flag_symbols = 0
        pattern_h = 0
        mult = 1

        for position in pattern:
            a, b, c = position
            temp = small_boards_heuristic[a][b][c]
            # temp = small_boards_heuristic[b][c]
            pattern_h += temp
            if temp < 0:
                return 0
            elif temp == self.blockPoints:
                count_flag_symbols += 1

        if count_flag_symbols == 2:
            mult = 20 # 2
        elif count_flag_symbols == 3:
            mult = 50
        # elif count_flag_symbols == 4:
        #     mult = 50

        return mult * pattern_h

    def small_board_heuristic_func(self, flag, small_board):
        small_heuristic = 0

        for pattern in self.patterns:
            small_heuristic += self.pattern_checker(flag,small_board,pattern)

        for i in range(3):
            for j in range(3):
                if small_board[i][j] == flag:
                    small_heuristic += 0.1 * self.weightage_matrix[i][j]

        return small_heuristic

    def pattern_checker(self, flag, small_board, pattern):
        count_flag_symbols = 0
        count_reverse_flag_symbols = 0

        for position in pattern:
            a, b, c = position
            if small_board[b][c] == flag:
                count_flag_symbols += 1
            # if small_board[b][c] == reverse_flag(flag):
            #     count_reverse_flag_symbols += 1
            elif small_board[b][c] == self.reverse_flag(flag):
                return 0
                # count_reverse_flag_symbols += 1
        if count_flag_symbols == 2:
            return 20 # 10
        # if count_reverse_flag_symbols  == 2:
        #     return 30
        # if count_flag_symbols == 2 and count_reverse_flag_symbols == 2:
        #     return 45
        return 0

    def heuristic(self, flag, board):

        total = 0
        total1 = 0

        small_boards = board.small_boards_status
        big_boards = board.big_boards_status
        small_boards_heuristic = [[[0,0,0],[0,0,0],[0,0,0]], [[0,0,0],[0,0,0],[0,0,0]]]

        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if small_boards[k][i][j]==flag:
                        small_boards_heuristic[k][i][j] = self.blockPoints
                    elif small_boards[k][i][j]==self.reverse_flag(flag) or small_boards[k][i][j]=='d':
                        small_boards_heuristic[k][i][j] = -1
                    else:
                        small_board = tuple([tuple(big_boards[k][3*i + x][3*j:3*(j+1)]) for x in range(3)])
                        small_boards_heuristic[k][i][j] = self.small_board_heuristic_func(flag,small_board)

        for pattern in self.patterns:
            total += self.big_board_pattern_checker(pattern,small_boards_heuristic)
            # total1 += self.big_board_pattern_checker(pattern,small_boards_heuristic[1])

        total += self.big_board_heuristic_func(small_boards_heuristic)
        # total += self.big_board_heuristic_func(small_boards_heuristic[0])
        # total1 += self.big_board_heuristic_func(small_boards_heuristic[1])

        # return max(total, total1)
        return total

    def minimax(self, board, flag, depth, max_depth, alpha, beta, prev_move, start_time):

        is_goal_state = board.find_terminal_state()

        if is_goal_state[1] == 'DRAW':
            return -100000, "nothing"
        elif is_goal_state[1] == 'WON' and is_goal_state[0] == self.curr:
                return numpy.inf, "nothing"
        elif is_goal_state[1] == 'WON':
            return -numpy.inf, "nothing"

        if depth == max_depth:
            maximise_heuristic = self.heuristic(self.curr, board)
            minimise_heuristic = self.heuristic(self.reverse_flag(self.curr), board)
            return ( maximise_heuristic - minimise_heuristic ) , "nothing"

        valid_moves = board.find_valid_move_cells(prev_move)

        if flag == self.curr:
            max_turn = 1
        else:
            max_turn = 0

        if max_turn:
            max_utility = -numpy.inf
            max_ind = 0
            for i in range(len(valid_moves)):

                unit = valid_moves[i]
                board.update(prev_move,unit,flag)

                # if (time.time() - start_time) > 23:
                #     return 0, "nthg"

                utility = self.minimax(board,self.reverse_flag(flag),depth+1,max_depth,alpha,beta,unit, start_time)[0]

                if utility > max_utility:
                    max_utility = utility
                    max_ind = i
                if max_utility > alpha:
                    alpha = max_utility

                board.big_boards_status[unit[0]][unit[1]][unit[2]] = '-'
                board.small_boards_status[unit[0]][unit[1]/3][unit[2]/3] = '-'

                if beta <= alpha:
                    break

                if (time.clock() - start_time) > 23:
                    return max_utility, valid_moves[max_ind]
            
            return max_utility, valid_moves[max_ind]

        else:
            min_utility = numpy.inf
            for i in range(len(valid_moves)):

                unit = valid_moves[i]
                board.update(prev_move,unit,flag)

                utility = self.minimax(board,self.reverse_flag(flag),depth+1,max_depth,alpha,beta,unit, start_time)[0]

                if utility < min_utility:
                    min_utility = utility
                if min_utility < beta:
                    beta = min_utility

                board.big_boards_status[unit[0]][unit[1]][unit[2]] = '-'
                board.small_boards_status[unit[0]][unit[1]/3][unit[2]/3] = '-'
                
                if beta <= alpha:
                    break

                if (time.clock() - start_time) > 23:
                    return min_utility, "nothing"
            
            return min_utility, "nothing"


    def move(self, board, prev_move, flag):
        if prev_move == (-1, -1, -1):
            return (0, 3, 3)

        self.curr = flag

        max_depth = 4

        valid_moves = board.find_valid_move_cells(prev_move)
        best_move = valid_moves[0]

        start_time = time.clock()

        # try:
        while (time.clock() - start_time) < 23:
            x = self.minimax(board,flag,0,max_depth,-numpy.inf,numpy.inf,prev_move, start_time)
            max_depth += 1
            best_move = x[1]
        

        return best_move