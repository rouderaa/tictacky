import threading
import queue
import socket
import selectors

from message import Message
from game import Game

HOST, PORT = "localhost", 9080

class Server(threading.Thread):
    def __init__(self, qin):
        threading.Thread.__init__(self)
        self.q = qin
        self.client_socket = None

    def handle_socket_input(self, s):
        done = False
        try:
            data = s.recv(1024)
        except Exception as e:
            print(e)
            done = True
            data = ''
        if len(data) == 0:
            # connection got closed
            done = True
        else:
            # got request from client
            data = data.strip()
            if len(data) >= 1:
                # set data in the queue to worker thread
                self.q.put(Message(self.client_socket, data))
        return done

    def run(self) -> None:
        # Create a socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        # Lists to keep track of sockets and queues
        input_sockets = [server_socket] # socket from godot client

        # Create a selector object
        selector = selectors.DefaultSelector()
        selector.register(server_socket, selectors.EVENT_READ)

        done = False
        while not done:
            try:
                # Wait for events on socket
                events = selector.select()

                for key, mask in events:
                    if key.fileobj == server_socket:
                        # Accept new connection
                        self.client_socket, address = server_socket.accept()
                        selector.register(self.client_socket, selectors.EVENT_READ)
                    else:
                        # Handle input from connected socket
                        self.client_socket = key.fileobj
                        self.handle_socket_input(self.client_socket)
            except Exception as e:
                print(e)

class Worker(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.game = Game(q)
        self.q = q

    def run(self) -> None:
        while True:
            self.game.play()

            # wait for any message to play again
            message = self.q.get()
            print(f'Game got data: {message.data}')
            self.game.initialize_game()

if __name__ == "__main__":
    q = queue.Queue()

    # start two threads, one queue in between
    server_thread = Server(q)
    model_thread = Worker(q)

    server_thread.start()
    model_thread.start()

    # wait for all threads to finish
    server_thread.join()
    model_thread.join()

    print("Done")
