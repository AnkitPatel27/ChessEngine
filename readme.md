## Chess Engine
Implemented a chess game using pygame and also implemented Negamax and Alpha beta pruning for minMax algorithm for computer to make moves

## Can Do 
Apply reinforcement learning over the game for AI to learn itself 

## to build the exe
python <pathToPyInstaller or PyInstaller>  --onefile --windowed --add-data "Images;." --add-data "Sounds;." --add-data "sound_effects.py;." --add-data "__init__.py;." --add-data "ChessEngine.py;." --add-data "MoveFinder.py;." --hidden-import pygame --hidden-import pygame_menu ChessMain.py