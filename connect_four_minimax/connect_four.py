import random
from connect_four_tree import ConnectFourTree

class Board:
    def __init__(self):
        self._grid = []
        self._width = 7
        self._height = 6
        for i in range(self._height):
            self._grid.append([])
            for _ in range(self._width):
                self._grid[i].append(None)
    
    def view(self) -> tuple[tuple[str]]:
        return tuple(tuple(row) for row in self._grid)
    
    def show(self):
        print('0 1 2 3 4 5 6')
        for row in self._grid:
            print(' '.join('.' if cell is None else str(cell) for cell in row))
        print()
    
    def is_valid_move(self, col: int) -> bool:
        if col is None:
            return None
        return self._grid[0][col] == None
    
    def move(self, col: int, symbol: str) -> bool:
        if self.is_valid_move(col):
            i = self._height - 1
            while i >= 0:
                if self._grid[i][col] == None:
                    self._grid[i][col] = symbol
                    return True
                i -= 1
        return False
    
    def is_filled(self) -> bool:
        for c in range(self._width):
            if self.is_valid_move(c):
                return False
        return True
    
    def get_winner(self) -> str:
        for row in self._grid:
            run = 1
            last = row[0]
            for n in row[1:]:
                if n and n == last:
                    run += 1
                    if run >= 4:
                        return n
                else:
                    run = 1
                last = n
        for i in range(self._width):
            run = 1
            last = self._grid[0][i]
            j = 1
            while j < self._height:
                n = self._grid[j][i]
                if n and n == last:
                    run += 1
                    if run >= 4:
                        return n
                else:
                    run = 1
                last = n
                j += 1

        for r in range(self._height):
            for c in range(self._width - 3):
                symbol = self._grid[r][c]
                if not symbol:
                    continue

                if r <= self._height - 4:
                    # down diagonal
                    win = True
                    for i in range(4):
                        if self._grid[r + i][c + i] != symbol:
                            win = False
                            break
                    if win:
                        return symbol
                if r >= 3:
                    # up diagonal
                    win = True
                    for i in range(4):
                        if self._grid[r - i][c + i] != symbol:
                            win = False
                            break
                    if win:
                        return symbol
        return None
    
class Game:
    def __init__(self, p1, p2):
        self._board = Board()
        self._p1 = p1
        self._p2 = p2
    
    def run(self, log: bool = False):
        p1_turn = True

        while True:
            if log:
                self._board.show()
            
            valid_move = False
            while not valid_move:
                if p1_turn:
                    move = self._p1.choose_move(self._board.view())
                    symbol = 'X'
                else:
                    move = self._p2.choose_move(self._board.view())
                    symbol = 'O'

                if self._board.move(move, symbol):
                    if log:
                        print(f'{symbol} move: {move}')
                    valid_move = True
                    p1_turn = not p1_turn
                elif log:
                    print(f'Invalid move {move} by {symbol}. Try again.')
            
            if self._board.get_winner() or self._board.is_filled():
                break

        self._board.show()
        winner = self._board.get_winner()
        if winner:
            print(f'{winner} wins')
        else:
            print('tie game')
        return winner

class Player:
    def __init__(self, strategy_function):
        self._strategy_function = strategy_function

    def choose_move(self, board: tuple[tuple[str]]):
        return self._strategy_function(board)
    
def random_strategy_function(board: tuple[tuple[str]]):
    return random.randint(0, 6)

def manual_strategy_function(board: tuple[tuple[str]]):
    while True:
        user_input = input('Input move (0-6): ')
        try:
            try_position = int(user_input)
        except ValueError:
            print('Invalid input. Must be an integer. Try again.')
            continue
        if not 0 <= try_position <= 6:
            print('Invalid input. Must be between 0-6. Try again.')
            continue
        return try_position
    
class MinimaxPlayer:
    def __init__(self, perspective: int, n_ply: int):
        self._tree = ConnectFourTree(perspective, n_ply)

    def choose_move(self, board: tuple[tuple[str]]):
        tree = self._tree
        tree.update_tree(board)
        choices = tree.get_children(tree.root)
        if not choices:
            return
        max = choices[0].minimax
        best_choices = [choices[0]]
        for c in choices:
            if c.minimax > max:
                max = c.minimax
                best_choices.clear()
                best_choices.append(c)
            elif c.minimax == max:
                best_choices.append(c)
        move = best_choices[random.randint(0, len(best_choices) - 1)]
        return tree.get_move_change(board, move.state)

# TESTING MINIMAX VS RANDOM

# wins = 0
# for i in range(500):
#     g = Game(MinimaxPlayer(0, 8), Player(random_strategy_function))
#     winner = g.run(False)
#     if winner == 'X':
#         wins += 1

# print(wins)

g = Game(Player(manual_strategy_function), MinimaxPlayer(1, 8))
g.run(True)