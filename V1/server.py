import socket
import threading
import chess
import chess.engine

from protocol import encode_move


class ChessServer:
    def __init__(self, host, port):
        self.host = host  # set the host
        self.port = port  # set the port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")  # create a chess engine instance (stockfish)

    def handle_client(self, client_socket, client_color):
        try:
            board = chess.Board()
            if client_color == "white":
                print("Waiting for client's move...")  # wait for the client's first move if they are playing white
            else:
                result = self.engine.play(board, chess.engine.Limit(time=0.5))  # get the engine's first move if the client is playing black
                server_move = result.move
                board.push(server_move)
                print("Server's first move:", server_move)
                print(board)
                client_socket.send(encode_move(server_move).encode())  # send the engine's move to the client

            while True:
                data = client_socket.recv(1024)  # receive data from the client
                if not data:
                    print("Client disconnected.")
                    break
                move_str = data.decode()
                print("Received move:", move_str)
                if move_str.lower() == "resign":
                    print("Client resigned. Game over.")
                    client_socket.send("resign".encode())  # send a resign message to the client
                    break
                move = chess.Move.from_uci(move_str)  # convert the received move string to a chess.Move object
                if move and board.piece_at(move.from_square) and board.piece_at(move.from_square).color == (
                        chess.WHITE if client_color == "white" else chess.BLACK):
                    board.push(move)
                    print("Client's move:", move)
                    print(board)
                    if board.is_checkmate(): # if user is checkmating u
                        print("Checkmate! Game over.")
                        client_socket.send("checkmate".encode())
                        break
                    result = self.engine.play(board, chess.engine.Limit(time=0.1))  # get the engine's move
                    server_move = result.move
                    board.push(server_move)
                    print("Server's move:", server_move)
                    print(board)
                    if board.is_checkmate(): # if server checkmates user
                        print("Checkmate! Game over.")
                        client_socket.send(encode_move(server_move).encode())
                        client_socket.send("checkmate".encode())  # send a checkmate message to the client
                        break
                    client_socket.send(encode_move(server_move).encode())  # send the engine's move to the client
                else:
                    print("Invalid move from client.")
                    client_socket.send("Invalid".encode())  # send an invalid move message to the client
        except Exception as e:
            print("Exception occurred:", e)
        finally:
            client_socket.close()  # close the client socket

    def start(self):
        self.server_socket.bind((self.host, self.port))  # bind the server socket to the specified host and port
        self.server_socket.listen(5)  # start listening for incoming connections
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                client_socket, _ = self.server_socket.accept()  # accept a client connection
                client_response = client_socket.recv(1024).decode().lower()  # receive the client's color choice
                if client_response not in ["white", "black"]:
                    client_socket.send("Invalid color choice.".encode())  # send an error message if the color choice is invalid
                    client_socket.close()  # close the client socket
                else:
                    client_socket.send("Accepted".encode())  # send an acceptance message to the client
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_response))  # create a new thread for handling the client
                    client_thread.start()  # start the client thread
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server_socket.close()  # close the server socket


if __name__ == "__main__":
    server = ChessServer('localhost', 5555)  # create a new ChessServer instance
    server.start()  # start the server
