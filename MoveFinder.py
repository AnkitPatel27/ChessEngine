import random
import timeit

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 5, "N": 3, "P": 1}
# here King score is zero bcz king will stay in the game no matter what

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
transpositionTable = {}

def orderMoves(gs,validMoves):
    def move_value(move):
        if move.pieceCaptured != "--":   #en passant covered as it changes the move.pieceCaptured
            return 10 * pieceScore[move.pieceCaptured[1]] - pieceScore[move.pieceMoved[1]]
        elif move.isPawnPromotion:
            return 9
        elif gs.givesCheck(move):  #TODO: implement the function gives check
            return 8
        return 0

    return sorted(validMoves, key=move_value, reverse=True)



def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    maxScore = -CHECKMATE if gs.whiteToMove else CHECKMATE
    bestMove = None

    for playerMove in validMoves:
        gs.makeMove(playerMove)
        score = 0
        if gs.checkMate:
            score = CHECKMATE if gs.whiteToMove else -CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            score = findScore(gs.board)

        # print("score ",score,maxScore,(not gs.whiteToMove) , score<maxScore)

        if (not gs.whiteToMove) and score > maxScore:
            maxScore = score
            bestMove = playerMove

        if (gs.whiteToMove) and score < maxScore:
            print(score, "max score updated")
            maxScore = score
            bestMove = playerMove

        gs.undoMove()

    return bestMove


def findBestNMove(gs, validMoves):
    global nextMove,counter
    nextMove = None
    counter = 0
    # findBestMinMaxMove(gs, validMoves, DEPTH, gs.whiteToMove)
    # print(nextMove)
    # nextMove = None
    # start_time = timeit.default_timer()
    # negaMax(gs,validMoves,DEPTH,gs.whiteToMove)
    # end_time = timeit.default_timer()
    # execution_time = end_time - start_time
    # print(execution_time)
    # print(counter)

    counter=0
    nextMove = None
    start_time = timeit.default_timer()
    alphaBetaPruning(gs,validMoves,DEPTH,gs.whiteToMove,-CHECKMATE,CHECKMATE)
    end_time = timeit.default_timer()
    execution_time = end_time - start_time
    print(execution_time)
    print(counter)
    return nextMove


def findBestMinMaxMove(gs, validMoves, depth, whiteToMove):
    global nextMove

    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        # random.shuffle(validMoves)
        for move in validMoves:
            score = -CHECKMATE
            gs.makeMove(move)
            score = findBestMinMaxMove(gs, gs.getAllValidMoves(), depth - 1, False)

            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()
        return maxScore

    if not whiteToMove:
        minScore = CHECKMATE
        random.shuffle(validMoves)
        for move in validMoves:
            score = CHECKMATE
            gs.makeMove(move)
            score = findBestMinMaxMove(gs, gs.getAllValidMoves(), depth - 1, True)

            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()
        return minScore


def negaMax(gs,validMoves,depth,whiteToMove):
    global nextMove,counter
    if depth == 0:
        counter+=1
        return scoreBoard(gs) if whiteToMove else -scoreBoard(gs)

    maxScore = -CHECKMATE
    # random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        score = -1*negaMax(gs, gs.getAllValidMoves(), depth - 1, not whiteToMove)
        if score > maxScore:
            maxScore = score
            if depth==DEPTH:
                nextMove = move

        gs.undoMove()

    return maxScore

def alphaBetaPruning(gs,validMoves,depth,whiteToMove,alpha,beta):
    global nextMove,counter

    if depth == 0:
        counter+=1
        return scoreBoard(gs) if whiteToMove else -scoreBoard(gs)

    maxScore = -CHECKMATE
    # random.shuffle(validMoves)
    orderMoves(gs,validMoves)
    for move in validMoves:
        gs.makeMove(move)
        score = -1*alphaBetaPruning(gs, gs.getAllValidMoves(), depth - 1, not whiteToMove,-1*beta,-1*alpha)
        gs.undoMove()
        if score >= beta:
            return score
        if score > maxScore:
            maxScore = score
            alpha = max(alpha,score)
            if depth==DEPTH:
                nextMove = move

    return maxScore

def checkOrStale(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # because if its white turn to move and its already in checkmate then its worst senario for white
        else:
            return CHECKMATE  # same as above
    elif gs.staleMate:
        return STALEMATE


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  #because if its white turn to move and its already in checkmate then its worst senario for white
        else:
            return CHECKMATE  #same as above
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for r in range(len(gs.board)):
        for c in range(len(gs.board[0])):
            if gs.board[r][c] != '--':
                mult = 1 if gs.board[r][c][0] == 'w' else -1
                score = score + mult * pieceScore[gs.board[r][c][1]]
    return score


def findScore(board):
    score = 0
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] != '--':
                mult = 1 if board[r][c][0] == 'w' else -1
                score = score + mult * pieceScore[board[r][c][1]]
    return score


