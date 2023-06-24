# url: https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python/

# game tree in every move. It's a nice way to show the
# distinction between the basic Minimax and Minimax with
# alpha-beta pruning :)
import time
import json

class Game:
    def __init__(self, q):
        self.initialize_game()
        self.q = q
        self.reply_socket = None

    def initialize_game(self):
        self.current_state = [['.','.','.'],
                              ['.','.','.'],
                              ['.','.','.']]

        # Player X always plays first
        self.player_turn = 'X'

    def get_board(self):
        return self.current_state

    def send_message(self, message):
        _dict = {'M': message}
        _json_dict = json.dumps(_dict)
        reply = _json_dict.encode("utf-8")
        if self.reply_socket is not None:
            self.reply_socket.send(reply)

    def draw_board(self):
        for i in range(0, 3):
            for j in range(0, 3):
                print('{}|'.format(self.current_state[i][j]), end=" ")
            print()
        print()

        # send latest board directly to client socket
        _board = self.get_board()
        _dict = {'U': _board}
        _json_dict = json.dumps(_dict)
        reply = _json_dict.encode("utf-8")
        if self.reply_socket is not None:
            self.reply_socket.send(reply)

    # Determines if the made move is a legal move
    def is_valid(self, px, py):
        if px < 0 or px > 2 or py < 0 or py > 2:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    # Checks if the game has ended and returns the winner in each case
    def is_end(self):
        # Vertical win
        for i in range(0, 3):
            if (self.current_state[0][i] != '.' and
                    self.current_state[0][i] == self.current_state[1][i] and
                    self.current_state[1][i] == self.current_state[2][i]):
                return self.current_state[0][i]

        # Horizontal win
        for i in range(0, 3):
            if (self.current_state[i] == ['X', 'X', 'X']):
                return 'X'
            elif (self.current_state[i] == ['O', 'O', 'O']):
                return 'O'

        # Main diagonal win
        if (self.current_state[0][0] != '.' and
                self.current_state[0][0] == self.current_state[1][1] and
                self.current_state[0][0] == self.current_state[2][2]):
            return self.current_state[0][0]

        # Second diagonal win
        if (self.current_state[0][2] != '.' and
                self.current_state[0][2] == self.current_state[1][1] and
                self.current_state[0][2] == self.current_state[2][0]):
            return self.current_state[0][2]

        # Is whole board full?
        for i in range(0, 3):
            for j in range(0, 3):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None

        # It's a tie!
        return '.'

    # Player 'O' is max, in this case AI
    def max(self):

        # Possible values for maxv are:
        # -1 - loss
        # 0  - a tie
        # 1  - win

        # We're initially setting it to -2 as worse than the worst case:
        maxv = -2

        px = None
        py = None

        result = self.is_end()

        # If the game came to an end, the function needs to return
        # the evaluation function of the end. That can be:
        # -1 - loss
        # 0  - a tie
        # 1  - win
        if result == 'X':
            return (-1, 0, 0)
        elif result == 'O':
            return (1, 0, 0)
        elif result == '.':
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    # On the empty field player 'O' makes a move and calls Min
                    # That's one branch of the game tree.
                    self.current_state[i][j] = 'O'
                    (m, min_i, min_j) = self.min()
                    # Fixing the maxv value if needed
                    if m > maxv:
                        maxv = m
                        px = i
                        py = j
                    # Setting back the field to empty
                    self.current_state[i][j] = '.'
        return (maxv, px, py)

    # Player 'X' is min, in this case human
    def min(self):

        # Possible values for minv are:
        # -1 - win
        # 0  - a tie
        # 1  - loss

        # We're initially setting it to 2 as worse than the worst case:
        minv = 2

        qx = None
        qy = None

        result = self.is_end()

        if result == 'X':
            return (-1, 0, 0)
        elif result == 'O':
            return (1, 0, 0)
        elif result == '.':
            return (0, 0, 0)

        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    self.current_state[i][j] = 'X'
                    (m, max_i, max_j) = self.max()
                    if m < minv:
                        minv = m
                        qx = i
                        qy = j
                    self.current_state[i][j] = '.'

        return (minv, qx, qy)

    def play(self):
        while True:
            self.draw_board()
            self.result = self.is_end()

            # Printing the appropriate message if the game has ended
            if self.result is not None:
                if self.result == 'X':
                    message = 'The winner is X!'
                elif self.result == 'O':
                    message = 'The winner is O!'
                elif self.result == '.':
                    message = "It's a tie!"

                print(message)
                self.send_message(message)
                self.draw_board()

#                self.initialize_game()
                return

            # If it's player's turn
            if self.player_turn == 'X':

                while True:

                    start = time.time()
                    (m, qx, qy) = self.min()
                    end = time.time()
                    print('Evaluation time: {}s'.format(round(end - start, 7)))
                    print('Recommended move: X = {}, Y = {}'.format(qx, qy))

                    # wait for next message with move of player
                    message = self.q.get()
                    self.reply_socket = message.reply_socket

                    print(f'Game got data: {message.data}')
                    js = json.loads(message.data)
                    # signal done with data from queue
                    self.q.task_done()

                    if js['cmd']=='S':
                        # make coordinates valid
                        px = int(js['x'])
                        py = int(js['y'])
                    else:
                        if js['cmd']=='R':
                            px = -1
                            py = -1
                            self.initialize_game()
                            self.draw_board()
                        else:
                            # make coordinates invalid
                            px = -1
                            py = -1

                    (qx, qy) = (px, py)

                    if self.is_valid(px, py):
                        self.current_state[px][py] = 'X'
                        self.player_turn = 'O'
                        break
                    # else:
                    #     print('The move is not valid! Try again.')

            # If it's AI's turn
            else:
                (m, px, py) = self.max()
                self.current_state[px][py] = 'O'
                self.player_turn = 'X'
