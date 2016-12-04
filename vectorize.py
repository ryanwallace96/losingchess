import chess
import losing_board

# this case handles promotions easily
def square_vector(board):
    board_type = board.__class__.__name__
    out_vec = []
    all_squares = chess.SquareSet(chess.BB_ALL)
    for square in all_squares:
        piece = board.piece_at(square)
        if piece is None:
            out_vec.append(0)
        elif piece.symbol() == 'P':
            out_vec.append(1)
        elif piece.symbol() == 'p':
            out_vec.append(2)
        elif piece.symbol() == 'N':
            out_vec.append(3)
        elif piece.symbol() == 'n':
            out_vec.append(4)
        elif piece.symbol() == 'B':
            out_vec.append(5)
        elif piece.symbol() == 'b':
            out_vec.append(6)
        elif piece.symbol() == 'R':
            out_vec.append(7)
        elif piece.symbol() == 'r':
            out_vec.append(8)
        elif piece.symbol() == 'Q':
            out_vec.append(9)
        elif piece.symbol() == 'q':
            out_vec.append(10)
        elif piece.symbol() == 'K':
            out_vec.append(11)
        elif piece.symbol() == 'k':
            out_vec.append(12)

    # en passant rights
    if board.has_legal_en_passant():
        if board_type == 'LosingBoard':
            out_vec.append(board.ep_square())
        else:
            out_vec.append(board.ep_square)
    else:
        out_vec.append(0)

    # turn
    if board_type == 'LosingBoard':
        out_vec.append(int(board.turn()))
    else:
        out_vec.append(int(board.turn))
    
    return out_vec

# promotions much more difficult here
# instead of full encoding of promotions, we follow Lai and use piece counts
def piece_vector(board):
    board_type = board.__class__.__name__
    out_vec = []
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    white_counts = [0] * 6
    black_counts = [0] * 6

    white_attacked = 0
    black_attacked = 0

    for ptype in piece_types:
        white_set = board.pieces(ptype, chess.WHITE)
        black_set = board.pieces(ptype, chess.BLACK)
        
        # encode existence and type of promotions by piece counts but not locations
        white_counts[ptype - 1] = len(white_set)
        black_counts[ptype - 1] = len(black_set)

        if ptype == chess.PAWN: 
            if len(white_set) > 8:
                white_set = list(white_set)[:8]
            if len(black_set) > 8:
                black_set = list(black_set)[:8] 

            for p_square in white_set:
                out_vec.append(p_square + 1)
            out_vec += [0] * (8 - len(white_set))
            for p_square in black_set:
                out_vec.append(p_square + 1)
            out_vec += [0] * (8 - len(black_set))
        elif ptype == chess.KNIGHT:
            if len(white_set) > 2:
                white_set = list(white_set)[:2]
            if len(black_set) > 2:
                black_set = list(black_set)[:2]

            if len(white_set) > 8:
                white_set = white_set[:8] 
            for n_square in white_set:
                out_vec.append(n_square + 1)
            out_vec += [0] * (2 - len(white_set))
            for n_square in black_set:
                out_vec.append(n_square + 1)
            out_vec += [0] * (2 - len(black_set))
        elif ptype == chess.BISHOP:
            if len(white_set) > 2:
                white_set = list(white_set)[:2]
            if len(black_set) > 2:
                black_set = list(black_set)[:2]

            for b_square in white_set:
                out_vec.append(b_square + 1)
            out_vec += [0] * (2 - len(white_set))
            for b_square in black_set:
                out_vec.append(b_square + 1)
            out_vec += [0] * (2 - len(black_set))
        elif ptype == chess.ROOK:
            if len(white_set) > 2:
                white_set = list(white_set)[:2]
            if len(black_set) > 2:
                black_set = list(black_set)[:2]

            for r_square in white_set:
                out_vec.append(r_square + 1)
            out_vec += [0] * (2 - len(white_set))
            for r_square in black_set:
                out_vec.append(r_square + 1)
            out_vec += [0] * (2 - len(black_set))
        elif ptype == chess.QUEEN:
            if len(white_set) > 1:
                white_set = list(white_set)[:1]
            if len(black_set) > 1:
                black_set = list(black_set)[:1]

            for q_square in white_set:
                out_vec.append(q_square + 1)
            out_vec += [0] * (1- len(white_set))
            for q_square in black_set:
                out_vec.append(q_square + 1)
            out_vec += [0] * (1 - len(black_set))
        else:
            if len(white_set) > 1:
                white_set = list(white_set)[:1]
            if len(black_set) > 1:
                black_set = list(black_set)[:1]

            for k_square in white_set:
                out_vec.append(k_square + 1)
            out_vec += [0] * (1 - len(white_set))
            for k_square in black_set:
                out_vec.append(k_square + 1)
            out_vec += [0] * (1 - len(black_set))

        for square in white_set:
            if board.is_attacked_by(chess.BLACK, square):
                white_attacked += 1

        for square in black_set:
            if board.is_attacked_by(chess.WHITE, square):
                black_attacked += 1

    # number of pieces on each side under attack
    out_vec.append(white_attacked)
    out_vec.append(black_attacked)

    # promotions via piece counts
    out_vec += white_counts
    out_vec += black_counts

    # en passant rights
    if board.has_legal_en_passant():
        if board_type == 'LosingBoard':
            out_vec.append(board.ep_square())
        else:
            out_vec.append(board.ep_square)
    else:
        out_vec.append(0)

    # turn
    if board_type == 'LosingBoard':
        out_vec.append(int(board.turn()))
    else:
        out_vec.append(int(board.turn))

    return out_vec

def piece_vector_len():
    board = losing_board.LosingBoard()
    vec = piece_vector(board)
    return len(vec)

def piece_count_vector(board):
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    white_counts = [0] * 6
    black_counts = [0] * 6
    for ptype in piece_types:
        # find the number of white and black pieces of each type
        white_set = board.pieces(ptype, chess.WHITE)
        black_set = board.pieces(ptype, chess.BLACK)

        white_counts[ptype - 1] = len(white_set)
        black_counts[ptype - 1] = len(black_set)

    # the final vectorization lists the number of white pieces of each type
    # followed by the number of black pieces of each type
    out_vec = white_counts + black_counts
    return out_vec

def piece_count_vector_len():
    board = losing_board.LosingBoard()
    vec = piece_count_vector(board)
    return len(vec)
