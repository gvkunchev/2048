"""2048 CLI game for Windows."""


import msvcrt
import os
import random


class GameOverException(Exception):
    """Game over exception."""
    pass


class GameFinishedException(Exception):
    """Game finished exception."""
    pass


class Square:
    """2048 grid square."""

    def __init__(self, value=None):
        """Initializator."""
        self.value = value


class Grid:
    """2048 grid."""

    GOAL = 2048

    def __init__(self, width, height):
        """initializator."""
        self._width = width
        self._height = height
        self.squares = []
        self._init_squares()
        self._new_square()
        self._new_square()

    def _init_squares(self):
        """initializa the sqares in the grid."""
        for x in range(self._width):
            self.squares.append([])
            for y in range(self._height):
                self.squares[-1].append(Square())

    def _get_empty_squares(self):
        """Get list of empty squares."""
        for x in self.squares:
            for y in x:
                if y.value is None:
                    yield y

    def _new_square(self):
        """Put random square in the grid."""
        empty_squares = list(self._get_empty_squares())
        if not len(empty_squares):
            raise GameOverException('No empty squares left.')
        random_square = random.choice(empty_squares)
        # TODO: Some fraction of the new squares should be 4s not 2s
        random_square.value = 2

    def _shift(self, squares):
        """Shift squares already ordered in the right direction."""
        first_empty_spot = None
        last_filled_spot = None
        merged = False
        finished = False
        made_move = False
        for i, spot in enumerate(squares):
            if spot.value is None:
                # Keep a record for the first empty spot
                if first_empty_spot is None:
                    first_empty_spot = i
                continue
            # Being here means the current square has value - try to merge it
            if last_filled_spot and last_filled_spot.value == spot.value:
                # Only allow merging once per move
                if merged:
                    continue
                # Merge the two spots
                last_filled_spot.value += spot.value
                if last_filled_spot.value == self.GOAL:
                    finished = True
                spot.value = None
                merged = True
                made_move = True
                # Update first empty spot to the one that was just created after the merge
                if first_empty_spot is None:
                    first_empty_spot = i
            # No merge available, but there is an empty spot where the current tile can move to
            elif first_empty_spot is not None:
                squares[first_empty_spot].value = spot.value
                last_filled_spot = squares[first_empty_spot]
                spot.value = None
                first_empty_spot += 1
                made_move = True
            else:
                # Keep a record of the last spot available for merging
                last_filled_spot = spot
        return made_move, finished
    
    def _get_columns(self):
        """Get squares as columns as opposed to rows."""
        columns = [[] for _ in self.squares]
        for row in self.squares:
            for i, spot in enumerate(row):
                columns[i].append(spot)
        return columns
    
    def _move(self, squares):
        """Make a move and determine if finished or not."""
        finished = False
        made_move = False
        for line in squares:
            made_move_, finished_ = self._shift(line)
            finished = finished_ or finished
            made_move = made_move_ or made_move
        if finished:
            raise GameFinishedException('Congrats!')
        elif made_move:
            self._new_square()

    def left(self):
        """Shift grid to left."""
        self._move(self.squares)

    def right(self):
        """Shift grid to right."""
        self._move(map(lambda x: x[::-1], self.squares))

    def top(self):
        """Shift grid to top."""
        self._move(self._get_columns())

    def bottom(self):
        """Shift grid to bottom."""
        self._move(map(lambda x: x[::-1], self._get_columns()))


class View:
    """2048 game view."""

    CHAR_MAP = {
        'q': 'quit',
        'a': 'left',
        'd': 'right',
        'w': 'top',
        's': 'bottom',
    }

    SQUARE_SIZE = 6

    COLORS = {
        None: '\u001b[40m%s\u001b[0m',
        2: '\u001b[41m%s\u001b[0m',
        4: '\u001b[42m%s\u001b[0m',
        8: '\u001b[43m%s\u001b[0m',
        16: '\u001b[44m%s\u001b[0m',
        32: '\u001b[45m%s\u001b[0m',
        64: '\u001b[46m%s\u001b[0m',
        128: '\u001b[41m%s\u001b[0m',
        256: '\u001b[42m%s\u001b[0m',
        512: '\u001b[43m%s\u001b[0m',
        1024: '\u001b[44m%s\u001b[0m',
        2048: '\u001b[45m%s\u001b[0m'
    }

    def __init__(self):
        """Initializator."""
        pass

    def _show_keys(self):
        """Show keys for controlling the game."""
        for key, value in self.CHAR_MAP.items():
            print(f"{key}: {value}")
        print('\n\n')

    def _clear(self):
        """Clear screen."""
        os.system('cls')
        self._show_keys()

    def parse(self, grid):
        """Parse grid to the screen."""
        self._clear()
        grid_length = (len(grid.squares) * self.SQUARE_SIZE) + len(grid.squares)
        for x in grid.squares:
            print('-' * grid_length)
            for y in x:
                print('|', end='')
                if y.value:
                    white_space_len = self.SQUARE_SIZE - len(str(y.value))
                    white_space_before = white_space_len // 2
                    white_space_after = white_space_len - white_space_len // 2
                    value_to_write = ' ' * white_space_before
                    value_to_write += str(y.value)
                    value_to_write += ' ' * white_space_after
                else:
                    value_to_write = " " * self.SQUARE_SIZE
                print(self.COLORS[y.value] % value_to_write, end='')
            print('|')
            print('-' * grid_length)

    def get_input(self):
        """Get user input."""
        input_char = None
        while input_char not in self.CHAR_MAP:
            try:
                input_char = msvcrt.getch().decode("utf-8").lower()
            except UnicodeDecodeError:
                pass # Invalid key
        return self.CHAR_MAP[input_char]


class Game:
    """2048 game."""

    GRID_WIDTH = GRID_HEIGHT = 4

    def __init__(self):
        """Initializator."""
        self._grid = Grid(self.GRID_WIDTH, self.GRID_HEIGHT)
        self._view = View()
        self._main_loop()

    def _main_loop(self):
        """Main game loop."""
        while True:
            self._view.parse(self._grid)
            action = self._view.get_input()
            if action == 'quit':
                break
            else:
                try:
                    getattr(self._grid, action)()
                except GameOverException:
                    print('Game over.')
                    break
                except GameFinishedException:
                    self._view.parse(self._grid)
                    print('Congrats.')
                    break


if __name__ == "__main__":
    game = Game()