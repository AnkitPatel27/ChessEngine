# responsible for all moves logging and current state
# all logical stuff like finding valid moves

# P pawn
# R Rook
# N Knight
# Q Queen
# K King
# B bishop

class GameState:
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
                      ]
        self.moveFunctions = {'P': self.getAllPawnMoves, "R": self.getAllRookMoves, "N": self.getAllKnightMoves
            , "K": self.getAllKingMoves, "Q": self.getAllQueenMoves, "B": self.getAllBishopMoves}
        self.whiteToMove = True
        self.moveLog = []

        # validating Moves
        self.pinned = []
        self.isCheck = False
        self.checks = []    #(position of piece that gives checks,direction from which checks comes from kings perspective)
        self.blackKingLocation = (0,4)
        self.whiteKingLocation = (7,4)

        # for enpassant moves
        self.enPassantSquare = ()
        self.enPassantSquareLog = []
        self.enPassantSquareLog.append(self.enPassantSquare)

        # for castling moves
        self.castlingState = {"bks":True,"wks":True,"bqs":True,"wqs":True}
        self.castlingStateLog = []
        self.castlingStateLog.append(dict(self.castlingState))


        # checkmate and stalemate
        self.checkMate = False
        self.staleMate = False

    # take position and makes move
    # ToDO : castling , pawn promotion and ex-passant
    def makeMove(self, move):
        self.board[move.startR][move.startC] = "--"
        self.board[move.endR][move.endC] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # updating king location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endR,move.endC)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endR, move.endC)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endR][move.endC] = move.pieceMoved[0]+'Q'


        #enPassant Sqaure
        if move.pieceMoved[1] == 'P' and abs(move.endR-move.startR)==2:
            self.enPassantSquare = ((move.endR+move.startR)//2,move.endC)
        else: #resetting enpassant square when pawn is not moved
            self.enPassantSquare = ()
        self.enPassantSquareLog.append(self.enPassantSquare)

        #is enPassant Move
        if move.isEnPassant:
            self.board[move.startR][move.endC] = "--"

        # is castleMove
        if move.isCastle:
            if (move.endC - move.startC )== 2:
                self.board[move.endR][move.endC-1] = self.board[move.endR][move.endC+1]
                self.board[move.endR][move.endC + 1] = '--'
            else:
                self.board[move.endR][move.endC+1] = self.board[move.endR][move.endC-2]
                self.board[move.endR][move.endC -2] = '--'


        # change castle state if needed
        if move.pieceMoved[1]=='K':
            self.castlingState[move.pieceMoved[0]+'ks'] = False
            self.castlingState[move.pieceMoved[0]+'qs'] = False
        elif move.pieceMoved[1]=='R':
            if move.startC==0:
                self.castlingState[move.pieceMoved[0]+'qs'] = False
            if move.startC==7:
                self.castlingState[move.pieceMoved[0]+'ks'] = False
        elif move.pieceCaptured[1]=='R':
            if move.endC==0:
                self.castlingState[move.pieceMoved[0]+'qs'] = False
            if move.endC==7:
                self.castlingState[move.pieceMoved[0]+'ks'] = False

        self.castlingStateLog.append(dict(self.castlingState))

    # undoes the last valid move made using the moveLog
    def undoMove(self):
        if len(self.moveLog) != 0:
            self.whiteToMove = not self.whiteToMove
            lastMove = self.moveLog.pop()
            self.board[lastMove.startR][lastMove.startC] = lastMove.pieceMoved
            self.board[lastMove.endR][lastMove.endC] = lastMove.pieceCaptured

            # updating king location
            if lastMove.pieceMoved == 'wK':
                self.whiteKingLocation = (lastMove.startR, lastMove.startC)
            if lastMove.pieceMoved == 'bK':
                self.blackKingLocation = (lastMove.startR, lastMove.startC)

            #undoing EnPassant move
            if lastMove.isEnPassant:
                self.board[lastMove.endR][lastMove.endC] = '--'
                self.board[lastMove.startR][lastMove.endC] = lastMove.pieceCaptured

            self.enPassantSquareLog.pop()
            self.enPassantSquare = self.enPassantSquareLog[-1]


            #undoing castle Move
            if lastMove.isCastle:
                if (lastMove.endC - lastMove.startC) == 2:
                    self.board[lastMove.endR][lastMove.endC + 1] = self.board[lastMove.endR][lastMove.endC - 1]
                    self.board[lastMove.endR][lastMove.endC - 1] = '--'
                else:
                    self.board[lastMove.endR][lastMove.endC - 2] = self.board[lastMove.endR][lastMove.endC + 1]
                    self.board[lastMove.endR][lastMove.endC + 1] = '--'

            #undoing Castling state
            self.castlingStateLog.pop()
            self.castlingState = dict(self.castlingStateLog[-1])

            self.checkMate = False
            self.staleMate = False

    # all moves that are valid considering check
    def getAllValidMoves(self):
        moves = []
        self.isCheck,self.pinned,self.checks = self.checkForPinsAndChecks()

        kingRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        kingCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]

        if self.isCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # either block the check or move the king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] # squares on which a piece would come and block a check

                if pieceChecking[1] == "N": #if Knight either capture knight or move king
                    validSquares.append((checkRow,checkCol))
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i,kingCol+check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:
                            break #includes the piece in validSquare that causes the check

                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1]!='K':
                        if not (moves[i].endR,moves[i].endC) in validSquares:
                            moves.remove(moves[i])

            else: #double or more check means king has to move
                self.getAllKingMoves(kingRow,kingCol,moves)
        else: # here you can think what if king moves to a check position ,that is taken in care of in function moveKing()
            moves = self.getAllPossibleMoves()

        if self.isCheck and len(moves)==0:
            self.checkMate = True
        if not self.isCheck and len(moves)==0:
            self.staleMate = True

        return moves
    def checkForPinsAndChecks(self):
        pins = [] # square where allied pieces are pinned and their direction
        checks = [] #sqaure where enemy pieces can apply checks
        isCheck = False
        enemyColor = 'b' if self.whiteToMove else 'w'
        allyColor = 'w' if self.whiteToMove else 'b'
        startR = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        startC = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]

        direction = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

        for j in range(len(direction)):
            d = direction[j]
            possiblePin = ()

            for i in range(1,8):
                endR = startR + d[0]*i
                endC = startC + d[1]*i

                if (0<=endC<=7 and 0<=endR<=7):
                    endPiece = self.board[endR][endC]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        # != 'K  bcz of use of this func in allKingMoves()
                        if len(possiblePin) == 0:
                            possiblePin = (endR,endC,d[0],d[1])
                        else: # 2nd allied piece means no further pins and checks possible
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0<=j<=3 and type=='R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type=='P' and ((enemyColor=='b' and 4<=j<=5) or (enemyColor=='w' and 6<=j<=7))) or \
                                (type == 'Q') or (i==1 and type == 'K'):
                            if possiblePin==():
                                isCheck = True
                                checks.append((endR,endC,d[0],d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break  # if any black that cant attack king
                else:
                    break

        # for knight checks and for this there can be no pinned piece
        knightMoves =  [(2,1),(2,-1),(1,2),(-1,2),(-2,1),(-2,-1),(1,-2),(-1,-2)]
        for m in knightMoves:
            endR = startR + m[0]
            endC = startC + m[1]
            if 0<=endR<=7 and 0<=endC<=7:
                endPiece = self.board[endR][endC]
                if  endPiece[0] == enemyColor and endPiece[1] == 'N':
                    isCheck = True
                    checks.append((endR,endC,m[0],m[1]))

        return isCheck,pins,checks

    def checkSquareUnderAttack(self,r,c):
        enemyColor = 'b' if self.whiteToMove else 'w'
        allyColor = 'w' if self.whiteToMove else 'b'
        dir = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for i in range(len(dir)):
            for j in range(1,8):
                x = r+j*dir[i][0]
                y = c+j*dir[i][1]
                if 0<=x<=7 and 0<=y<=7:
                    piece = self.board[x][y][1]
                    pieceColor = self.board[x][y][0]
                    if self.board[x][y][0] == enemyColor:
                        if (i<=3 and piece=='R') or (piece=='B' and 4<=i<=7) or (piece=='K' and j==1) or (piece=='Q') or (piece=='P' and j==1 and ((pieceColor=='b' and i>=6) or (pieceColor=='w' and 4<=i<=5))):
                            return True
                    elif self.board[x][y][0] == allyColor:
                        break
                else:
                    break

        return False
    # all moves possible
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                color = self.board[r][c][0]

                if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves

    # pawn promotion
    def getAllPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pinned)-1,-1,-1):
            curPin = self.pinned[i]
            if r == curPin[0] and c == curPin[1]:
                piecePinned = True
                pinDirection = (curPin[2],curPin[3])
                self.pinned.remove(curPin)
                break

        # calculating all the moves
        if self.whiteToMove:
            if r - 1 >= 0 and self.board[r - 1][c] == '--':
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if r-1>=0 and c-1>=0 and (self.board[r-1][c-1][0]=='b' or self.enPassantSquare==(r-1,c-1)):
                if not piecePinned or pinDirection == (-1,-1):
                    moves.append(Move((r, c), (r - 1, c-1), self.board,isEnPassant=(self.enPassantSquare==(r-1,c-1))))
            if r-1>=0 and c+1<=7and (self.board[r-1][c+1][0]=='b' or self.enPassantSquare==(r-1,c+1)):
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r - 1, c+1), self.board,isEnPassant=(self.enPassantSquare==(r-1,c+1))))

        if not self.whiteToMove:
            if r + 1 <= 7 and self.board[r + 1][c] == '--':
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r+2][c] == '--':
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if r+1 <= 7 and c-1>=0 and (self.board[r+1][c-1][0]=='w' or self.enPassantSquare==(r+1,c-1)):
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r + 1, c-1), self.board,isEnPassant=(self.enPassantSquare==(r+1,c-1))))
            if r+1 <=7 and c+1<=7 and (self.board[r+1][c+1][0]=='w' or self.enPassantSquare==(r+1,c+1)):
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r + 1, c+1), self.board,isEnPassant=(self.enPassantSquare==(r+1,c+1))))

    def getAllRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pinned)-1, -1, -1):
            curPin = self.pinned[i]
            if r == curPin[0] and c == curPin[1]:
                piecePinned = True
                pinDirection = (curPin[2], curPin[3])
                self.pinned.remove(curPin)
                break

        dir = [(-1,0),(1,0),(0,1),(0,-1)]
        enemyColor = 'b' if self.whiteToMove else 'w'

        for i in range(4):
            x = r + dir[i][0]
            y = c + dir[i][1]

            while 0<=x<=7 and 0<=y<=7:
                if not piecePinned or dir[i] == pinDirection or (-1 * dir[i][0], -1 * dir[i][1]) == pinDirection:
                    if self.board[x][y]=='--':
                        moves.append(Move((r,c),(x,y),self.board))
                    elif self.board[x][y][0]==enemyColor:
                        moves.append(Move((r, c), (x, y), self.board))
                        break
                    else:
                        break
                x = x + dir[i][0]
                y = y + dir[i][1]


    def getAllQueenMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pinned)-1, -1, -1):
            curPin = self.pinned[i]
            if r == curPin[0] and c == curPin[1]:
                piecePinned = True
                pinDirection = (curPin[2], curPin[3])
                self.pinned.remove(curPin)
                break


        dir = [(-1, 0), (1, 0), (0, 1), (0, -1),(1,1),(1,-1),(-1,-1),(-1,1)]
        enemyColor = 'b' if self.whiteToMove else 'w'

        for i in range(len(dir)):
            x = r + dir[i][0]
            y = c + dir[i][1]

            while 0 <= x <= 7 and 0 <= y <= 7:
                if not piecePinned or dir[i] == pinDirection or (-1 * dir[i][0], -1 * dir[i][1]) == pinDirection:
                    if self.board[x][y] == '--':
                        moves.append(Move((r, c), (x, y), self.board))
                    elif self.board[x][y][0] == enemyColor:
                        moves.append(Move((r, c), (x, y), self.board))
                        break
                    else:
                        break
                x = x + dir[i][0]
                y = y + dir[i][1]

    def getAllBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pinned)-1, -1, -1):
            curPin = self.pinned[i]
            if r == curPin[0] and c == curPin[1]:
                piecePinned = True
                pinDirection = (curPin[2], curPin[3])
                self.pinned.remove(curPin)
                break

        dir = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        enemyColor = 'b' if self.whiteToMove else 'w'

        for i in range(len(dir)):
            x = r + dir[i][0]
            y = c + dir[i][1]

            while 0 <= x <= 7 and 0 <= y <= 7:
                if not piecePinned or dir[i] == pinDirection or (-1 * dir[i][0], -1 * dir[i][1]) == pinDirection:
                    if self.board[x][y] == '--':
                        moves.append(Move((r, c), (x, y), self.board))
                    elif self.board[x][y][0] == enemyColor:
                        moves.append(Move((r, c), (x, y), self.board))
                        break
                    else:
                        break
                x = x + dir[i][0]
                y = y + dir[i][1]

    def getAllKnightMoves(self, r, c, moves):
        piecePinned = False

        for i in range(len(self.pinned)-1, -1, -1):
            curPin = self.pinned[i]
            if r == curPin[0] and c == curPin[1]:
                piecePinned = True
                self.pinned.remove(curPin)
                break

        dir = [(2,1),(2,-1),(1,2),(-1,2),(-2,1),(-2,-1),(1,-2),(-1,-2)]
        enemyColor = 'b' if self.whiteToMove else 'w'

        for i in range(len(dir)):
            x = r + dir[i][0]
            y = c + dir[i][1]
            if 0<=x<=7 and 0<=y<=7 and (self.board[x][y]=='--' or self.board[x][y][0]==enemyColor) :
                if not piecePinned:
                    moves.append(Move((r, c), (x, y), self.board))


    # castling pending
    def getAllKingMoves(self, r, c, moves):
        dir = [(-1, 0), (1, 0), (0, 1), (0, -1),(1,1),(1,-1),(-1,-1),(-1,1)]
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(len(dir)):
            x = r + dir[i][0]
            y = c + dir[i][1]
            if 0 <= x <= 7 and 0 <= y <= 7 :
                endPiece = self.board[x][y]

                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (x,y)
                    else:
                        self.blackKingLocation = (x,y)

                    inCheck,pins,checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(x,y),self.board))

                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)

        self.getKingSideCastleMoves(r, c, moves)
        self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self,r,c,moves):
        if self.isCheck:
            return
        elif (self.castlingState["wks"] and self.whiteToMove) or (self.castlingState["bks"] and not self.whiteToMove):
            if (self.board[r][c+1]=='--' and self.board[r][c+2]=='--')and not self.checkSquareUnderAttack(r,c+1) and not self.checkSquareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastle=True))

    def getQueenSideCastleMoves(self,r,c,moves):
        if self.isCheck:
            return
        elif (self.castlingState["wks"] and self.whiteToMove) or (self.castlingState["bks"] and not self.whiteToMove):
            if (self.board[r][c-1]=='--' and self.board[r][c-2]=='--' and self.board[r][c-3]=='--') and not self.checkSquareUnderAttack(r,c-1) and not self.checkSquareUnderAttack(r,c-2) and not self.checkSquareUnderAttack(r,c-3):
                moves.append(Move((r,c),(r,c-2),self.board,isCastle=True))


class Move:
    rowToRank = {0: 8, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1}
    rankToRow = {val: key for key, val in rowToRank.items()}
    colToRank = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    rankToCol = {val: key for key, val in colToRank.items()}

    def __eq__(self, other):
        if isinstance(other,
                      Move) and other.startR == self.startR and other.startC == self.startC and other.endC == self.endC and other.endR == self.endR:
            return True
        return False

    def __init__(self, start, end, board,isEnPassant = False, isCastle=False):
        self.startR = start[0]
        self.startC = start[1]
        self.endR = end[0]
        self.endC = end[1]
        self.pieceMoved = board[self.startR][self.startC]
        self.pieceCaptured = board[self.endR][self.endC]
        self.isPawnPromotion = self.pieceMoved[1]=='P' and ((self.pieceMoved[0] == 'b' and self.endR==7) or (self.pieceMoved[0] == 'w' and self.endR==0))
        self.isEnPassant = isEnPassant
        if isEnPassant:
            self.pieceCaptured = 'wP' if self.pieceMoved[0] == 'b' else "bP"

        self.isCastle = isCastle

    def getChessNotation(self):
        return str(self.colToRank[self.startC]) + str(self.rowToRank[self.startR]) + " " + str(
            self.colToRank[self.endC]) + \
            str(self.rowToRank[self.endR])
