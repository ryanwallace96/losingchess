import chess
import losing_board
import random
import time
import copy_reg
import types
from functools import partial
from multiprocessing import Pool

class Agent:
    """
    Parent class for all agents. Agents must be able to return a move
    given a game_state
    """
    def __init__(self, eval_func, ant_eval_func, color=chess.WHITE, depth=1, parallelize=False):
        self.color = color
        self.eval_func = eval_func
        self.depth = depth - 1
        self.ant_eval_func = ant_eval_func
        self.parallelize = parallelize
        if self.depth < 0:
            raise Exception("Depth must be >= 0")

    def get_move(self, game_state):
        raise Exception("Undefined!")

class HumanAgent(Agent):
    """
    The agent that takes a move from std in
    """
    def get_move(self, game_state):
        moves = game_state.board.get_legal_moves()
        if len(moves) == 0:
            return None
        else:
            while True:
                move_string = raw_input('Enter your move: ')
                if move_string == 'moves':
                    print 'Possible moves:'
                    for move in moves:
                        print str(move)
                else:
                    try:
                        move = chess.Move.from_uci(move_string)
                        if move in moves:
                            return move
                        else:
                            print 'Invalid move. Try again.'
                    except:
                        print 'Invalid move. Try again.'

class RandomAgent(Agent):
    """
    Agent that chooses a move uniformly from available moves
    """
    def get_move(self, game_state):
        moves = game_state.board.get_legal_moves()
        print len(moves)
        if len(moves) == 0:
            return None
        else:
            move = random.sample(moves, 1)[0]
            return move

"""
Necessary code for running a class method in parallel.
Essentially, tells python how to convert a method that is built into a class 
to a standalone binary file (since this is necessary for multiprocesing).

citation: dano, http://stackoverflow.com/questions/25156768
          /cant-pickle-type-instancemethod-using-pythons-multiprocessing-pool-apply-a
"""
def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

class MinimaxAgent(Agent):
    """
    Agent that returns the minimax optimal move according to the evaluation function
    (no pruning or parallelization)
    """
    def get_move(self, game_state, return_value=False):
        """
        Return minimax move using self.depth and self.eval_func.
        """
        moves = game_state.board.get_legal_moves()
        if len(moves) == 0:
            return None

        values = {}
        for move in moves:
            values[move] = self.get_value(move, game_state.board, 0, self.color)

        # return action with max utility,
        # random action if there's a tie
        best_val = max(values.values())
        best_actions = []
        for k, v in values.iteritems():
            if v == best_val:
                best_actions.append(k)
        best_action = random.sample(best_actions, 1)[0]
        if return_value:
            return (best_action, best_val)
        else:
            return best_action

    def get_value(self, move, board, depth, color):
        """
        Helper function for performing expectimax.
        """
        # get next game state
        next_state = board.generate_successor(move)

        # has agent won?
        if next_state.is_game_over():
            return 99999

        # does agent move next?
        next_color = not color

        # has max depth been reached?
        if depth == self.depth:
            return self.eval_func(next_state, color)

        # get information about next state
        next_moves = next_state.get_legal_moves()

        # if this agent is to move
        if next_color == self.color: 

            # increment depth
            depth += 1

            # if we've reached a terminal state
            # update alpha and return terminal value
            if next_moves == []:
                term_val = self.eval_func(next_state, next_color)
                return term_val

            # find next action with max utility
            v = -99999
            for mv in next_moves:
                mvValue = self.get_value(mv, next_state, depth, next_color)
                v = max(v, mvValue)
            return v

        # if opponent is to move
        else:
            # if we've reached a terminal state
            # return terminal value without updating alpha/beta
            if next_moves == []:
                term_val = self.eval_func(next_state, next_color)
                return term_val

            # find next action with minimum utility
            v = 99999
            for mv in next_moves:
                mvValue = self.get_value(mv, next_state, depth, next_color)
                v = min(v, mvValue)
            return v

class AlphaBetaAgent(Agent):
    """
    Agent that returns the minimax move using alpha-beta pruning
    """
    def get_move(self, game_state, return_value=False):
        """
        Return minimax move using self.depth, self.eval_func, and alpha-beta pruning.
        """
        moves = game_state.board.get_legal_moves()
        if len(moves) == 0:
            return None

        if self.parallelize:
            get_ab_value = partial( self._alpha_beta_value, board=game_state.board,
                                    alpha=-99999, beta=99999, depth=0,
                                    color=self.color)

            p = Pool(8)
            values = p.map_async(get_ab_value, moves).get(99999)
            p.terminate()

            values = {mv: v for mv, v in zip(moves, values)}

        else:
            values = {}
            for move in moves:
                values[move] = self._alpha_beta_value(move, game_state.board, alpha=-99999, beta=99999, 
                                                      depth=0, color=self.color)

        # return action with max utility,
        # random action if there's a tie
        best_val = max(values.values())
        best_actions = []
        for k, v in values.iteritems():
            if v == best_val:
                best_actions.append(k)
        best_action = random.sample(best_actions, 1)[0]
        if return_value:
            return (best_action, best_val)
        else:
            return best_action


    def _alpha_beta_value(self, move, board, alpha, beta, depth, color):
        """
        Helper function for performing alpha-beta pruning.
        """
        # get next game state
        next_state = board.generate_successor(move)

        # has agent won?
        if next_state.is_game_over():
            return 99999

        # does agent move next?
        next_color = not color

        # has max depth been reached?
        if depth == self.depth:
            return self.eval_func(next_state, color)

        # get information about next state
        next_moves = next_state.get_legal_moves()

        # if this agent is to move
        if next_color == self.color:

            # increment depth
            depth += 1

            # if we've reached a terminal state
            # update alpha and return terminal value
            if next_moves == []:
                term_val = self.eval_func(next_state, next_color)
                alpha = max(alpha, term_val)
                return term_val

            # find next action with max utility
            v = -99999
            for mv in next_moves:
                mvValue = self._alpha_beta_value(mv, next_state, alpha, beta, depth, next_color)
                v = max(v, mvValue)
                # prune if value is great enough
                if v >= beta:
                    return v
            alpha = max(alpha, v)
            return v

        # if opponent is to move
        else:
            # if we've reached a terminal state
            # return terminal value without updating alpha/beta
            if next_moves == []:
                term_val = self.ant_eval_func(next_state, next_color)
                return term_val

            # find next action with min utility
            v = 99999
            for mv in next_moves:
                mvValue = self._alpha_beta_value(mv, next_state, alpha, beta, depth, next_color)
                v = min(v, mvValue)
                #prune if value is small enough
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

class ExpectimaxAgent(Agent):
    """
    Returns the expectimax value according to the evaluation function 
    """
    def get_move(self, game_state, return_value=False):
        moves = game_state.board.get_legal_moves()
        if len(moves) == 0:
            return None

        values = {}
        for move in moves:
            values[move] = self.get_value(move, game_state.board, 0, self.color)

        # return action with max utility,
        # random action if there's a tie
        best_val = max(values.values())
        best_actions = []
        for k, v in values.iteritems():
            if v == best_val:
                best_actions.append(k)
        best_action = random.sample(best_actions, 1)[0]
        if return_value:
            return (best_action, best_val)
        else:
            return best_action

    def get_value(self, move, board, depth, color):
        """
        Helper function for performing expectimax.
        """
        # get next game state
        next_state = board.generate_successor(move)

        # has agent won?
        if next_state.is_game_over():
            return 99999

        # does agent move next?
        next_color = not color

        # has max depth been reached?
        if depth == self.depth:
            return self.eval_func(next_state, color)

        # get information about next state
        next_moves = next_state.get_legal_moves()

        # if this agent is to move
        if next_color == self.color: 

            # increment depth
            depth += 1

            # if we've reached a terminal state
            # update alpha and return terminal value
            if next_moves == []:
                term_val = self.eval_func(next_state, next_color)
                return term_val

            # find next action with max utility
            v = -99999
            for mv in next_moves:
                mvValue = self.get_value(mv, next_state, depth, next_color)
                v = max(v, mvValue)
            return v

        # if opponent is to move
        else:
            # if we've reached a terminal state
            # return terminal value without updating alpha/beta
            if next_moves == []:
                term_val = self.eval_func(next_state, next_color)
                return term_val

            # find next expected utility of next action
            # p is the uniform probability of this action
            p = 1.0 / float(len(next_moves))
            v = 0
            for mv in next_moves:
                mvValue = self.get_value(mv, next_state, depth, next_color)
                v += p * mvValue
            return v
