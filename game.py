import sys
import chess
import losing_board
import chess_agents
import evaluation
import time

"""
Here we will build the processes that drive games between two AIs,
and games between an AI and a human.

Perhaps we'll use command line arguments to select agent types,
evaluation functions, number of AIs, a la Berkeley.
"""

board = losing_board.LosingBoard(no_kings=True)
a1 = chess_agents.RandomAgent(color=chess.WHITE, eval_func=evaluation.weighted_piece_count)
a2 = chess_agents.AlphaBetaAgent(color=chess.BLACK, eval_func=evaluation.weighted_piece_count, depth='2')

while True:

	turn = False
	draw = False
	for agent in [a1,a2]:
		mv = agent.getMove(board)
		board.move(mv)
		print "Agent " + str(turn + 1) + " makes move: "+ str(mv)
		print board
		print

		turn = not turn

		if board.isGameOver():
			print 
			print "Agent 1 victorious!"
			break
		if board.isDraw():
			print "It's a draw in " + str(board.board.fullmove_number) + " plies."
			print
			draw = True
			break
	
	if draw: break

