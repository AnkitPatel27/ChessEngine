# responsible for input and output stuff

import pygame as p
import ChessEngine
import sound_effects as se
import MoveFinder
import random
import timeit
import pygame_menu

# BOARD DIMENSIONS
DIMENSION = 8
TEXTWIDTH = 180
BOARDWIDTH = HEIGHT = 512
WIDTH = TEXTWIDTH+BOARDWIDTH
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# PLAYER TYPE
player1 = True  #white to move and True if the human player
player2 = True  #black to move and True if the human player

# getting all the piece images at once
def loadImages():
    pieces = ['wP','wR','wN','wQ','wK','wB','bP','bR','bN','bQ','bK','bB']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('./Images/' + piece + '.png'),(SQ_SIZE,SQ_SIZE))


def show_menu(screen):
    global player1, player2

    menu = pygame_menu.Menu('Chess Game', WIDTH, HEIGHT,
                            theme=pygame_menu.themes.THEME_DARK)

    menu.add.selector('White Player :', [('Human', True), ('AI', False)], onchange=set_player1)
    menu.add.selector('Black Player :', [('Human', True), ('AI', False)], onchange=set_player2)
    menu.add.button('Play', menu.disable)
    menu.mainloop(screen, disable_loop=False)
def set_player1(_, value):
    global player1
    player1 = value
def set_player2(_, value):
    global player2
    player2 = value

def main():
    global BOARDWIDTH, HEIGHT, SQ_SIZE,DIMENSION,WIDTH
    # pygame setup
    p.init()
    loadImages()
    gs = ChessEngine.GameState()
    screen = p.display.set_mode((WIDTH,HEIGHT),p.RESIZABLE)
    clock = p.time.Clock()
    running = True

    # getting moves
    allValidMoves = gs.getAllValidMoves()
    madeMove = False  #to get valid moves again when the move is made
    animate = False
    # storing last two moves
    lastMove = ()
    last2Moves = []
    gameOver = False

    show_menu(screen)


    while running:

        # pygame.QUIT event means the user clicked X to close your window # poll for events
        for event in p.event.get():
            humanTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
            if event.type == p.QUIT:
                running = False
            elif event.type == p.VIDEORESIZE:
                # Window has been resized
                BOARDWIDTH = HEIGHT = min(event.w-TEXTWIDTH, event.h)
                BOARDWIDTH = HEIGHT = (BOARDWIDTH // 8) * 8  # Ensure it's divisible by 8
                SQ_SIZE = HEIGHT // DIMENSION
                screen = p.display.set_mode((BOARDWIDTH+TEXTWIDTH, HEIGHT), p.RESIZABLE)
                loadImages()
            elif not gameOver and humanTurn and event.type == p.MOUSEBUTTONUP:
                pos = p.mouse.get_pos()
                row = pos[1]//SQ_SIZE
                col = pos[0]//SQ_SIZE


                if not (0<=row<=7) or not (0<=col<=7):
                    pass
                elif lastMove == () and gs.board[row][col]=='--':# getting two last clicks to make a move
                    pass
                elif lastMove == ():
                    lastMove = (row,col)
                    last2Moves.append((row,col))
                elif lastMove == (row,col):
                    lastMove = ()
                    last2Moves = []
                else:
                    lastMove = (row,col)
                    last2Moves.append((row,col))

                if len(last2Moves) == 2:
                    #make a valid move
                    move = ChessEngine.Move(last2Moves[0],last2Moves[1],gs.board)
                    for i in range(len(allValidMoves)):
                        if move == allValidMoves[i]:
                            gs.makeMove(allValidMoves[i])
                            madeMove = True
                            animate = True
                            lastMove = ()
                            last2Moves = []
                    if not madeMove:
                        lastMove = last2Moves[1]
                        last2Moves = [lastMove]

            elif event.type == p.KEYDOWN and event.key==p.K_z:
                gs.undoMove()
                animate = False
                madeMove = True
                gameOver = False
            elif event.type == p.KEYDOWN and event.key==p.K_r:
                gs = ChessEngine.GameState()
                # getting moves
                allValidMoves = gs.getAllValidMoves()
                madeMove = False  # to get valid moves again when the move is made
                animate = False
                # storing last two moves
                lastMove = ()
                last2Moves = []
                gameOver = False

            if not gameOver and not humanTurn:
                AIMove = MoveFinder.findBestNMove(gs,allValidMoves)
                if AIMove is None:
                    if len(allValidMoves)==1:
                        AIMove = allValidMoves[0]
                    else:
                        AIMove = allValidMoves[random.randint(0, len(allValidMoves) - 1)]
                gs.makeMove(AIMove)
                madeMove = True
                # animate = True

            if madeMove:
                if animate:
                    animateMove(gs.moveLog[-1],screen,gs.board,clock,last2Moves)
                allValidMoves = gs.getAllValidMoves()
                madeMove = False
                animate = True


        # RENDER YOUR GAME HERE
        drawState(gs,screen,last2Moves,allValidMoves)

        # checkMate and StaleMate
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,"White loses checkMate")
            else:
                drawText(screen, "White loses checkMate")
        if gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")
        # flip() the display to put your work on screen
        p.display.flip()

        clock.tick(15)  # limits FPS to 60

    p.quit()

def drawText(screen,message):
    font = p.font.SysFont("Arial",32,True,False)
    textObj = font.render(message,0,p.Color('black'))
    textLoc = p.Rect(0,0,BOARDWIDTH,HEIGHT).move(BOARDWIDTH/2-textObj.get_width()/2,HEIGHT/2-textObj.get_height()/2)
    screen.blit(textObj,textLoc)

def drawSideText(moveLog,screen):
    p.draw.rect(screen, p.Color((0,0,0)), p.Rect(BOARDWIDTH, 0,TEXTWIDTH, HEIGHT))
    font = p.font.SysFont("Arial", 12, True, False)
    message = "\nUNDO : press(z) \n\n PawnPromo: press(Q,N,B,R)\n (Q): Queen \n (N): Knight \n (B): Bishop \n (R): Rook \n\n\n"
    logMessage = "Last Ten Moves : \n"
    if len(moveLog)==0:
      logMessage += "No Moves Made!!\n"
    else:
        for i in range(len(moveLog) - 1, max(-1,len(moveLog)-10), -1):
            logMessage+=str(i+1)+"] "+moveLog[i].getChessNotation()+"\n"
    text_surf = font.render(
        message+logMessage,
        True,
        "white",
        wraplength=140,
    )


    screen.blit(text_surf, (BOARDWIDTH+10,0))


def drawState(gs,screen,last2Moves,ValidMoves):
    drawBoard(screen,last2Moves)
    highlightSquare(gs,screen,last2Moves,ValidMoves)
    drawPieces(screen,gs.board)
    drawSideText(gs.moveLog,screen)


def highlightSquare(gs,screen,last2Moves,ValidMoves):
    if len(last2Moves)>0 and last2Moves[0]!=():
        r,c = last2Moves[0]
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill('purple')
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight the square that are valid to move the selected piece

            s.fill('yellow')
            for move in ValidMoves:
                if move.startR == r and move.startC==c:
                    screen.blit(s,(move.endC*SQ_SIZE,move.endR*SQ_SIZE))

def animateMove(move,screen,board,clock,last2Moves):
    global colors
    dR = move.endR-move.startR
    dC = move.endC-move.startC
    framePerSqaure = 10
    if abs(dR)+abs(dC) > 4:
        framePerSqaure = 3
    frameCount = (abs(dR)+abs(dC))*framePerSqaure
    # print(frameCount)
    for frame in range(frameCount+1):
        r,c = (move.startR + dR*frame/frameCount,move.startC + dC*frame/frameCount)
        drawBoard(screen,last2Moves)
        drawPieces(screen,board)
        # erase the pieces moved from its ending square
        color = colors[(move.endR+move.endC)%2]
        endSquare = p.Rect(move.endC*SQ_SIZE,move.endR*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured],endSquare)

        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)
    se.moveMade.play()

def drawBoard(screen,last2Moves):
    global colors
    x=-1
    y=-1
    if len(last2Moves)>0:
        x = last2Moves[0][0]
        y = last2Moves[0][1]

    colors = [p.Color((255, 206, 158)),p.Color((209, 139, 71)),p.Color((181, 146, 112)),p.Color((255,170,87))]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if board[r][c] != "--":
                screen.blit(IMAGES[board[r][c]],(c*SQ_SIZE,r*SQ_SIZE))



if __name__=="__main__":
    main()
