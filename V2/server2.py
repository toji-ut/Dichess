import socket
import threading
import chess
import chess.engine

from protocol2 import encode_move


class ChessServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")

    def handle_client(self, client_socket, client_color):
        try:
            board = chess.Board()
            if client_color == "white":
                print("Waiting for client's move...")
            else:
                result = self.engine.play(board, chess.engine.Limit(time=0.5))
                server_move = result.move
                board.push(server_move)
                print("Server's first move:", server_move)
                print(board)
                client_socket.send(encode_move(server_move).encode())

            while True:
                data = client_socket.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break
                move_str = data.decode()
                print("Received move:", move_str)
                if move_str.lower() == "resign":
                    print("Client resigned. Game over.")
                    client_socket.send("resign".encode())
                    break
                move = chess.Move.from_uci(move_str)
                if move and board.piece_at(move.from_square) and board.piece_at(move.from_square).color == (
                        chess.WHITE if client_color == "white" else chess.BLACK):
                    board.push(move)
                    print("Client's move:", move)
                    print(board)
                    if board.is_checkmate():
                        print("Checkmate! Game over.")
                        client_socket.send("checkmate".encode())
                        break
                    result = self.engine.play(board, chess.engine.Limit(time=0.1))
                    server_move = result.move
                    board.push(server_move)
                    print("Server's move:", server_move)
                    print(board)
                    if board.is_checkmate():
                        print("Checkmate! Game over.")
                        client_socket.send(encode_move(server_move).encode())
                        client_socket.send("checkmate".encode())
                        break
                    client_socket.send(encode_move(server_move).encode())
                else:
                    print("Invalid move from client.")
                    client_socket.send("Invalid".encode())
        except Exception as e:
            print("Exception occurred:", e)
        finally:
            client_socket.close()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                client_socket, _ = self.server_socket.accept()
                client_socket.send("Ready".encode())
                client_response = client_socket.recv(1024).decode().lower()
                if client_response not in ["bot", "human"]:
                    client_socket.send("Invalid opponent choice.".encode())
                    client_socket.close()
                else:
                    client_socket.send("Accepted".encode())
                    client_color_response = client_socket.recv(1024).decode().lower()
                    if client_color_response not in ["white", "black"]:
                        client_socket.send("Invalid color choice.".encode())
                        client_socket.close()
                    else:
                        client_socket.send("Accepted".encode())
                        client_thread = threading.Thread(target=self.handle_client, args=(
                            client_socket, client_color_response))
                        client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = ChessServer('localhost', 5555)
    server.start()
